#!/usr/bin/env python3
"""逐层测绘 Seller Central：顶栏/侧栏链接 + 关键页 URL + 报表 XHR 抓包。

产出：backend/data/amazon-discovery/sitemap-<ts>.json
      backend/data/amazon-discovery/network-<ts>.jsonl

用法（需紫鸟 YOTO 已登录）：
  cd backend/python
  $env:PYTHONPATH=(Get-Location)
  py scripts/discover_amazon_sc.py --headed --browser-id 16505337258263
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from app.amazon.navigation_guard import (
    assert_allowed_url,
    attach_network_logger,
    collect_nav_links,
    is_blocked_url,
    navigate_to_br_child_asin,
)
from app.amazon.page_urls import HOME_URL, INVENTORY_URLS, ORDER_LIST_SPECS, REPORT_URLS
from app.amazon.session_context import extract_debug_port, looks_logged_in, require_seller_logged_in
from app.ziniao.client import ZiniaoClient, ZiniaoConfig

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "amazon-discovery"


def _log(msg: str) -> None:
    print(msg, flush=True)


def _probe_url(page, url: str, *, label: str) -> dict:
    entry = {"label": label, "requested": url, "final": "", "title": "", "blocked": False, "error": ""}
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=90_000)
        page.wait_for_timeout(4000)
        entry["final"] = page.url
        entry["title"] = page.title()
        if is_blocked_url(page.url):
            entry["blocked"] = True
            entry["error"] = "BLOCKED_URL"
        else:
            assert_allowed_url(page.url, context=label)
    except Exception as exc:
        entry["error"] = str(exc)
        entry["final"] = page.url
    return entry


def main() -> int:
    parser = argparse.ArgumentParser(description="Amazon SC 站点测绘 + 抓包")
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--browser-id", default="")
    parser.add_argument("--browser-oauth", default="")
    parser.add_argument("--pause-seconds", type=int, default=10)
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = int(time.time())
    net_log = OUT_DIR / f"network-{ts}.jsonl"
    if net_log.exists():
        net_log.unlink()

    ziniao = ZiniaoClient(ZiniaoConfig.from_env())
    ziniao.ensure_webdriver_client(wait_seconds=20)
    start = ziniao.start_browser(
        browser_id=args.browser_id or None,
        browser_oauth=args.browser_oauth or None,
        headless=not args.headed,
    )
    port = extract_debug_port(start)

    from playwright.sync_api import sync_playwright

    sitemap: dict = {"captured_at": ts, "pages": [], "nav_links": [], "br_sidebar_href": ""}

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            ctx = browser.contexts[0] if browser.contexts else browser.new_context()
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            attach_network_logger(page, str(net_log))

            page.goto(HOME_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            body = page.inner_text("body")
            require_seller_logged_in(page, body, store_name="discover")
            sitemap["nav_links"] = collect_nav_links(page)
            sitemap["pages"].append(_probe_url(page, HOME_URL, label="home"))

            # 订单 hub（侧栏「订单」类入口的真实 URL）
            sitemap["pages"].append(_probe_url(page, ORDER_LIST_SPECS[0]["url"], label="orders_hub"))

            # BR：先直连配置 URL，再试侧栏
            for i, url in enumerate(REPORT_URLS[:2]):
                sitemap["pages"].append(_probe_url(page, url, label=f"br_direct_{i}"))

            page.goto(HOME_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
            try:
                final = navigate_to_br_child_asin(page, home_url=HOME_URL)
                sitemap["br_sidebar_href"] = final
                page.wait_for_timeout(3000)
                sitemap["pages"].append({
                    "label": "br_via_sidebar",
                    "requested": "navigate_to_br_child_asin",
                    "final": page.url,
                    "title": page.title(),
                    "blocked": is_blocked_url(page.url),
                    "error": "BLOCKED_URL" if is_blocked_url(page.url) else "",
                })
            except RuntimeError as exc:
                sitemap["pages"].append({
                    "label": "br_via_sidebar",
                    "requested": "navigate_to_br_child_asin",
                    "final": page.url,
                    "title": page.title(),
                    "blocked": is_blocked_url(page.url),
                    "error": str(exc),
                })

            sitemap["pages"].append(_probe_url(page, INVENTORY_URLS[0], label="inventory"))

            out = OUT_DIR / f"sitemap-{ts}.json"
            out.write_text(json.dumps(sitemap, ensure_ascii=False, indent=2), encoding="utf-8")
            _log(f"==> sitemap: {out}")
            _log(f"==> network log: {net_log}")

            blocked = [p for p in sitemap["pages"] if p.get("blocked")]
            if blocked:
                _log("==> 警告：以下探测落入禁止页（如 sellermobileapp）:")
                for p in blocked:
                    _log(f"    {p['label']}: {p['final']}")

            if args.headed and args.pause_seconds > 0:
                _log(f"==> 保留窗口 {args.pause_seconds}s")
                page.wait_for_timeout(args.pause_seconds * 1000)
            browser.close()
    finally:
        try:
            ziniao.stop_browser(browser_id=args.browser_id or None, browser_oauth=args.browser_oauth or None)
        except Exception:
            pass

    return 1 if any(p.get("blocked") for p in sitemap.get("pages", [])) else 0


if __name__ == "__main__":
    raise SystemExit(main())
