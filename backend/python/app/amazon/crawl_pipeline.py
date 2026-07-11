"""Amazon 运营数据爬取主编排（V2 Pipeline）。"""
from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Any

from app.amazon.composer.metrics_merger import coalesce_ads_summary, merge_ads_metrics
from app.amazon.composer.product_composer import (
    allocate_account_ads_by_revenue,
    compose_product_rows,
    enrich_product_rows,
    merge_campaign_ads_into_products,
)
from app.amazon.crawlers.account import (
    cases_from_seller_news,
    crawl_account_health_metrics,
    parse_home_metrics,
    parse_home_news_and_cases,
)
from app.amazon.crawlers.business_report import crawl_business_report
from app.amazon.crawlers.campaign_manager import crawl_ads_data
from app.amazon.crawlers.daily_ops import crawl_cases, crawl_messages, crawl_operational_lists, crawl_reviews
from app.amazon.crawlers.inventory import (
    crawl_home_catalog,
    crawl_inventory_products,
    merge_catalog_sources,
)
from app.amazon.crawlers.orders_v3 import crawl_orders_v3
from app.amazon.diagnostics import CrawlDiagnostics, PageDiagnostic
from app.amazon.page_urls import HOME_URL
from app.amazon.parsers.seller_pages import EXTRACT_DEEP_BODY_TEXT_JS
from app.amazon.scope_planner import normalize_scope
from app.amazon.session_context import (
    AmazonLoginRequiredError,
    CAPTURE_DIR,
    SessionContext,
    extract_debug_port,
    looks_logged_in,
    require_seller_logged_in,
    save_capture,
)
from app.ziniao.client import ZiniaoClient, ZiniaoConfig

PRODUCT_SYNC_SCOPES = frozenset({"daily", "insights", "reports"})


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _annotate_product_sync(result: dict[str, Any], scope: str, catalog_count: int, br_count: int) -> None:
    if scope not in PRODUCT_SYNC_SCOPES:
        return
    products = result.get("products") or []
    if products:
        result["product_sync_warning"] = ""
        if br_count > 0 and catalog_count > 0 and br_count < max(3, int(catalog_count * 0.2)):
            result["product_sync_warning"] = "PARTIAL_BR"
        return
    result["product_sync_warning"] = "NO_ASIN_ROWS"


def _empty_result() -> dict[str, Any]:
    return {
        "synced_at": _now_text(),
        "metrics": [],
        "products": [],
        "outbound_orders": [],
        "buyer_messages": [],
        "reviews": [],
        "coupons": [],
        "seller_news": [],
        "shipments": [],
        "cases": [],
        "page_url": "",
        "capture_path": "",
        "merchant_id": "",
        "page_diagnostics": [],
        "result_summary": {},
    }


def _record(diagnostic: CrawlDiagnostics, key: str, url: str, rows: list, started: float, warning: str = "") -> None:
    diagnostic.add(
        PageDiagnostic(
            key=key,
            url=url,
            ok=bool(rows) and not warning,
            rows=len(rows) if isinstance(rows, list) else 0,
            duration_ms=int((time.time() - started) * 1000),
            warning=warning,
        )
    )


