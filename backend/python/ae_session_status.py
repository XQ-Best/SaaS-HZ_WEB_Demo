#!/usr/bin/env python3
"""检查 AliExpress 卖家后台登录态，并刷新 Cookie 快照。"""
from __future__ import annotations

import argparse
import json
import sys

from app.browser.ae_session import persist_ae_session, read_ae_cookie_snapshot, read_ae_session_cache
from app.browser.aliexpress_context import open_aliexpress_context
from app.config import AE_CSP_HOME, resolve_tenant_id


def main() -> None:
    parser = argparse.ArgumentParser(description="AliExpress 卖家后台会话状态")
    parser.add_argument("--tenant-id", type=int, help="租户 ID")
    parser.add_argument("--cache-only", action="store_true", help="仅读取本地缓存，不打开浏览器")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    try:
        tenant_id = resolve_tenant_id(args.tenant_id)
    except ValueError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        sys.exit(2)

    if args.cache_only:
        cached = read_ae_session_cache(tenant_id)
        snapshot = read_ae_cookie_snapshot(tenant_id)
        payload = cached or {
            "tenant_id": tenant_id,
            "logged_in": False,
            "ready": False,
            "message": "未检测到 AliExpress 登录缓存",
        }
        if snapshot:
            payload["snapshot_cookie_count"] = snapshot.get("cookie_count", 0)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False))
        else:
            print(payload)
        return

    with open_aliexpress_context(tenant_id, headless=True) as (_, context):
        page = context.new_page()
        page.goto(AE_CSP_HOME, wait_until="domcontentloaded", timeout=120_000)
        page.wait_for_timeout(3_000)
        payload = persist_ae_session(tenant_id, page, context)
        payload["message"] = (
            "AliExpress 卖家后台已就绪，可以同步数据。"
            if payload.get("logged_in")
            else "AliExpress 卖家后台未登录，请先运行 login_aliexpress.py"
        )

    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(payload)


if __name__ == "__main__":
    main()
