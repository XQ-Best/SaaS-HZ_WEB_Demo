import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "backend" / "data" / "crosshub.db"
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row
rows = c.execute(
    "SELECT id, tenant_id, name, substr(token,1,20) AS token_prefix, last_heartbeat_at FROM integration_agent ORDER BY last_heartbeat_at DESC LIMIT 5"
).fetchall()
for row in rows:
    print(dict(row))
