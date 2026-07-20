#!/usr/bin/env python3
"""Dump BR 页面可点击元素（找 CSV 导出按钮真实文案/结构）。"""
from __future__ import annotations

import argparse
import json

from app.amazon.navigation_guard import navigate_to_br_child_asin
from app.amazon.page_urls import HOME_URL
from app.amazon.session_context import extract_debug_port, require_seller_logged_in, save_capture
from app.ziniao.client import ZiniaoClient, ZiniaoConfig

DUMP_JS = """
() => {
  const blocked = (node) => {
    const footer = document.querySelector('footer, [class*="footer"]');
    return footer && footer.contains(node);
  };
  const scopes = ['kat-workflow', 'main', '[data-testid="report-page"]', '#sc-content-container', 'kat-side-nav'];
  let root = document.body;
  for (const sel of scopes) {
    const el = document.querySelector(sel);
    if (el) { root = el; break; }
  }
  const out = [];
  const sel = 'button, kat-button, kat-dropdown-button, kat-icon, [role="button"], a, input[type="button"], kat-tab, [role="tab"], kat-menu-item, kat-option, li';
  for (const node of root.querySelectorAll(sel)) {
    if (blocked(node)) continue;
    const text = (node.innerText || '').trim().replace(/\\s+/g, ' ').slice(0, 120);
    const aria = (node.getAttribute('aria-label') || '').trim();
    const label = (node.getAttribute('label') || '').trim();
    const title = (node.getAttribute('title') || '').trim();
    const href = (node.getAttribute('href') || node.href || '').slice(0, 120);
    const tag = node.tagName.toLowerCase();
    const id = node.id || '';
    const cls = (node.className && String(node.className).slice(0, 80)) || '';
    const hit = /download|export|csv|导出|下载|spreadsheet|report/i.test([text, aria, label, title, href].join(' '));
    if (hit || text || aria || label) {
      out.push({ tag, text, aria, label, title, href, id, cls, hit });
    }
  }
  return out.filter((x) => x.hit || /apply|应用|period|日期|7|30|run/i.test([x.text, x.aria, x.label].join(' '))).slice(0, 80);
}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--browser-id", default="16505337258263")
    parser.add_argument("--store-name", default="YOTO美国账号")
    args = parser.parse_args()

    ziniao = ZiniaoClient(ZiniaoConfig.from_env())
    ziniao.ensure_webdriver_client(wait_seconds=20)
    start = ziniao.start_browser(browser_id=args.browser_id, headless=not args.headed)
    port = extract_debug_port(start)

    from playwright.sync_api import sync_playwright

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            ctx = browser.contexts[0] if browser.contexts else browser.new_context()
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto(HOME_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            require_seller_logged_in(page, page.inner_text("body"), store_name=args.store_name)
            navigate_to_br_child_asin(page, home_url=HOME_URL)
            page.wait_for_timeout(8000)
            cap = save_capture(page, store_name=args.store_name, suffix="br_ui_dump")
            items = page.evaluate(DUMP_JS)
            print(json.dumps({"url": page.url, "capture": cap, "items": items}, ensure_ascii=False, indent=2), flush=True)
            browser.close()
    finally:
        try:
            ziniao.stop_browser(browser_id=args.browser_id)
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
