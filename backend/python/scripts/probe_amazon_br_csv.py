#!/usr/bin/env python3
"""联调 Business Report CSV：先测绘导航，再下载（禁止全页盲点）。"""
from __future__ import annotations

import argparse
import json
import sys

from app.amazon.navigation_guard import assert_allowed_url, is_blocked_url, navigate_to_br_child_asin
from app.amazon.page_urls import HOME_URL
from app.amazon.session_context import extract_debug_port, require_seller_logged_in
from app.amazon.sources.business_report_csv import crawl_business_report_csv
from app.ziniao.client import ZiniaoClient, ZiniaoConfig


def _log(msg: str) -> None:
    print(msg, flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="BR CSV 联调（侧栏导航 + 作用域点击）")
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--browser-id", default="16505337258263")
    parser.add_argument("--store-name", default="YOTO美国账号")
    parser.add_argument("--pause-seconds", type=int, default=15)
    args = parser.parse_args()

    ziniao = ZiniaoClient(ZiniaoConfig.from_env())
    ziniao.ensure_webdriver_client(wait_seconds=20)
    start = ziniao.start_browser(browser_id=args.browser_id, headless=not args.headed)
    port = extract_debug_port(start)

    from playwright.sync_api import sync_playwright

    exit_code = 1
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            ctx = browser.contexts[0] if browser.contexts else browser.new_context()
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.set_default_timeout(90_000)

            page.goto(HOME_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            require_seller_logged_in(page, page.inner_text("body"), store_name=args.store_name)

            _log("==> 侧栏导航至 BR 子 ASIN ...")
            try:
                final = navigate_to_br_child_asin(page, home_url=HOME_URL)
                _log(f"==> 导航落地: {final}")
                if is_blocked_url(final):
                    _log("错误：落入 sellermobileapp 等禁止页")
                    return 4
                assert_allowed_url(final, context="probe_nav")
            except RuntimeError as exc:
                _log(f"导航失败: {exc}")
                return 5

            _log("==> crawl_business_report_csv ...")
            br = crawl_business_report_csv(page, store_name=args.store_name)
            _log(json.dumps({
                "rows": len(br.rows),
                "warning": br.warning,
                "artifact": br.artifact,
                "page_url": br.page_url,
                "sample": br.rows[:2],
            }, ensure_ascii=False, indent=2))
            exit_code = 0 if br.rows else 6

            if args.headed and args.pause_seconds > 0:
                _log(f"==> 保留窗口 {args.pause_seconds}s")
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
