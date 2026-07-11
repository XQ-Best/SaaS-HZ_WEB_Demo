import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "backend" / "data" / "crosshub.db"
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row
tenant = 5
row = c.execute(
    """
    SELECT COUNT(*) AS total,
           SUM(CASE WHEN revenue_30d IS NOT NULL AND trim(revenue_30d) != '' THEN 1 ELSE 0 END) AS with_rev,
           SUM(CASE WHEN orders_30d > 0 THEN 1 ELSE 0 END) AS with_orders,
           SUM(CASE WHEN ad_spend_30d IS NOT NULL AND trim(ad_spend_30d) != '' THEN 1 ELSE 0 END) AS with_ads
    FROM amazon_product_snapshot WHERE tenant_id = ?
    """,
    (tenant,),
).fetchone()
print("metrics:", dict(row))
jobs = c.execute(
    "SELECT scope, status, finished_at FROM amazon_sync_job WHERE tenant_id = ? ORDER BY finished_at DESC LIMIT 8",
    (tenant,),
).fetchall()
print("jobs:", [dict(j) for j in jobs])
sample = c.execute(
    """
    SELECT asin, substr(product_name,1,40) AS name, revenue_30d, orders_30d, ad_spend_30d, acos
    FROM amazon_product_snapshot WHERE tenant_id = ? AND trim(product_name) NOT LIKE 'US$%'
    LIMIT 8
    """,
    (tenant,),
).fetchall()
print("sample:", [dict(s) for s in sample])

job = c.execute(
    "SELECT id, status, scope, finished_at, error_message FROM amazon_sync_job ORDER BY finished_at DESC LIMIT 3"
).fetchall()
print("latest jobs:", [dict(j) for j in job])

task = c.execute(
    """
    SELECT id, status, finished_at, substr(result_json, 1, 1200) AS preview
    FROM agent_task WHERE task_type='amazon_sync' ORDER BY finished_at DESC LIMIT 1
    """
).fetchone()
if task:
    print("latest task:", dict(task))
