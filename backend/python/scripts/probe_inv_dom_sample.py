#!/usr/bin/env python3
from __future__ import annotations

import json

from app.amazon.crawlers.inventory import crawl_inventory_products
from app.amazon.page_urls import HOME_URL
from app.amazon.session_context import extract_debug_port, require_seller_logged_in
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
        rows = crawl_inventory_products(page, store_name="YOTO", max_pages=2, fast=False)
        sample = rows[:8]
        inv_pos = sum(1 for r in rows if int(str(r.get("inventory") or "0").replace(",", "") or 0) > 0)
        print(json.dumps({"rows": len(rows), "inv_gt0": inv_pos, "sample": sample}, ensure_ascii=False, indent=2), flush=True)
finally:
    ziniao.stop_browser(browser_id="16505337258263")
