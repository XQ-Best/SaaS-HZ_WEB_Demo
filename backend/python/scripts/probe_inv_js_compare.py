#!/usr/bin/env python3
from __future__ import annotations

import json

from app.amazon.crawlers._page_js import evaluate_js
from app.amazon.page_urls import HOME_URL, INVENTORY_URLS
from app.amazon.parsers.seller_pages import EXTRACT_INVENTORY_CARDS_JS, EXTRACT_INVENTORY_JS
from app.amazon.session_context import extract_debug_port, require_seller_logged_in
from app.ziniao.client import ZiniaoClient, ZiniaoConfig
from playwright.sync_api import sync_playwright


def _inv_gt0(rows):
    return sum(1 for r in rows if int(str(r.get("inventory") or "0").replace(",", "") or 0) > 0)


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
        cards = evaluate_js(page, EXTRACT_INVENTORY_CARDS_JS) or []
        table = evaluate_js(page, EXTRACT_INVENTORY_JS) or []
        print(json.dumps({
            "cards": {"rows": len(cards), "inv_gt0": _inv_gt0(cards), "sample": cards[:3]},
            "table": {"rows": len(table), "inv_gt0": _inv_gt0(table), "sample": table[:3]},
        }, ensure_ascii=False, indent=2), flush=True)
finally:
    ziniao.stop_browser(browser_id="16505337258263")
