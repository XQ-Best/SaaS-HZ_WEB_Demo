#!/usr/bin/env python3
"""Amazon V2 爬取重写 — 自动化回归（单元 + API + DB + 可选 live sync）。"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "backend" / "data" / "crosshub.db"
JAVA = "http://127.0.0.1:18080"
ACCOUNT = "HangZhouYiTuo"
PASSWORD = "HangZhouYiTuo"
TENANT_ID = 5


@dataclass
class Case:
    case_id: str
    name: str
    ok: bool
    detail: str = ""


@dataclass
class Report:
    cases: list[Case] = field(default_factory=list)

    def add(self, case_id: str, name: str, ok: bool, detail: str = "") -> None:
        self.cases.append(Case(case_id, name, ok, detail))

    def print_summary(self) -> int:
        passed = [c for c in self.cases if c.ok]
        failed = [c for c in self.cases if not c.ok]
        print("\n=== Amazon V2 Regression Summary ===")
        for item in self.cases:
            mark = "PASS" if item.ok else "FAIL"
            line = f"[{mark}] {item.case_id} {item.name}"
            if item.detail:
                line += f" — {item.detail}"
            print(line)
        print(f"\nTotal {len(self.cases)} | PASS {len(passed)} | FAIL {len(failed)}")
        return 0 if not failed else 1


def http_json(method: str, url: str, *, token: str = "", payload: dict | None = None, timeout: int = 20):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body) if body else {}
        except json.JSONDecodeError:
            parsed = {"raw": body}
        return exc.code, parsed
    except Exception as exc:  # noqa: BLE001
        return -1, {"error": str(exc)}


def login() -> str:
    code, body = http_json(
        "POST",
        f"{JAVA}/api/auth/login",
        payload={"account": ACCOUNT, "password": PASSWORD, "portalRole": "boss"},
    )
    if code != 200:
        raise RuntimeError(f"login HTTP {code}: {body}")
    data = body.get("data") or body
    token = data.get("token") or data.get("access_token")
    if not token:
        raise RuntimeError(f"login missing token: {body}")
    return token


def run_unit_tests(report: Report) -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "backend" / "python" / "tests" / "test_amazon_parsers.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    report.add(
        "UT-01",
        "parser + pipeline unit tests",
        proc.returncode == 0,
        (proc.stdout or proc.stderr).strip()[:200],
    )


def run_service_checks(report: Report) -> None:
    for case_id, name, url in (
        ("ENV-01", "Vue dev :5173", "http://localhost:5173/"),
        ("ENV-02", "Agent health :18765", "http://127.0.0.1:18765/health"),
    ):
        try:
            with urllib.request.urlopen(url, timeout=8) as resp:
                report.add(case_id, name, resp.status == 200, f"HTTP {resp.status}")
        except Exception as exc:  # noqa: BLE001
            report.add(case_id, name, False, str(exc))

    try:
        import socket

        ziniao_open = False
        for host, port in (("127.0.0.1", 16851), ("127.0.0.1", 18080)):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            ok = sock.connect_ex((host, port)) == 0
            sock.close()
            if port == 16851:
                ziniao_open = ok
            if port == 18080:
                report.add("ENV-03", "Java API :18080", ok, "listening" if ok else "down")
        report.add("ENV-04", "Ziniao WebDriver :16851", ziniao_open, "required for live crawl")
    except Exception as exc:  # noqa: BLE001
        report.add("ENV-04", "Ziniao WebDriver :16851", False, str(exc))


def run_hard_api_regression(report: Report, token: str) -> None:
    checks = [
        ("HR-01", "GET /api/auth/session", "GET", f"{JAVA}/api/auth/session", None, (200,)),
        ("HR-02", "GET /api/platform-accounts?platform=temu", "GET", f"{JAVA}/api/platform-accounts?platform=temu", None, (200,)),
        ("HR-05", "GET /api/warehouse/orders", "GET", f"{JAVA}/api/warehouse/orders", None, (200,)),
        ("AMZ-R20", "GET /api/amazon/insights", "GET", f"{JAVA}/api/amazon/insights", None, (200,)),
        ("AMZ-R10", "GET /api/amazon/daily", "GET", f"{JAVA}/api/amazon/daily", None, (200,)),
        ("AMZ-R02", "GET /api/amazon/integration/status", "GET", f"{JAVA}/api/amazon/integration/status", None, (200,)),
    ]
    for case_id, name, method, url, payload, ok_codes in checks:
        code, body = http_json(method, url, token=token, payload=payload)
        report.add(case_id, name, code in ok_codes, f"HTTP {code}")


def run_db_regression(report: Report) -> None:
    if not DB.exists():
        report.add("DB-00", "crosshub.db exists", False, str(DB))
        return
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    amazon_accounts = conn.execute(
        """
        SELECT COUNT(*) AS c FROM platform_account
        WHERE lower(platform)='amazon' AND trim(coalesce(external_shop_id,'')) != ''
        """
    ).fetchone()["c"]
    report.add("AMZ-R02", "amazon account bound with external_shop_id", amazon_accounts >= 1, f"count={amazon_accounts}")

    demo_rows = conn.execute(
        """
        SELECT COUNT(*) AS c FROM amazon_product_snapshot
        WHERE lower(coalesce(asin,'')) LIKE 'demo_%'
        """
    ).fetchone()["c"]
    report.add("DC-01", "no demo_asin in product_snapshot", demo_rows == 0, f"demo_rows={demo_rows}")

    cols = {row[1] for row in conn.execute("PRAGMA table_info(amazon_product_snapshot)")}
    for col in ("tacos", "conversion_rate", "period_days"):
        report.add(f"DB-V12-{col}", f"column amazon_product_snapshot.{col}", col in cols, "present" if col in cols else "missing")

    pa_cols = {row[1] for row in conn.execute("PRAGMA table_info(platform_account)")}
    report.add("DB-V12-merchant", "column platform_account.amazon_merchant_id", "amazon_merchant_id" in pa_cols)

    metrics = conn.execute(
        """
        SELECT COUNT(*) AS total,
               SUM(CASE WHEN trim(coalesce(revenue_30d,'')) != '' THEN 1 ELSE 0 END) AS with_rev,
               SUM(CASE WHEN orders_30d > 0 THEN 1 ELSE 0 END) AS with_orders,
               SUM(CASE WHEN trim(coalesce(ad_spend_30d,'')) != '' THEN 1 ELSE 0 END) AS with_ads
        FROM amazon_product_snapshot WHERE tenant_id = ?
        """,
        (TENANT_ID,),
    ).fetchone()
    report.add(
        "AMZ-R21",
        "product_snapshot has rows",
        metrics["total"] >= 1,
        f"total={metrics['total']} revenue={metrics['with_rev']} orders={metrics['with_orders']} ads={metrics['with_ads']}",
    )

    orders = conn.execute(
        "SELECT COUNT(*) AS c FROM amazon_operational_item WHERE item_type='outbound_order'"
    ).fetchone()["c"]
    report.add("AMZ-R22", "outbound_orders persisted", orders >= 1, f"count={orders}")

    latest_reports = conn.execute(
        """
        SELECT status, result_summary FROM amazon_sync_job
        WHERE scope='reports' ORDER BY finished_at DESC LIMIT 1
        """
    ).fetchone()
    if latest_reports:
        summary = {}
        try:
            summary = json.loads(latest_reports["result_summary"] or "{}")
        except json.JSONDecodeError:
            pass
        has_diag = "page_diagnostics" in summary or any(
            key in summary for key in ("pages_ok", "orders_count", "merchant_id")
        )
        report.add(
            "V2-01",
            "latest reports job result_summary enriched",
            latest_reports["status"] == "success" or has_diag,
            f"status={latest_reports['status']} keys={list(summary.keys())[:6]}",
        )


def optional_live_sync(report: Report, token: str) -> None:
    if "--live" not in sys.argv:
        report.add("LIVE-00", "live reports sync", True, "skipped (pass --live to run)")
        return

    code, body = http_json(
        "POST",
        f"{JAVA}/api/amazon/sync",
        token=token,
        payload={"scope": "reports"},
    )
    data = body.get("data") or body
    job_id = data.get("job_id") or data.get("id")
    if code not in (200, 202) or not job_id:
        report.add("LIVE-01", "trigger reports sync", False, f"HTTP {code} {body}")
        return

    final_status = "timeout"
    summary: dict = {}
    error = ""
    for _ in range(120):
        time.sleep(3)
        _, job = http_json("GET", f"{JAVA}/api/amazon/sync/{job_id}", token=token)
        payload = job.get("data") or job
        final_status = str(payload.get("status") or "")
        error = str(payload.get("error_message") or "")
        summary = payload.get("result_summary") or {}
        if final_status in {"success", "failed", "partial", "error"}:
            break

    report.add(
        "LIVE-01",
        "reports sync completed",
        final_status in {"success", "partial"},
        f"status={final_status} err={error[:120]}",
    )
    diagnostics = summary.get("page_diagnostics") or []
    report.add(
        "V2-02",
        "page_diagnostics present",
        isinstance(diagnostics, list) and len(diagnostics) >= 3,
        f"pages={len(diagnostics)}",
    )
    report.add(
        "V2-03",
        "orders_count in result_summary",
        int(summary.get("orders_count") or 0) >= 0 and "orders_count" in summary,
        str(summary.get("orders_count")),
    )


def main() -> int:
    report = Report()
    run_unit_tests(report)
    run_service_checks(report)

    token = ""
    try:
        token = login()
        report.add("AUTH-01", "boss login", True)
    except Exception as exc:  # noqa: BLE001
        report.add("AUTH-01", "boss login", False, str(exc))

    if token:
        run_hard_api_regression(report, token)
        optional_live_sync(report, token)

    run_db_regression(report)
    return report.print_summary()


if __name__ == "__main__":
    raise SystemExit(main())
