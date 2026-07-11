import json
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "backend" / "data" / "crosshub.db"
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row
row = c.execute(
    """
    SELECT COUNT(*) AS total,
           SUM(CASE WHEN trim(revenue_30d) != '' THEN 1 ELSE 0 END) AS with_rev,
           SUM(CASE WHEN orders_30d > 0 THEN 1 ELSE 0 END) AS with_orders
    FROM amazon_product_snapshot WHERE tenant_id = 5
    """
).fetchone()
print(dict(row))
rows = c.execute(
    """
    SELECT asin, substr(product_name,1,35) AS name, revenue_30d, orders_30d
    FROM amazon_product_snapshot WHERE tenant_id = 5
    ORDER BY CASE WHEN trim(revenue_30d) = '' THEN 0 ELSE 1 END DESC,
             CAST(REPLACE(REPLACE(revenue_30d, ',', ''), ' ', '') AS REAL) DESC,
             orders_30d DESC
    """
).fetchall()
for r in rows:
    print(dict(r))
