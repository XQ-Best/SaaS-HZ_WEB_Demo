#!/usr/bin/env python3
from __future__ import annotations

import json

from app.amazon.page_urls import HOME_URL, INVENTORY_URLS
from app.amazon.session_context import extract_debug_port, require_seller_logged_in
from app.amazon.sources.click_export import _SHADOW_EXPORT_JS
from app.ziniao.client import ZiniaoClient, ZiniaoConfig
from playwright.sync_api import sync_playwright

ziniao = ZiniaoClient(ZiniaoConfig.from_env())
ziniao.ensure_webdriver_client(wait_seconds=20)
start = ziniao.start_browser(browser_id="16505337258263", headless=False)
port = extract_debug_port(start)
try:
    with sync_playwright() as p:
        page = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}").contexts[0].pages[0]
        page.goto(HOME_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        require_seller_logged_in(page, page.inner_text("body"), store_name="YOTO")
        page.goto(INVENTORY_URLS[0], wait_until="domcontentloaded")
        page.wait_for_timeout(12000)
        labels = page.evaluate(
            """
            () => {
              const rows = [...document.querySelectorAll('[class*="tableContentRow"]')].slice(0, 1);
              const lines = (rows[0]?.innerText || '').split('\\n').map((s) => s.trim()).filter(Boolean);
              return lines.map((line, i) => ({ i, line, has_amazon: /亚马逊|amazon/i.test(line), has_avail: /可售|available|fulfill/i.test(line) }));
            }
            """
        )
        clicked = page.evaluate(_SHADOW_EXPORT_JS)
        print(json.dumps({"labels": labels, "shadow_export_clicked": clicked, "url": page.url}, ensure_ascii=False, indent=2), flush=True)
finally:
    ziniao.stop_browser(browser_id="16505337258263")
