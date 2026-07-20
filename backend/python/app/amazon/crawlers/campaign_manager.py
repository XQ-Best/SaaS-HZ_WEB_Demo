"""Campaign Manager 广告 DOM 爬取（已降级，CSV 失败时 AMAZON_ADS_DOM_FALLBACK=1 兜底）。"""
from __future__ import annotations

from typing import Any

from app.amazon.crawlers._page_js import evaluate_js
from app.amazon.page_registry import ads_urls_for_merchant
from app.amazon.page_urls import ADS_CAMPAIGN_MANAGER_BASE, HOME_URL
from app.amazon.parsers.seller_pages import EXTRACT_AD_CAMPAIGNS_JS, EXTRACT_ADS_SUMMARY_JS, EXTRACT_AD_SKU_SPEND_JS
from app.amazon.session_context import looks_login_page, resolve_merchant_id


def crawl_ads_data(page, *, merchant_id: str = "", fast: bool = False) -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    summary: dict[str, Any] = {}
    campaigns: list[dict[str, Any]] = []
    seen_campaigns: set[str] = set()
    resolved_merchant = merchant_id
    wait_ms = 10000 if fast else 16000
    network_idle_ms = 12000 if fast else 20000

    if not resolved_merchant:
        try:
            page.goto(HOME_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(3000 if fast else 5000)
            resolved_merchant = resolve_merchant_id(page)
            if not resolved_merchant:
                page.goto(ADS_CAMPAIGN_MANAGER_BASE, wait_until="domcontentloaded")
                page.wait_for_timeout(6000 if fast else 8000)
                resolved_merchant = resolve_merchant_id(page)
        except Exception:
            pass

    ad_urls = ads_urls_for_merchant(resolved_merchant)
    if fast:
        ad_urls = ad_urls[:1]

    for url in ad_urls:
        try:
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(wait_ms)
            try:
                page.wait_for_load_state("networkidle", timeout=network_idle_ms)
            except Exception:
                pass
            body = page.inner_text("body")
            if looks_login_page(body, page.url):
                continue
            if not resolved_merchant:
                resolved_merchant = resolve_merchant_id(page)
            if not summary.get("ad_spend_30d") and not summary.get("acos"):
                candidate = page.evaluate(EXTRACT_ADS_SUMMARY_JS) or {}
                if isinstance(candidate, dict):
                    for key, value in candidate.items():
                        if value and not summary.get(key):
                            summary[key] = value
            rows = evaluate_js(page, EXTRACT_AD_CAMPAIGNS_JS)
            if not rows:
                rows = evaluate_js(page, EXTRACT_AD_SKU_SPEND_JS)
            for row in rows:
                if not isinstance(row, dict):
                    continue
                key = str(row.get("asin") or row.get("campaign_name") or "")
                if key and key in seen_campaigns:
                    continue
                if key:
                    seen_campaigns.add(key)
                campaigns.append(row)
            if campaigns and (summary.get("ad_spend_30d") or not fast):
                break
            if fast and campaigns:
                break
        except Exception:
            continue
    return summary, campaigns, resolved_merchant
