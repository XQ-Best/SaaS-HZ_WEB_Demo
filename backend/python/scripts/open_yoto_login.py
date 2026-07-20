#!/usr/bin/env python3
"""打开紫鸟 YOTO 店铺 headed 窗口，停在 Seller Central 首页供人工登录。"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend" / "python"))

from app.amazon.page_urls import HOME_URL
from app.amazon.session_context import extract_debug_port
from app.ziniao.client import ZiniaoClient, ZiniaoConfig

BROWSER_ID = "16505337258263"
STORE = "YOTO美国账号"


def main() -> int:
    ziniao = ZiniaoClient(ZiniaoConfig.from_env())
    print("==> 连接紫鸟 WebDriver ...", flush=True)
    ziniao.ensure_webdriver_client(wait_seconds=25)
    print(f"==> 打开店铺 {STORE} browserId={BROWSER_ID}", flush=True)
    start = ziniao.start_browser(browser_id=BROWSER_ID, headless=False)
    port = extract_debug_port(start)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.bring_to_front()
        print(f"==> 导航: {HOME_URL}", flush=True)
        page.goto(HOME_URL, wait_until="domcontentloaded", timeout=120_000)
        time.sleep(2)
        print(f"==> 当前: {page.url}", flush=True)
        print("==> 请在紫鸟窗口完成 Seller Central 登录，完成后回到聊天告知。", flush=True)
        print("    （窗口保持打开，勿关闭此 PowerShell 进程）", flush=True)
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("==> 已结束等待。", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
