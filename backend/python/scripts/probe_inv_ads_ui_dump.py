#!/usr/bin/env python3
"""Dump 库存/广告页可点击元素。"""
from __future__ import annotations

import argparse
import json

from app.amazon.page_urls import HOME_URL, INVENTORY_URLS
from app.amazon.session_context import extract_debug_port, require_seller_logged_in, save_capture
from app.ziniao.client import ZiniaoClient, ZiniaoConfig

DUMP_JS = """
(label) => {
  const blocked = (node) => {
    const footer = document.querySelector('footer, [class*="footer"]');
    return footer && footer.contains(node);
  };
  const scopes = ['main', '#sc-content-container', 'kat-workflow', '[role="main"]'];
  let root = document.body;
  for (const sel of scopes) {
    const el = document.querySelector(sel);
    if (el) { root = el; break; }
  }
  const out = [];
  const sel = 'button, kat-button, kat-dropdown-button, [role="button"], a, input[type="button"], kat-tab';
  for (const node of root.querySelectorAll(sel)) {
    if (blocked(node)) continue;
    const text = (node.innerText || '').trim().replace(/\\s+/g, ' ').slice(0, 120);
    const aria = (node.getAttribute('aria-label') || '').trim();
    const labelAttr = (node.getAttribute('label') || '').trim();
    const href = (node.getAttribute('href') || node.href || '').slice(0, 120);
    const tag = node.tagName.toLowerCase();
    const blob = [text, aria, labelAttr, href].join(' ');
    const hit = /download|export|csv|导出|下载|report|报告/i.test(blob);
    if (hit || /inventory|库存|apply|应用|export/i.test(blob)) {
      out.push({ tag, text, aria, label: labelAttr, href, hit });
    }
  }
  return { url: location.href, title: document.title, items: out.slice(0, 60) };
}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--browser-id", default="16505337258263")
    parser.add_argument("--store-name", default="YOTO美国账号")
    parser.add_argument("--page", choices=("inventory", "ads"), default="inventory")
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
            if args.page == "inventory":
                page.goto(INVENTORY_URLS[0], wait_until="domcontentloaded")
            else:
                page.goto("https://advertising.amazon.com/reports", wait_until="domcontentloaded")
            page.wait_for_timeout(10000)
            try:
                cap = save_capture(page, store_name=args.store_name, suffix=f"{args.page}_ui")
            except Exception as exc:
                cap = f"capture_failed:{exc.__class__.__name__}"
            data = page.evaluate(DUMP_JS, args.page)
            data["capture"] = cap
            print(json.dumps(data, ensure_ascii=False, indent=2), flush=True)
            browser.close()
    finally:
        try:
            ziniao.stop_browser(browser_id=args.browser_id)
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
