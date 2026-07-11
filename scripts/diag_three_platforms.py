#!/usr/bin/env python3
"""三平台运营同步一键诊断：HTTP 探活、API 读数/可选触发、DB 计数与最近 job。"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "backend" / "data" / "crosshub.db"
JAVA = "http://localhost:18080"
DEFAULT_ACCOUNT = "HangZhouYiTuo"
DEFAULT_PASSWORD = "HangZhouYiTuo"


def http(method: str, path: str, token: str = "", body: dict | None = None, timeout: int = 120):
    url = JAVA + path if path.startswith("/") else path
    payload = json.dumps(body or {}).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"raw": raw[:500]}
        return exc.code, data
    except Exception as exc:  # noqa: BLE001
        return -1, {"error": str(exc)}


def probe_url(url: str, timeout: int = 5) -> None:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            print(f"[HTTP] {url} -> {resp.status}")
    except Exception as exc:  # noqa: BLE001
        print(f"[HTTP] {url} -> ERR {exc}")


def login(account: str, password: str) -> str:
    code, body = http("POST", "/api/auth/login", body={
        "account": account,
        "password": password,
        "portalRole": "boss",
    })
    if code != 200:
        raise RuntimeError(f"login failed {code}: {body}")
    data = body.get("data") or body
    token = data.get("token") or data.get("access_token")
    if not token:
        raise RuntimeError(f"no token: {body}")
    return token


def table_exists(conn: sqlite3.Connection, name: str) -> bool:
    return conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone() is not None


def scalar(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> int:
    try:
        return int(conn.execute(sql, params).fetchone()[0])
    except sqlite3.Error:
        return -1


def db_counts(conn: sqlite3.Connection, tenant_id: int) -> dict[str, int]:
    counts: dict[str, int] = {}
    if table_exists(conn, "temu_shop"):
        counts["temu_shops"] = scalar(conn, "SELECT count(*) FROM temu_shop WHERE tenant_id=?", (tenant_id,))
    if table_exists(conn, "temu_sale"):
        counts["temu_sales"] = scalar(conn, "SELECT count(*) FROM temu_sale WHERE tenant_id=?", (tenant_id,))
    if table_exists(conn, "aliexpress_product"):
        counts["aliexpress_products"] = scalar(
            conn, "SELECT count(*) FROM aliexpress_product WHERE tenant_id=?", (tenant_id,)
        )
    counts["amazon_accounts"] = scalar(
        conn,
        "SELECT count(*) FROM platform_account WHERE tenant_id=? AND lower(platform)='amazon'",
        (tenant_id,),
    )
    counts["amazon_products"] = scalar(
        conn, "SELECT count(*) FROM amazon_product_snapshot WHERE tenant_id=?", (tenant_id,)
    )
    counts["amazon_metrics"] = scalar(
        conn, "SELECT count(*) FROM amazon_account_metric WHERE tenant_id=?", (tenant_id,)
    )
    return counts


def latest_jobs(conn: sqlite3.Connection, tenant_id: int, table: str, limit: int = 3) -> list[dict]:
    if not table_exists(conn, table):
        return []
    cols = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    err = "substr(coalesce(error_message,''),1,120)" if "error_message" in cols else "''"
    order_col = "created_at" if "created_at" in cols else "id"
    q = f"SELECT id, status, {err} AS err FROM {table} WHERE tenant_id=? ORDER BY {order_col} DESC LIMIT ?"
    try:
        return [dict(row) for row in map(dict, conn.execute(q, (tenant_id, limit)).fetchall())]
    except sqlite3.Error:
        return []


def poll_job(path: str, token: str, label: str, max_wait: int = 180) -> dict:
    deadline = time.time() + max_wait
    last = None
    while time.time() < deadline:
        _, body = http("GET", path, token=token, timeout=30)
        job = body.get("data") or body
        status = job.get("status")
        if status != last:
            print(f"  [{label}] status={status}")
            last = status
        if status in ("success", "partial", "failed", "completed"):
            return job
        time.sleep(3)
    return {"status": "timeout"}


def trigger_sync(token: str, platform: str, wait: bool) -> None:
    print(f"\n--- {platform.upper()} ---")
    if platform == "temu":
        code, body = http("POST", "/api/temu/crawl", token=token, body={})
        print("trigger", code)
        job = body.get("data") or body
        job_id = job.get("job_id") or job.get("id")
        if wait and job_id:
            result = poll_job(f"/api/temu/crawl/{job_id}", token, "temu")
            print("job", json.dumps({k: result.get(k) for k in ("status", "rows_count", "error_message")}, ensure_ascii=False))
    elif platform == "aliexpress":
        code, body = http("POST", "/api/aliexpress/crawl", token=token, body={"scope": "all"})
        print("trigger", code)
        job = body.get("data") or body
        job_id = job.get("job_id") or job.get("id")
        if wait and job_id:
            result = poll_job(f"/api/aliexpress/crawl/{job_id}", token, "aliexpress", 240)
            print("job", json.dumps({
                k: result.get(k) for k in (
                    "status", "rows_count", "orders_count", "violations_count", "error_message"
                )
            }, ensure_ascii=False))
    elif platform == "amazon":
        code, body = http("POST", "/api/amazon/sync", token=token, body={"scope": "account_health"})
        print("trigger", code)
        jobs = ((body.get("data") or body).get("jobs") or [])
        if wait and jobs:
            job_id = jobs[0].get("job_id")
            if job_id:
                result = poll_job(f"/api/amazon/sync/{job_id}", token, "amazon")
                print("job", json.dumps({k: result.get(k) for k in ("status", "error_message")}, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(description="三平台运营同步诊断")
    parser.add_argument("--account", default=DEFAULT_ACCOUNT)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--tenant-id", type=int, default=5)
    parser.add_argument("--trigger", choices=["temu", "aliexpress", "amazon", "all"], default="")
    parser.add_argument("--wait", action="store_true")
    args = parser.parse_args()

    print("=== 三平台链路诊断 ===")
    print("time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("tenant:", args.tenant_id, "account:", args.account)

    probe_url("http://localhost:5173/")
    probe_url("http://127.0.0.1:18765/health")
    code, _ = http("POST", "/api/auth/login", body={
        "account": args.account, "password": args.password, "portalRole": "boss",
    }, timeout=10)
    print(f"[HTTP] {JAVA}/api/auth/login -> {code}")

    if not DB.exists():
        print("[DB] missing:", DB)
        return 1

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    print("\n[DB] counts:", json.dumps(db_counts(conn, args.tenant_id), ensure_ascii=False))
    print("\n[DB] amazon accounts:")
    for row in conn.execute(
        """
        SELECT id, store_name, external_shop_id, integration_mode, bound_at
        FROM platform_account WHERE tenant_id=? AND lower(platform)='amazon'
        ORDER BY bound_at DESC
        """,
        (args.tenant_id,),
    ):
        print(dict(row))
    print("\n[DB] latest jobs:")
    for table in ("temu_crawl_job", "aliexpress_crawl_job", "amazon_sync_job"):
        print(f"  {table}:", latest_jobs(conn, args.tenant_id, table))

    token = login(args.account, args.password)
    print("\n[AUTH] login ok")

    if args.trigger == "all":
        for p in ("temu", "aliexpress", "amazon"):
            trigger_sync(token, p, args.wait)
    elif args.trigger:
        trigger_sync(token, args.trigger, args.wait)
    else:
        for path in ("/api/temu/operational", "/api/aliexpress/operational", "/api/amazon/daily", "/api/amazon/insights"):
            _, body = http("GET", path, token=token)
            data = body.get("data") or body
            if "daily" in path:
                print(path, "metrics", len(data.get("account_metrics") or []))
            elif "insights" in path:
                print(path, "products", len(data.get("products") or []))
            else:
                print(path, "products", len(data.get("products") or []))

    print("\n[DB] post-check:", json.dumps(db_counts(conn, args.tenant_id), ensure_ascii=False))
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
