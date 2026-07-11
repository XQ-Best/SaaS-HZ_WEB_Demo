import json
import sqlite3
from pathlib import Path

c = sqlite3.connect(Path(__file__).resolve().parents[1] / "backend/data/crosshub.db")
c.row_factory = sqlite3.Row
row = c.execute(
    """
    SELECT j.scope, j.finished_at, t.result_json
    FROM amazon_sync_job j
    JOIN agent_task t ON j.agent_task_id = t.id
    WHERE j.scope = 'daily' AND j.status = 'success'
    ORDER BY j.finished_at DESC
    LIMIT 1
    """
).fetchone()
if not row:
    print("no daily success")
    raise SystemExit(0)
d = json.loads(row["result_json"] or "{}")
print("daily @", row["finished_at"])
for k in ("buyer_messages", "reviews", "coupons", "seller_news", "shipments", "cases", "products"):
    print(f"  {k}: {len(d.get(k) or [])}")
