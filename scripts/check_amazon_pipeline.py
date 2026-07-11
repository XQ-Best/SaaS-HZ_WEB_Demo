#!/usr/bin/env python3
"""Amazon V2 爬取管道诊断（读最近一次 sync job 与 DB 指标）。"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "backend" / "data" / "crosshub.db"


def main() -> int:
    if not DB.exists():
        print(f"数据库不存在: {DB}", file=sys.stderr)
        return 2

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    job = conn.execute(
        """
        SELECT id, scope, status, result_summary, error_message, finished_at
        FROM amazon_sync_job
        ORDER BY created_at DESC
        LIMIT 1
        """
    ).fetchone()
    if not job:
        print("无 amazon_sync_job 记录")
        return 0

    print(f"==> 最近任务: {job['id']} scope={job['scope']} status={job['status']}")
    if job["error_message"]:
        print(f"    error: {job['error_message']}")
    summary = {}
    try:
        summary = json.loads(job["result_summary"] or "{}")
    except json.JSONDecodeError:
        pass
    if summary:
        print(f"    summary: {json.dumps(summary, ensure_ascii=False)}")

    metrics = conn.execute(
        """
        SELECT COUNT(*) AS total,
               SUM(CASE WHEN revenue_30d != '' AND revenue_30d != '0' THEN 1 ELSE 0 END) AS with_revenue,
               SUM(CASE WHEN orders_30d > 0 THEN 1 ELSE 0 END) AS with_orders,
               SUM(CASE WHEN ad_spend_30d != '' AND ad_spend_30d != '0' THEN 1 ELSE 0 END) AS with_ads,
               SUM(CASE WHEN conversion_rate > 0 THEN 1 ELSE 0 END) AS with_conversion
        FROM amazon_product_snapshot
        """
    ).fetchone()
    print(
        f"==> product_snapshot: total={metrics['total']} "
        f"revenue={metrics['with_revenue']} orders={metrics['with_orders']} "
        f"ads={metrics['with_ads']} conversion={metrics['with_conversion']}"
    )

    orders = conn.execute(
        """
        SELECT COUNT(*) AS total FROM amazon_operational_item
        WHERE item_type = 'outbound_order'
        """
    ).fetchone()
    print(f"==> outbound_orders: {orders['total']}")

    merchant = conn.execute(
        """
        SELECT store_name, amazon_merchant_id FROM platform_account
        WHERE platform = 'amazon' AND amazon_merchant_id != ''
        LIMIT 3
        """
    ).fetchall()
    if merchant:
        for row in merchant:
            print(f"==> merchant_id cache: {row['store_name']} -> {row['amazon_merchant_id']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
