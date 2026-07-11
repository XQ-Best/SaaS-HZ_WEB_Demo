"""Business Report 爬取。"""
from __future__ import annotations

import re
from typing import Any

from app.amazon.composer.product_filters import (
    filter_valid_product_rows,
    has_report_metrics,
    sanitize_br_rows,
)
from app.amazon.crawlers._page_js import evaluate_js
from app.amazon.page_urls import REPORT_URLS
from app.amazon.parsers.seller_pages import (
    EXTRACT_BR_BODY_TEXT_JS,
    EXTRACT_BR_GRID_JS,
    EXTRACT_BUSINESS_REPORT_JS,
)
from app.amazon.session_context import looks_login_page, save_capture


def _click_report_apply(page) -> None:
    try:
        page.evaluate(
            """
            () => {
              const nodes = [...document.querySelectorAll('button, kat-button, input[type=submit]')];
              const btn = nodes.find((node) => /apply|应用|run report|刷新|更新|generate/i.test(
                (node.innerText || node.value || '').trim()
              ));
              if (btn) btn.click();
            }
            """
        )
        page.wait_for_timeout(6000)
    except Exception:
        pass


def _prepare_business_report_page(page) -> None:
    try:
        page.evaluate(
            """
            () => {
              const clickMatch = (pattern) => {
                const nodes = [
                  ...document.querySelectorAll('button, a, kat-tab, kat-button, [role="tab"], label, span'),
                ];
                const target = nodes.find((node) => pattern.test(
                  (node.innerText || node.getAttribute('label') || node.getAttribute('aria-label') || '').trim()
                ));
                if (target) target.click();
              };
              clickMatch(/detail page sales and traffic by child asin|子\\s*asin\\s*的详情页面|详情页面销售和流量/i);
              clickMatch(/by asin|按\\s*asin|child asin|子\\s*asin|sku/i);
              clickMatch(/last\\s*30|最近\\s*30|30\\s*days?|30\\s*天/i);
              clickMatch(/查看详细|view detail|detail page sales|详情页面/i);
              clickMatch(/子\\s*asin|child asin/i);
              clickMatch(/sessions|会话|page views|浏览量/i);
            }
            """
        )
        page.wait_for_timeout(2500)
        _click_report_apply(page)
    except Exception:
        pass


def _scroll_br_table(page) -> None:
    try:
        page.evaluate(
            """
            async () => {
              const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
              const roots = [];
              const walk = (node) => {
                if (!node) return;
                roots.push(node);
                if (node.shadowRoot) walk(node.shadowRoot);
                node.querySelectorAll?.('*').forEach((el) => { if (el.shadowRoot) walk(el.shadowRoot); });
              };
              walk(document);
              let scroller = null;
              for (const root of roots) {
                scroller = root.querySelector('[role="grid"]')
                  || root.querySelector('kat-table')
                  || root.querySelector('.mt-table-container')
                  || root.querySelector('[class*="scroll"]');
                if (scroller) break;
              }
              for (let i = 0; i < 30; i += 1) {
                if (scroller) scroller.scrollTop += 800;
                window.scrollBy(0, 1000);
                await sleep(300);
              }
            }
            """
        )
        page.wait_for_timeout(2500)
    except Exception:
        pass


def crawl_business_report(page, *, store_name: str = "") -> list[dict[str, Any]]:
    for url in REPORT_URLS:
        for attempt in range(3):
            try:
                page.goto(url, wait_until="domcontentloaded")
                try:
                    page.wait_for_load_state("networkidle", timeout=35000)
                except Exception:
                    pass
                if attempt > 0:
                    page.reload(wait_until="domcontentloaded")
                    page.wait_for_timeout(4000)
                _prepare_business_report_page(page)
                extra_wait = 8000 + attempt * 5000
                page.wait_for_timeout(extra_wait)
                for selector in ("table tbody tr", "kat-table", "[role='grid']"):
                    try:
                        page.wait_for_selector(selector, timeout=12000 + attempt * 4000)
                        break
                    except Exception:
                        continue
                page.evaluate("() => { window.scrollTo(0, document.body.scrollHeight); }")
                page.wait_for_timeout(3000 + attempt * 2000)
                _scroll_br_table(page)
                body = page.inner_text("body")
                if looks_login_page(body, page.url):
                    break
                if not re.search(r"(sales|traffic|asin|销售额|流量|ordered product|business report)", body, re.I):
                    save_capture(page, store_name=store_name, suffix=f"br_nodata_a{attempt}")
                    if attempt < 2:
                        continue
                    break
                table_rows: list[dict[str, Any]] = []
                for js in (EXTRACT_BUSINESS_REPORT_JS, EXTRACT_BR_GRID_JS):
                    candidate = evaluate_js(page, js)
                    if candidate and len(candidate) >= len(table_rows):
                        table_rows = candidate
                if table_rows:
                    with_metrics = [
                        row
                        for row in sanitize_br_rows(filter_valid_product_rows(table_rows))
                        if has_report_metrics(row)
                    ]
                    if with_metrics:
                        return with_metrics
                body_rows = evaluate_js(page, EXTRACT_BR_BODY_TEXT_JS) or []
                with_metrics = [
                    row
                    for row in sanitize_br_rows(filter_valid_product_rows(body_rows))
                    if has_report_metrics(row)
                ]
                if with_metrics:
                    return with_metrics
                valid = filter_valid_product_rows(table_rows or body_rows)
                with_metrics = [row for row in valid if has_report_metrics(row)]
                if with_metrics:
                    return with_metrics
                if valid and attempt == 2:
                    save_capture(page, store_name=store_name, suffix="br_no_metrics")
                elif not valid:
                    save_capture(page, store_name=store_name, suffix=f"br_nodata_a{attempt}")
                if attempt < 2:
                    continue
            except Exception:
                if attempt < 2:
                    page.wait_for_timeout(3000)
                    continue
    return []
