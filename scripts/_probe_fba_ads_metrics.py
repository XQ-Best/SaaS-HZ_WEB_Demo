"""Probe FBA health + ads product traffic for sessions/inventory."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend/python"))

from app.amazon.page_urls import INVENTORY_URLS, build_ads_urls
from app.amazon.parsers.seller_pages import EXTRACT_INVENTORY_CARDS_JS, EXTRACT_PERFORMANCE_TABLE_JS
from app.ziniao.client import ZiniaoClient, ZiniaoConfig

BROWSER_ID = "16505337258263"
TARGET = "B08B8X3Q6C"


def main() -> None:
    ziniao = ZiniaoClient(ZiniaoConfig.from_env())
    ziniao.ensure_webdriver_client(wait_seconds=20)
    start = ziniao.start_browser(browser_id=BROWSER_ID, headless=False)
    port = start.get("debuggingPort") or start.get("debug_port") or 9222
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        page = (
            browser.contexts[0].pages[0]
            if browser.contexts and browser.contexts[0].pages
            else browser.contexts[0].new_page()
        )
        health_url = INVENTORY_URLS[-1]
        page.goto(health_url, wait_until="domcontentloaded")
        page.wait_for_timeout(14000)
        body = page.inner_text("body")
        idx = body.find(TARGET)
        print("health found", idx >= 0)
        rows = page.evaluate(EXTRACT_PERFORMANCE_TABLE_JS) or []
        print("health table rows", len(rows))
        hit = [r for r in rows if TARGET in str(r.get("asin", "")).upper()]
        print("health hit", json.dumps(hit[:2], ensure_ascii=False))

        for ads_url in build_ads_urls("A3B69JEON4HA6")[:2]:
            page.goto(ads_url, wait_until="domcontentloaded")
            page.wait_for_timeout(12000)
            ads_rows = page.evaluate(EXTRACT_PERFORMANCE_TABLE_JS) or []
            print("ads url", ads_url[:80], "rows", len(ads_rows))
            hit = [r for r in ads_rows if str(r.get("asin", "")).upper() == TARGET]
            if hit:
                print("ads hit", json.dumps(hit[:1], ensure_ascii=False))
                break

        ziniao.stop_browser(browser_id=BROWSER_ID)


if __name__ == "__main__":
    main()
