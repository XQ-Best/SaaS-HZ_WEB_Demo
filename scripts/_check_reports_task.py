import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "backend" / "data" / "crosshub.db"
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row
for jid in (
    "amz_sync_5ae096f7-922e-49dc-a715-4b7d2022425b",
    "amz_sync_65852c91-0e0a-4a0a-9f0a-000000000000",
):
    row = c.execute(
        "SELECT id, status, scope, finished_at, error_message FROM amazon_sync_job WHERE id LIKE ?",
        (jid.split("-")[0] + "%",),
    ).fetchone()
    if row:
        print("job", dict(row))

rows = c.execute(
    """
    SELECT id, status, finished_at, length(result_json) AS len
    FROM agent_task
    WHERE task_type='amazon_sync' AND payload_json LIKE '%reports%'
    ORDER BY finished_at DESC LIMIT 5
    """
).fetchall()
print("report tasks:", [dict(r) for r in rows])

task = c.execute(
    """
    SELECT result_json FROM agent_task
    WHERE task_type='amazon_sync' AND payload_json LIKE '%reports%'
    ORDER BY finished_at DESC LIMIT 1
    """
).fetchone()
if task and task[0]:
    import json
    data = json.loads(task[0])
    products = data.get("products") or []
    print("products in last reports task:", len(products))
    for p in products[:5]:
        print(
            p.get("asin"),
            p.get("revenue_30d"),
            p.get("orders_30d"),
            p.get("ad_spend_30d"),
            (p.get("product_name") or "")[:35],
        )
    print("capture:", data.get("capture_path"))
