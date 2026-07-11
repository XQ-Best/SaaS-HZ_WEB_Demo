"""Dump line context around ASIN on inventory + BR pages."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend/python"))

from app.amazon.page_urls import INVENTORY_URLS, REPORT_URLS
from app.ziniao.client import ZiniaoClient, ZiniaoConfig

BROWSER_ID = "16505337258263"


def dump_around(text: str, marker: str, radius: int = 18) -> None:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for i, line in enumerate(lines):
        if marker in line:
            print(f"--- around {marker} @ {i} ---")
            for j in range(max(0, i - 2), min(len(lines), i + radius)):
                print(f"{j:04d}: {lines[j]}")


def main() -> None:
    ziniao = ZiniaoClient(ZiniaoConfig.from_env())
    ziniao.ensure_webdriver_client(wait_seconds=20)
    start = ziniao.start_browser(browser_id=BROWSER_ID, headless=False)
    port = start.get("debuggingPort") or start.get("debug_port") or 9222
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        page = browser.contexts[0].pages[0] if browser.contexts and browser.contexts[0].pages else browser.contexts[0].new_page()
        page.goto(INVENTORY_URLS[0], wait_until="domcontentloaded")
        page.wait_for_timeout(14000)
        inv = page.inner_text("body")
        dump_around(inv, "B0H8BRYF9T")
        dump_around(inv, "B08B8X3Q6C")

        page.goto(REPORT_URLS[0], wait_until="domcontentloaded")
        page.wait_for_timeout(14000)
        br = page.inner_text("body")
        dump_around(br, "B08B8X3Q6C")
        ziniao.stop_browser(browser_id=BROWSER_ID)


if __name__ == "__main__":
    main()
