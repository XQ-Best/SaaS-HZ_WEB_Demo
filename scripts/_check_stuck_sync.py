import sqlite3
from pathlib import Path

db = Path(__file__).resolve().parents[1] / "backend/data/crosshub.db"
c = sqlite3.connect(db)
print("=== amazon_sync_job (latest 3) ===")
for row in c.execute(
    "SELECT id, status, scope, agent_task_id, created_at, error_message "
    "FROM amazon_sync_job ORDER BY created_at DESC LIMIT 3"
):
    print(row)
print("=== agent_task (latest 5 amazon) ===")
for row in c.execute(
    "SELECT id, status, task_type, created_at, error_message "
    "FROM agent_task WHERE task_type='amazon_sync' ORDER BY created_at DESC LIMIT 5"
):
    print(row)
