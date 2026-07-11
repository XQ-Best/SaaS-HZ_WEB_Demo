"""离线重放上次 Agent 结果，验证缺口闭合逻辑（不触发浏览器）。"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend" / "python"))

from app.amazon.composer.metrics_merger import coalesce_ads_summary
from app.amazon.composer.product_composer import (
    allocate_account_ads_by_revenue,
    cap_suspicious_order_metrics,
    enrich_product_rows,
)


def field_coverage(products: list[dict]) -> dict[str, int]:
    total = len(products)
    keys = ("ad_spend_30d", "inventory", "page_views", "conversion_rate", "acos")
    out: dict[str, int] = {}
    for key in keys:
        if key == "inventory":
            out[key] = sum(1 for p in products if int(p.get(key) or 0) > 0)
        elif key == "conversion_rate":
            out[key] = sum(1 for p in products if p.get(key) not in (None, "", 0, 0.0))
        else:
            out[key] = sum(1 for p in products if str(p.get(key) or "").strip() not in ("", "0", "0.0"))
    out["_total"] = total
    return out


def main() -> None:
    task_id = sys.argv[1] if len(sys.argv) > 1 else "agt_1cdc8c58-07e5-40f3-b99f-8117f087b9cc"
    db = ROOT / "backend/data/crosshub.db"
    row = sqlite3.connect(db).execute(
        "SELECT result_json FROM agent_task WHERE id=?",
        (task_id,),
    ).fetchone()
    if not row:
        print(f"task not found: {task_id}")
        sys.exit(1)
    payload = json.loads(row[0])
    products = [dict(p) for p in payload.get("products") or []]
    metrics = payload.get("metrics") or []

    print("BEFORE", field_coverage(products))
    products = cap_suspicious_order_metrics(products)
    summary = coalesce_ads_summary({}, metrics)
    products = allocate_account_ads_by_revenue(products, summary)
    products = enrich_product_rows(products)
    print("AFTER ", field_coverage(products))
    print("ads_summary", summary)
    for row in products[:5]:
        print(
            row.get("asin"),
            "ord=", row.get("orders_30d"),
            "rev=", row.get("revenue_30d"),
            "ad=", row.get("ad_spend_30d"),
            "acos=", row.get("acos"),
        )


if __name__ == "__main__":
    main()
