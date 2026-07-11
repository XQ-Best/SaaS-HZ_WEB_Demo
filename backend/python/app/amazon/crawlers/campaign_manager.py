"""Campaign Manager 广告爬取。"""
from __future__ import annotations

from typing import Any

from app.amazon.crawlers._page_js import evaluate_js
from app.amazon.page_registry import ads_urls_for_merchant
from app.amazon.page_urls import ADS_CAMPAIGN_MANAGER_BASE, HOME_URL
from app.amazon.parsers.seller_pages import EXTRACT_AD_CAMPAIGNS_JS, EXTRACT_ADS_SUMMARY_JS, EXTRACT_AD_SKU_SPEND_JS
from app.amazon.session_context import looks_login_page, resolve_merchant_id


def crawl_ads_data(page, *, merchant_id: str = "") -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    summary: dict[str, Any] = {}
    campaigns: list[dict[str, Any]] = []
    seen_campaigns: set[str] = set()
    resolved_merchant = merchant_id

    try:
        page.goto(HOME_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        if not resolved_merchant:
            resolved_merchant = resolve_merchant_id(page)
        if not resolved_merchant:
            page.goto(ADS_CAMPAIGN_MANAGER_BASE, wait_until="domcontentloaded")
            page.wait_for_timeout(8000)
            resolved_merchant = resolve_merchant_id(page)
    except Exception:
        pass

    for url in ads_urls_for_merchant(resolved_merchant):
        try:
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(16000)
            try:
                page.wait_for_load_state("networkidle", timeout=20000)
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
            if campaigns and summary.get("ad_spend_30d"):
                break
        except Exception:
            continue
    return summary, campaigns, resolved_merchant
