import json
import sqlite3
from pathlib import Path

c = sqlite3.connect(Path(__file__).resolve().parents[1] / "backend/data/crosshub.db")
row = c.execute(
    "SELECT result_json FROM agent_task WHERE id='agt_1cdc8c58-07e5-40f3-b99f-8117f087b9cc'"
).fetchone()
d = json.loads(row[0])
print("keys:", list(d.keys()))
for k in ("products", "outbound_orders", "buyer_messages", "reviews", "coupons", "shipments", "cases", "seller_news"):
    print(k, len(d.get(k) or []))
for m in d.get("metrics") or []:
    if "ad" in str(m.get("metric_key", "")).lower():
        print("metric", m)
prods = d.get("products") or []
print(
    "product fields:",
    "ad=", sum(1 for p in prods if p.get("ad_spend_30d")),
    "inv=", sum(1 for p in prods if int(p.get("inventory") or 0) > 0),
    "pv=", sum(1 for p in prods if int(p.get("page_views") or 0) > 0),
    "conv=", sum(1 for p in prods if p.get("conversion_rate")),
)
