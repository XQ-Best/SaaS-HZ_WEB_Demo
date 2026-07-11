"""Trigger Amazon reports sync and print product metrics summary."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import requests

JAVA = "http://127.0.0.1:18080"
ACCOUNT = "HangZhouYiTuo"
PASSWORD = "HangZhouYiTuo"
SCOPE = sys.argv[1] if len(sys.argv) > 1 else "reports"


def login() -> str:
    res = requests.post(
        f"{JAVA}/api/auth/login",
        json={"account": ACCOUNT, "password": PASSWORD, "portalRole": "boss"},
        timeout=15,
    )
    res.raise_for_status()
    body = res.json()
    data = body.get("data") or body
    token = data.get("token") or data.get("access_token")
    if not token:
        raise RuntimeError(f"login failed: {body}")
    return token


def main() -> None:
    token = login()
    status = requests.get(
        f"{JAVA}/api/amazon/integration/status",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    ).json()
    print("integration:", json.dumps(status.get("data") or status, ensure_ascii=False)[:500])

    sync = requests.post(
        f"{JAVA}/api/amazon/sync",
        headers={"Authorization": f"Bearer {token}"},
        json={"scope": SCOPE},
        timeout=30,
    ).json()
    print("sync trigger:", json.dumps(sync, ensure_ascii=False)[:400])
    data = sync.get("data") or sync
    job_id = data.get("job_id") or data.get("id")
    if not job_id:
        jobs = data.get("jobs") or []
        if jobs:
            job_id = jobs[0].get("job_id") or jobs[0].get("id")
    if not job_id:
        print("no job_id in response")
        return

    for _ in range(100):
        time.sleep(3)
        job = requests.get(
            f"{JAVA}/api/amazon/sync/{job_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        ).json()
        data = job.get("data") or job
        status_text = data.get("status") or data.get("job_status")
        err = data.get("error_message") or data.get("error_code") or ""
        print("job:", status_text, err)
        if status_text in {"success", "failed", "error", "partial"}:
            break

    insights = requests.get(
        f"{JAVA}/api/amazon/insights",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    ).json()
    products = (insights.get("data") or insights).get("products") or []
    with_metrics = [
        p for p in products
        if (p.get("revenue7d") or p.get("revenue_30d") or p.get("orders7d") or p.get("orders_30d"))
    ]
    print(f"products={len(products)} with_metrics={len(with_metrics)}")
    for row in products[:5]:
        print(
            row.get("asin"),
            (row.get("productName") or row.get("product_name") or "")[:40],
            "rev=", row.get("revenue7d") or row.get("revenue_30d"),
            "ord=", row.get("orders7d") or row.get("orders_30d"),
            "ad=", row.get("adSpend7d") or row.get("ad_spend_30d"),
            "acos=", row.get("acos"),
        )


if __name__ == "__main__":
    main()
