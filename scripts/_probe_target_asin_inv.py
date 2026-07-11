"""Search inventory pages for target ASIN metrics."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend/python"))

from app.amazon.page_urls import INVENTORY_URLS
from app.amazon.parsers.seller_pages import EXTRACT_INVENTORY_CARDS_JS
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
        page.goto(INVENTORY_URLS[0], wait_until="domcontentloaded")
        page.wait_for_timeout(14000)
        found = None
        for page_no in range(1, 4):
            rows = page.evaluate(EXTRACT_INVENTORY_CARDS_JS) or []
            for row in rows:
                if str(row.get("asin", "")).upper() == TARGET:
                    found = row
                    break
            if found:
                print("page", page_no, found)
                break
            clicked = page.evaluate(
                """
                () => {
                  const btn = [...document.querySelectorAll('button, a, kat-pagination button')].find((el) =>
                    /next|下一页|›|→|>>/i.test((el.innerText || el.getAttribute('aria-label') || '').trim())
                  );
                  if (!btn || btn.disabled || btn.getAttribute('aria-disabled') === 'true') return false;
                  btn.click();
                  return true;
                }
                """
            )
            if not clicked:
                break
            page.wait_for_timeout(3500)
        if not found:
            print("not found in 3 pages")
            rows = page.evaluate(EXTRACT_INVENTORY_CARDS_JS) or []
            pv = sorted(
                [
                    r
                    for r in rows
                    if int(str(r.get("page_views") or "0")) > 0
                ],
                key=lambda item: int(str(item.get("page_views") or "0")),
                reverse=True,
            )
            print("top pv rows", pv[:5])
        ziniao.stop_browser(browser_id=BROWSER_ID)


if __name__ == "__main__":
    main()
