import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "backend" / "data" / "crosshub.db"
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row
for row in c.execute(
    """
    SELECT id, status, started_at, finished_at, substr(payload_json,1,120) AS payload
    FROM agent_task
    WHERE task_type='amazon_sync' AND status IN ('pending','running')
    ORDER BY started_at DESC
    """
):
    print(dict(row))
for row in c.execute(
    """
    SELECT id, status, scope, started_at, finished_at
    FROM amazon_sync_job
    WHERE status IN ('pending','running')
    ORDER BY started_at DESC
    """
):
    print("job", dict(row))
