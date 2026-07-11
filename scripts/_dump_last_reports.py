import json
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "backend" / "data" / "crosshub.db"
c = sqlite3.connect(DB)
raw = c.execute(
    "SELECT result_json FROM agent_task WHERE id='agt_e4cfbcd4-c668-4f5c-9aea-f1954fda15b1'"
).fetchone()[0]
data = json.loads(raw)
products = data.get("products") or []
print("products", len(products))
print("with rev", sum(1 for p in products if p.get("revenue_30d")))
print("with ad", sum(1 for p in products if p.get("ad_spend_30d")))
metrics = data.get("metrics") or []
print("metrics keys", [m.get("metric_key") for m in metrics if "ad" in str(m.get("metric_key", "")).lower()])
for p in products:
    if p.get("revenue_30d") or p.get("orders_30d") not in (None, "", "0", 0):
        print(p.get("asin"), p.get("revenue_30d"), p.get("orders_30d"), p.get("ad_spend_30d"), (p.get("product_name") or "")[:50])
