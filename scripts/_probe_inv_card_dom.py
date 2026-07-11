"""Probe inventory card DOM boundaries."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend/python"))

from app.amazon.page_urls import INVENTORY_URLS
from app.amazon.parsers.seller_pages import EXTRACT_INVENTORY_CARDS_JS
from app.ziniao.client import ZiniaoClient, ZiniaoConfig

BROWSER_ID = "16505337258263"
JS = """
() => {
  const anchor = [...document.querySelectorAll('a[href*="/dp/B0"]')][0];
  if (!anchor) return null;
  const walk = [];
  let current = anchor;
  for (let depth = 0; depth < 14 && current; depth += 1) {
    const text = (current.innerText || '').trim();
    walk.push({
      depth,
      tag: current.tagName,
      cls: String(current.className || '').slice(0, 100),
      hasPv: /页面浏览量|page views/i.test(text),
      hasInv: /可售|available/i.test(text),
      len: text.length,
      snippet: text.slice(0, 500).replace(/\\n/g, ' | '),
    });
    current = current.parentElement;
  }
  return { href: anchor.href, walk };
}
"""


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
        info = page.evaluate(JS)
        rows = page.evaluate(EXTRACT_INVENTORY_CARDS_JS) or []
        print("walk:", json.dumps(info, ensure_ascii=False)[:3000])
        b0_pv = [
            r
            for r in rows
            if str(r.get("asin", "")).startswith("B0")
            and int(str(r.get("page_views") or "0")) > 0
        ]
        print("B0 pv>0", len(b0_pv), b0_pv[:3])
        ziniao.stop_browser(browser_id=BROWSER_ID)


if __name__ == "__main__":
    main()
