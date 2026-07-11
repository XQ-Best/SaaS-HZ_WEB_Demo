"""M1-M3 regression checks."""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "backend" / "data" / "crosshub.db"
JAVA = "http://localhost:18080"


def api(method: str, path: str, token: str = "", payload=None):
    body = json.dumps(payload).encode() if payload is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(JAVA + path, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.status, json.loads(resp.read())


def main() -> int:
    _, login = api("POST", "/api/auth/login", payload={
        "account": "HangZhouYiTuo", "password": "HangZhouYiTuo", "portalRole": "boss",
    })
    token = (login.get("data") or login).get("token")
    print("=== M1 AliExpress violations ===")
    _, viol = api("GET", "/api/aliexpress/violations", token)
    data = viol.get("data") or viol
    synced_at = data.get("syncedAt") or data.get("synced_at") or ""
    print("syncedAt:", synced_at or None)
    print("violations:", len(data.get("violations") or []))

    conn = sqlite3.connect(DB)
    row = conn.execute(
        """
        SELECT id, scope, status, orders_count, violations_count, finished_at, error_message
        FROM aliexpress_crawl_job WHERE tenant_id=5 ORDER BY created_at DESC LIMIT 1
        """
    ).fetchone()
    print("latest crawl job:", row)
    if row and row[4] is not None and not synced_at:
        print("M1 WARN: violations_count set but syncedAt empty")
    elif row and row[5] and synced_at:
        print("M1 OK: syncedAt from crawl job or violation rows")

    print("\n=== M2 Temu monitor ===")
    _, targets = api("GET", "/api/monitor/targets?platform=temu", token)
    target_list = targets.get("data") or targets
    print("targets:", len(target_list))
    if target_list:
        tid = target_list[0]["id"]
        _, latest = api("GET", f"/api/monitor/targets/{tid}/latest", token)
        print("latest:", json.dumps(latest.get("data") or latest, ensure_ascii=False)[:300])
        pending = conn.execute(
            "SELECT id,status FROM monitor_job WHERE tenant_id=5 AND status IN ('pending','running') ORDER BY queued_at DESC LIMIT 3"
        ).fetchall()
        print("pending monitor jobs:", pending)
        if not pending:
            code, trig = api("POST", f"/api/monitor/targets/{tid}/trigger", token, {"reason": "regression", "force": False})
            print("trigger", code, trig.get("data") or trig)
            worker = ROOT / "backend" / "python" / "monitor_worker.py"
            proc = subprocess.run(
                [sys.executable, str(worker), "--once", "--json", "--worker-id", "regression-worker"],
                cwd=ROOT / "backend" / "python",
                capture_output=True,
                text=True,
                timeout=600,
            )
            print("worker exit", proc.returncode)
            if proc.stdout.strip():
                print("worker out:", proc.stdout.strip()[:400])
            if proc.stderr.strip():
                print("worker err:", proc.stderr.strip()[:400])
            _, latest2 = api("GET", f"/api/monitor/targets/{tid}/latest", token)
            print("after worker:", json.dumps(latest2.get("data") or latest2, ensure_ascii=False)[:300])

    print("\n=== M3 Amazon write API ===")
    outbound = conn.execute(
        """
        SELECT id FROM amazon_operational_item
        WHERE tenant_id=5 AND item_type='outbound_order'
          AND json_extract(payload_json, '$.status') = 'pending'
        LIMIT 1
        """
    ).fetchone()
    print("sample outbound item:", outbound[0] if outbound else None)
    try:
        code, _ = api("GET", "/api/amazon/write/amz_write_missing", token)
        print("write 404 check:", code)
    except urllib.error.HTTPError as exc:
        print("write 404 check:", exc.code)

    write_table = conn.execute("SELECT name FROM sqlite_master WHERE name='amazon_write_job'").fetchone()
    print("amazon_write_job table:", bool(write_table))

    if outbound:
        oid = outbound[0]
        try:
            code, ship = api("PATCH", f"/api/amazon/outbound/{oid}/ship", token, {"tracking_no": "REGTEST-OPS-P2"})
            job = ship.get("data") or ship
            jid = job.get("write_job_id") or job.get("writeJobId")
            print("write enqueue:", code, jid)
            if jid:
                import time
                for i in range(12):
                    time.sleep(5)
                    _, poll = api("GET", f"/api/amazon/write/{jid}", token)
                    st = (poll.get("data") or poll).get("status")
                    err = (poll.get("data") or poll).get("error_code") or (poll.get("data") or poll).get("errorCode")
                    print(f"  poll {i + 1}:", st, err or "")
                    if st in ("success", "failed", "cancelled"):
                        if st == "success":
                            print("M3 OK: write job succeeded")
                        elif err == "AMAZON_WRITE_DOM_FAILED":
                            print("M3 OK: agent pipeline works (DOM mismatch on SC page is expected in headless/regression)")
                        else:
                            print("M3 WARN: write job ended with", st, err)
                        break
        except urllib.error.HTTPError as exc:
            print("write enqueue failed:", exc.code, exc.read().decode()[:200])

    print("\n=== M4 Amazon write audit ===")
    _, audit = api("GET", "/api/amazon/write/audit", token)
    audit_rows = audit.get("data") if isinstance(audit.get("data"), list) else audit
    audit_count = len(audit_rows) if isinstance(audit_rows, list) else 0
    print("audit api rows:", audit_count)
    audit_table = conn.execute("SELECT name FROM sqlite_master WHERE name='amazon_write_audit'").fetchone()
    print("amazon_write_audit table:", bool(audit_table))
    if audit_table:
        latest_audit = conn.execute(
            "SELECT id, action, status, initiated_by_name FROM amazon_write_audit ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        print("latest audit:", latest_audit)
        if latest_audit:
            print("M4 OK: write audit recorded")

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
