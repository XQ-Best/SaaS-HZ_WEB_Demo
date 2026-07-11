import json
import sqlite3
import sys
from pathlib import Path

task_id = sys.argv[1] if len(sys.argv) > 1 else "agt_db60c3b6-5669-420e-98b1-78ac82c07024"
db = Path(__file__).resolve().parents[1] / "backend/data/crosshub.db"
row = sqlite3.connect(db).execute(
    "SELECT status, error_message, result_json FROM agent_task WHERE id=?",
    (task_id,),
).fetchone()
print("status:", row[0])
print("error:", row[1] or "")
if row[2]:
    data = json.loads(row[2])
    print("v2:", "page_diagnostics" in data, "result_summary" in data)
    prods = data.get("products") or []
    orders = data.get("outbound_orders") or []
    print(
        "products", len(prods),
        "ad", sum(1 for p in prods if str(p.get("ad_spend_30d") or "").strip()),
        "inv", sum(1 for p in prods if int(p.get("inventory") or 0) > 0),
        "pv", sum(1 for p in prods if int(p.get("page_views") or 0) > 0),
        "orders", len(orders),
        "cases", len(data.get("cases") or []),
    )
    if data.get("result_summary"):
        print("summary:", json.dumps(data["result_summary"], ensure_ascii=False)[:400])
    if data.get("page_diagnostics"):
        for d in data["page_diagnostics"][:8]:
            print("diag:", d.get("page_key"), d.get("row_count"), d.get("warning_code"))
    for p in prods[:4]:
        print(p.get("asin"), "ord=", p.get("orders_30d"), "ad=", p.get("ad_spend_30d"), "inv=", p.get("inventory"))
