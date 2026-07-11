"""Probe inventory + BR page text via Ziniao (read-only)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend/python"))

from app.amazon.parsers.seller_pages import (
    EXTRACT_BR_BODY_TEXT_JS,
    EXTRACT_BUSINESS_REPORT_JS,
    EXTRACT_INVENTORY_JS,
)
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
        page.set_default_timeout(90000)

        page.goto(INVENTORY_URLS[0], wait_until="domcontentloaded")
        page.wait_for_timeout(14000)
        page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        inv_rows = page.evaluate(EXTRACT_INVENTORY_JS) or []
        inv_text = page.inner_text("body")[:4000]
        print("INVENTORY rows", len(inv_rows))
        print("sample rows", json.dumps(inv_rows[:3], ensure_ascii=False)[:1200])
        print("body snippet", inv_text[:1500].replace("\n", " | "))

        page.goto(REPORT_URLS[0], wait_until="domcontentloaded")
        page.wait_for_timeout(12000)
        br_rows = page.evaluate(EXTRACT_BUSINESS_REPORT_JS) or []
        br_body = page.evaluate(EXTRACT_BR_BODY_TEXT_JS) or []
        br_text = page.inner_text("body")[:4000]
        print("BR table rows", len(br_rows))
        print("BR body rows", len(br_body))
        print("BR sample", json.dumps((br_rows or br_body)[:3], ensure_ascii=False)[:1200])
        headers = [line for line in br_text.splitlines() if line.strip()][:40]
        print("BR headers/lines", " || ".join(headers[:25]))

        ziniao.stop_browser(browser_id=BROWSER_ID)


if __name__ == "__main__":
    main()
