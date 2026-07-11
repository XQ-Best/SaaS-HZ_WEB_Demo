import json
import sqlite3
from pathlib import Path

task_id = "agt_b1506e15-9d07-4949-b906-cb9f48d43f83"
db = Path(__file__).resolve().parents[1] / "backend/data/crosshub.db"
row = sqlite3.connect(db).execute(
    "SELECT status, error_message, result_json FROM agent_task WHERE id=?",
    (task_id,),
).fetchone()
print("status:", row[0])
print("error:", row[1])
if row[2]:
    data = json.loads(row[2])
    print("keys:", list(data.keys()))
    print("page_diagnostics" in data, "result_summary" in data)
    prods = data.get("products") or []
    print(
        "products",
        len(prods),
        "ad=",
        sum(1 for p in prods if p.get("ad_spend_30d")),
        "inv=",
        sum(1 for p in prods if int(p.get("inventory") or 0) > 0),
        "orders=",
        len(data.get("outbound_orders") or []),
    )
    if data.get("result_summary"):
        print("summary:", data["result_summary"])