def run_crawl(
    *,
    scope: str = "account_health",
    browser_id: str = "",
    browser_oauth: str = "",
    store_name: str = "",
    merchant_id: str = "",
) -> dict[str, Any]:
    if not browser_id and not browser_oauth:
        raise ValueError("缺少 browser_id 或 browser_oauth")

    normalized_scope = normalize_scope(scope)
    ziniao = ZiniaoClient(ZiniaoConfig.from_env())
    ziniao.ensure_webdriver_client(wait_seconds=20)
    start_result = ziniao.start_browser(
        browser_id=browser_id or None,
        browser_oauth=browser_oauth or None,
    )
    debug_port = extract_debug_port(start_result)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("缺少 playwright，请执行 pip install -r backend/python/requirements.txt") from exc

    result = _empty_result()
    diagnostics = CrawlDiagnostics()

    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{debug_port}")
        try:
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.pages[0] if context.pages else context.new_page()
            page.set_default_timeout(90000)
            ctx = SessionContext(page, store_name=store_name, merchant_id=merchant_id)

            started = time.time()
            page.goto(HOME_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)
            try:
                home_text = page.evaluate(EXTRACT_DEEP_BODY_TEXT_JS) or page.inner_text("body")
            except Exception:
                home_text = page.inner_text("body")
            result["page_url"] = page.url
            require_seller_logged_in(page, home_text, store_name=store_name)
            ctx.ensure_merchant_id()
            _record(diagnostics, "home", HOME_URL, [{"ok": True}], started)

            if normalized_scope in {"account_health", "daily", "reports"}:
                result["metrics"] = parse_home_metrics(home_text)
                if normalized_scope in {"daily", "reports"}:
                    seller_news, cases = parse_home_news_and_cases(home_text)
                    if seller_news:
                        result["seller_news"] = seller_news
                    if cases:
                        result["cases"] = cases

            report_products: list[dict[str, Any]] = []
            inventory_products: list[dict[str, Any]] = []
            order_rows: list[dict[str, Any]] = []
            br_count = 0
            catalog_count = 0

            if normalized_scope in {"daily", "reports"}:
                started = time.time()
                home_products = crawl_home_catalog(page)
                _record(diagnostics, "home_catalog", HOME_URL, home_products, started)

                started = time.time()
                report_products = crawl_business_report(page, store_name=store_name)
                br_count = len(report_products)
                _record(
                    diagnostics,
                    "br_child_asin",
                    page.url,
                    report_products,
                    started,
                    "" if report_products else "ZERO_ROWS",
                )

                started = time.time()
                inventory_products = crawl_inventory_products(page, store_name=store_name)
                catalog_count = len(inventory_products)
                _record(
                    diagnostics,
                    "inventory_all",
                    page.url,
                    inventory_products,
                    started,
                    "" if inventory_products else "ZERO_ROWS",
                )

                inventory_products = merge_catalog_sources(
                    inventory_products,
                    home_products,
                    store_name=store_name,
                    page=page,
                )
                catalog_count = max(catalog_count, len(inventory_products))

                started = time.time()
                order_rows = crawl_orders_v3(page)
                if order_rows:
                    result["outbound_orders"] = order_rows
                _record(
                    diagnostics,
                    "orders_all",
                    "orders-v3/*",
                    order_rows,
                    started,
                    "" if order_rows else "ZERO_ROWS",
                )

                composed = compose_product_rows(
                    report_products,
                    inventory_products,
                    home_products,
                    order_rows,
                )
                if composed:
                    result["products"] = enrich_product_rows(composed)

                started = time.time()
                ads_summary, ad_campaigns, resolved_merchant = crawl_ads_data(
                    page,
                    merchant_id=ctx.merchant_id,
                )
                ctx.merchant_id = resolved_merchant or ctx.merchant_id
                result["merchant_id"] = ctx.merchant_id
                _record(
                    diagnostics,
                    "ads_campaign_manager",
                    page.url,
                    ad_campaigns,
                    started,
                    "" if ad_campaigns or ads_summary else "ZERO_ROWS",
                )
                ads_summary = coalesce_ads_summary(ads_summary, result.get("metrics"))
                if ads_summary:
                    result["metrics"] = merge_ads_metrics(result.get("metrics") or [], ads_summary)
                if result.get("products"):
                    if ad_campaigns:
                        result["products"] = merge_campaign_ads_into_products(
                            result.get("products") or [],
                            ad_campaigns,
                        )
                    if ads_summary:
                        result["products"] = allocate_account_ads_by_revenue(
                            result.get("products") or [],
                            ads_summary,
                        )

                    result["products"] = enrich_product_rows(result["products"])

            if normalized_scope in {"daily", "reports"}:
                started = time.time()
                coupons, shipments = crawl_operational_lists(page)
                if coupons:
                    result["coupons"] = coupons
                if shipments:
                    result["shipments"] = shipments
                _record(diagnostics, "coupons", "promotions/*", coupons, started)
                _record(diagnostics, "shipments", "fba/inbound/*", shipments, time.time())
                if not result["cases"]:
                    started = time.time()
                    cases = crawl_cases(page)
                    if cases:
                        result["cases"] = cases
                    _record(diagnostics, "cases", "case-lobby/*", cases, started)
                if not result["cases"] and result.get("seller_news"):
                    result["cases"] = cases_from_seller_news(result["seller_news"])

            if normalized_scope == "daily":
                started = time.time()
                messages = crawl_messages(page)
                if messages:
                    result["buyer_messages"] = messages
                _record(diagnostics, "messages", page.url, messages, started)

                started = time.time()
                reviews = crawl_reviews(page)
                if reviews:
                    result["reviews"] = reviews
                _record(diagnostics, "reviews", page.url, reviews, started)

                if not result["cases"]:
                    _, cases = parse_home_news_and_cases(home_text)
                    result["cases"] = cases
                if not result["cases"]:
                    cases = crawl_cases(page)
                    if cases:
                        result["cases"] = cases
                if not result["cases"] and result.get("seller_news"):
                    result["cases"] = cases_from_seller_news(result["seller_news"])
                if not result.get("coupons") or not result.get("shipments"):
                    coupons, shipments = crawl_operational_lists(page)
                    if coupons and not result.get("coupons"):
                        result["coupons"] = coupons
                    if shipments and not result.get("shipments"):
                        result["shipments"] = shipments

            if normalized_scope == "account_health" and not result["metrics"]:
                started = time.time()
                result["metrics"] = crawl_account_health_metrics(page)
                _record(diagnostics, "account_health", page.url, result["metrics"], started)

            if not looks_logged_in(home_text, HOME_URL) and not result["metrics"] and not result["products"]:
                capture = save_capture(page, store_name=store_name, suffix="empty")
                raise RuntimeError(f"卖家平台页面未解析到数据，截图: {capture}")

            if normalized_scope == "account_health" and not result["metrics"]:
                capture = save_capture(page, store_name=store_name, suffix="empty")
                raise RuntimeError(f"未解析到账户状况指标，截图: {capture}")

            _annotate_product_sync(result, normalized_scope, catalog_count, br_count)

            diag_summary = diagnostics.summary()
            result["page_diagnostics"] = diag_summary["page_diagnostics"]
            result["result_summary"] = {
                **diag_summary,
                "products_count": len(result.get("products") or []),
                "orders_count": len(result.get("outbound_orders") or []),
                "merchant_id": result.get("merchant_id") or "",
            }
            if result.get("product_sync_warning"):
                result["result_summary"]["warnings"] = list(
                    dict.fromkeys(
                        [
                            *diag_summary.get("warnings", []),
                            str(result.get("product_sync_warning")),
                        ]
                    )
                )

            if result.get("product_sync_warning") == "NO_ASIN_ROWS" and not result.get("capture_path"):
                latest = sorted(CAPTURE_DIR.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
                if latest:
                    result["capture_path"] = str(latest[0])

            return result
        finally:
            try:
                browser.close()
            except Exception:
                pass
            try:
                ziniao.stop_browser(
                    browser_id=browser_id or None,
                    browser_oauth=browser_oauth or None,
                )
            except Exception:
                pass


def crawl_account_health(**kwargs: Any) -> dict[str, Any]:
    return run_crawl(scope="account_health", **kwargs)
