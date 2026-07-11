#!/usr/bin/env python3
"""Amazon 写回 E2E 探针：enqueue + 轮询 + 审计检查。"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "backend" / "data" / "crosshub.db"
JAVA = "http://localhost:18080"


def api(method: str, path: str, token: str = "", payload=None, timeout: int = 120):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(JAVA + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"raw": raw[:500]}


def login(account: str, password: str) -> str:
    _, res = api("POST", "/api/auth/login", payload={
        "account": account,
        "password": password,
        "portalRole": "boss",
    })
    token = (res.get("data") or res).get("token")
    if not token:
        raise RuntimeError(f"login failed: {res}")
    return token


def pick_item(conn: sqlite3.Connection, item_type: str, item_id: str | None) -> str | None:
    if item_id:
        row = conn.execute(
            "SELECT id FROM amazon_operational_item WHERE id=? AND item_type=?",
            (item_id, item_type),
        ).fetchone()
        return row[0] if row else None
    row = conn.execute(
        """
        SELECT id FROM amazon_operational_item
        WHERE item_type=? AND json_extract(payload_json, '$.status') = 'pending'
        ORDER BY synced_at DESC LIMIT 1
        """,
        (item_type,),
    ).fetchone()
    return row[0] if row else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Amazon write E2E probe")
    parser.add_argument("--tenant-id", type=int, default=5)
    parser.add_argument("--account", default="HangZhouYiTuo")
    parser.add_argument("--password", default="HangZhouYiTuo")
    parser.add_argument("--action", choices=("outbound_ship", "review_handle", "case_ack", "buyer_message_reply"), default="outbound_ship")
    parser.add_argument("--item-id", default="")
    parser.add_argument("--tracking-no", default="E2E-TEST-TRACK-001")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--wait-seconds", type=int, default=90)
    args = parser.parse_args()

    conn = sqlite3.connect(DB)
    item_type = {
        "outbound_ship": "outbound_order",
        "review_handle": "review",
        "case_ack": "case",
        "buyer_message_reply": "buyer_message",
    }[args.action]
    item_id = pick_item(conn, item_type, args.item_id or None)
    print("action:", args.action, "item:", item_id)
    if not item_id:
        print("No pending item found")
        return 1
    if args.dry_run:
        print("dry-run ok")
        return 0

    token = login(args.account, args.password)
    if args.action == "outbound_ship":
        code, res = api("PATCH", f"/api/amazon/outbound/{item_id}/ship", token, {"tracking_no": args.tracking_no})
    elif args.action == "review_handle":
        code, res = api("PATCH", f"/api/amazon/daily/reviews/{item_id}", token, {"note": "E2E regression"})
    elif args.action == "case_ack":
        code, res = api("PATCH", f"/api/amazon/daily/cases/{item_id}", token, {})
    else:
        code, res = api("PATCH", f"/api/amazon/daily/messages/{item_id}", token, {"template_id": "thanks", "note": "E2E regression"})

    print("enqueue:", code, json.dumps(res, ensure_ascii=False)[:600])
    if code >= 400:
        return 1

    job = res.get("data") or res
    jid = job.get("write_job_id") or job.get("writeJobId")
    if not jid:
        print("missing write_job_id")
        return 1

    deadline = time.time() + args.wait_seconds
    final_status = ""
    while time.time() < deadline:
        time.sleep(5)
        _, poll = api("GET", f"/api/amazon/write/{jid}", token)
        data = poll.get("data") or poll
        final_status = data.get("status") or ""
        print("poll:", final_status, data.get("error_code") or "")
        if final_status in ("success", "failed", "cancelled"):
            break

    _, audit = api("GET", "/api/amazon/write/audit", token, payload=None)
    audit_rows = audit.get("data") or audit
    print("audit rows:", len(audit_rows) if isinstance(audit_rows, list) else audit_rows)
    db_audit = conn.execute(
        "SELECT id, status, action, initiated_by_name FROM amazon_write_audit ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    print("latest db audit:", db_audit)
    conn.close()

    if final_status == "success":
        print("E2E OK")
        return 0
    if final_status == "failed":
        print("E2E pipeline OK, DOM/SC failed (check agent + captures)")
        return 0
    print("E2E timeout")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
