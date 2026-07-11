"""Probe BR after prepare + inventory card parser."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend/python"))

from app.amazon.crawlers.business_report import _prepare_business_report_page, _scroll_br_table
from app.amazon.page_urls import INVENTORY_URLS, REPORT_URLS
from app.ziniao.client import ZiniaoClient, ZiniaoConfig

BROWSER_ID = "16505337258263"


def main() -> None:
    ziniao = ZiniaoClient(ZiniaoConfig.from_env())
    ziniao.ensure_webdriver_client(wait_seconds=20)
    start = ziniao.start_browser(browser_id=BROWSER_ID, headless=False)
    port = start.get("debuggingPort") or start.get("debug_port") or 9222
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        page = browser.contexts[0].pages[0] if browser.contexts and browser.contexts[0].pages else browser.contexts[0].new_page()
        page.goto(REPORT_URLS[0], wait_until="domcontentloaded")
        page.wait_for_timeout(8000)
        _prepare_business_report_page(page)
        page.wait_for_timeout(12000)
        _scroll_br_table(page)
        text = page.inner_text("body")
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for i, line in enumerate(lines):
            if line == "B08B8X3Q6C":
                print("BR prepared context:")
                for j in range(i, min(len(lines), i + 25)):
                    print(f"{j}: {lines[j]}")
                break
        from app.amazon.parsers.seller_pages import EXTRACT_BUSINESS_REPORT_JS, EXTRACT_BR_BODY_TEXT_JS
        trows = page.evaluate(EXTRACT_BUSINESS_REPORT_JS) or []
        brows = page.evaluate(EXTRACT_BR_BODY_TEXT_JS) or []
        print("table", len(trows), "body", len(brows))
        if trows:
            print(json.dumps(trows[0], ensure_ascii=False))
        if brows:
            print(json.dumps(brows[0], ensure_ascii=False))

        from app.amazon.parsers.seller_pages import EXTRACT_INVENTORY_CARDS_JS
        page.goto(INVENTORY_URLS[0], wait_until="domcontentloaded")
        page.wait_for_timeout(14000)
        cards = page.evaluate(EXTRACT_INVENTORY_CARDS_JS) or []
        print("inv cards", len(cards))
        print(json.dumps(cards[:5], ensure_ascii=False))
        ziniao.stop_browser(browser_id=BROWSER_ID)


if __name__ == "__main__":
    main()
