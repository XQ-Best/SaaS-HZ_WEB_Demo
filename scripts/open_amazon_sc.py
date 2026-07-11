#!/usr/bin/env python3
"""在紫鸟已登录环境中打开 Amazon Seller Central 页面（窗口保持打开供人工查看）。"""
from __future__ import annotations

import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend" / "python"))

from app.ziniao.client import ZiniaoClient, ZiniaoConfig

from app.amazon.page_urls import OPEN_PAGE_URLS

PAGES = OPEN_PAGE_URLS


def load_browser_id() -> str:
    db = ROOT / "backend" / "data" / "crosshub.db"
    if db.exists():
        conn = sqlite3.connect(db)
        row = conn.execute(
            """
            SELECT external_shop_id FROM platform_account
            WHERE platform = 'amazon' AND external_shop_id != ''
            ORDER BY bound_at DESC LIMIT 1
            """
        ).fetchone()
        if row and row[0]:
            return str(row[0])
    return ""


def extract_debug_port(start_result: dict) -> int:
    for key in ("debuggingPort", "debugging_port", "debugPort"):
        value = start_result.get(key)
        if value is not None and str(value).strip().isdigit():
            return int(str(value).strip())
    for container in (start_result, start_result.get("data") or {}):
        if not isinstance(container, dict):
            continue
        for key, value in container.items():
            if "port" in str(key).lower() and str(value).strip().isdigit():
                return int(str(value).strip())
    raise RuntimeError(f"startBrowser 未返回 debuggingPort: {start_result!r}")


def main() -> int:
    page_key = (sys.argv[1] if len(sys.argv) > 1 else "inventory").strip().lower()
    url = PAGES.get(page_key, PAGES["inventory"])
    browser_id = load_browser_id()
    if not browser_id:
        print("未找到 Amazon 店铺的 external_shop_id（紫鸟 browserId）", file=sys.stderr)
        return 2

    ziniao = ZiniaoClient(ZiniaoConfig.from_env())
    print("==> 启动/连接紫鸟 WebDriver ...")
    ziniao.ensure_webdriver_client(wait_seconds=25)
    print(f"==> 打开店铺 browserId={browser_id}")
    start_result = ziniao.start_browser(browser_id=browser_id, headless=False)
    debug_port = extract_debug_port(start_result)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{debug_port}")
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()
        print(f"==> 导航: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=120000)
        time.sleep(3)
        print(f"==> 当前页面: {page.url}")
        print("==> 紫鸟浏览器窗口已打开，请在此窗口查看 Amazon 平台数据。")
        print("    关闭紫鸟店铺窗口即可结束（脚本不会自动 stopBrowser）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
