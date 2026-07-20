"""同步结果 data_quality 汇总。"""
from __future__ import annotations

from typing import Any

from app.amazon.sources.amazon_sync_config import report_period_days


def build_data_quality(
    *,
    scope: str,
    products: list[dict[str, Any]],
    br_count: int,
    inv_count: int,
    ads_count: int,
    diagnostics: list[dict[str, Any]],
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    period = report_period_days() if scope == "reports" else 30
    br_source = next(
        (str(p.get("key") or "") for p in diagnostics if str(p.get("key", "")).startswith("br_")),
        "",
    )
    inv_source = next(
        (str(p.get("key") or "") for p in diagnostics if str(p.get("key", "")).startswith("inv")),
        "",
    )
    ads_source = next(
        (str(p.get("key") or "") for p in diagnostics if str(p.get("key", "")).startswith("ads")),
        "",
    )
    quality_warnings = list(warnings or [])
    if scope == "reports" and br_count <= 0:
        quality_warnings.append("BR_EMPTY")
    if scope == "reports" and inv_count <= 0:
        quality_warnings.append("INV_CSV_EMPTY")
    if scope == "reports" and ads_count <= 0:
        quality_warnings.append("ADS_CSV_EMPTY")

    return {
        "period_days": period,
        "br_source": br_source,
        "inventory_source": inv_source,
        "ads_source": ads_source,
        "br_rows": br_count,
        "inventory_rows": inv_count,
        "ads_rows": ads_count,
        "products_stored": len(products),
        "products_with_revenue": sum(1 for row in products if str(row.get("revenue_30d") or "").strip()),
        "products_with_ad_spend": sum(1 for row in products if str(row.get("ad_spend_30d") or "").strip()),
        "products_with_inventory": sum(
            1 for row in products if int(str(row.get("inventory") or "0").replace(",", "") or 0) > 0
        ),
        "warnings": list(dict.fromkeys(quality_warnings)),
    }
