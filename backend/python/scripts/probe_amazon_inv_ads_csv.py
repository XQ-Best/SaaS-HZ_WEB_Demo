#!/usr/bin/env python3
"""联调 Inventory + Ads ASIN CSV（headed）。"""
from __future__ import annotations

import argparse
import json

from app.amazon.page_urls import HOME_URL, INVENTORY_URLS
from app.amazon.session_context import extract_debug_port, require_seller_logged_in
from app.amazon.sources.ads_asin_report_csv import crawl_ads_asin_csv
from app.amazon.sources.inventory_csv import crawl_inventory_csv
from app.ziniao.client import ZiniaoClient, ZiniaoConfig


def _log(msg: str) -> None:
    print(msg, flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--browser-id", default="16505337258263")
    parser.add_argument("--store-name", default="YOTO美国账号")
    parser.add_argument("--pause-seconds", type=int, default=5)
    args = parser.parse_args()

    ziniao = ZiniaoClient(ZiniaoConfig.from_env())
    ziniao.ensure_webdriver_client(wait_seconds=20)
    start = ziniao.start_browser(browser_id=args.browser_id, headless=not args.headed)
    port = extract_debug_port(start)

    from playwright.sync_api import sync_playwright

    exit_code = 0
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            ctx = browser.contexts[0] if browser.contexts else browser.new_context()
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.set_default_timeout(90_000)

            page.goto(HOME_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            require_seller_logged_in(page, page.inner_text("body"), store_name=args.store_name)

            _log("==> crawl_inventory_csv ...")
            inv = crawl_inventory_csv(page, store_name=args.store_name)
            inv_sample = inv.rows[:3]
            _log(json.dumps({
                "inventory": {
                    "rows": len(inv.rows),
                    "warning": inv.warning,
                    "artifact": inv.artifact,
                    "page_url": inv.page_url,
                    "sample": inv_sample,
                }
            }, ensure_ascii=False, indent=2))

            _log("==> crawl_ads_asin_csv ...")
            ads = crawl_ads_asin_csv(page, store_name=args.store_name, period_days=7)
            _log(json.dumps({
                "ads": {
                    "rows": len(ads.rows),
                    "warning": ads.warning,
                    "artifact": ads.artifact,
                    "page_url": ads.page_url,
                    "merchant_id": ads.merchant_id,
                    "sample": ads.rows[:3],
                }
            }, ensure_ascii=False, indent=2))

            if not inv.rows:
                exit_code |= 1
            if not ads.rows:
                exit_code |= 2
            if args.headed and args.pause_seconds > 0:
                page.wait_for_timeout(args.pause_seconds * 1000)
            browser.close()
    finally:
        try:
            ziniao.stop_browser(browser_id=args.browser_id)
        except Exception:
            pass
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
