"""Amazon 多源产品行合成。"""
from __future__ import annotations

from typing import Any

from app.amazon.composer.product_filters import (
    filter_valid_product_rows,
    is_junk_product_name,
    is_valid_product_row,
    parse_money_text,
    sanitize_br_rows,
)
from app.amazon.sources.amazon_sync_config import report_period_days

_ASIN_RE = __import__("re").compile(r"^[A-Z0-9]{10}$", __import__("re").I)


def _metric_numeric(raw: dict[str, Any], key: str) -> float:
    return parse_money_text(raw.get(key))


def _pick_richer_metric(current: dict[str, Any], incoming: dict[str, Any], key: str) -> Any:
    current_val = current.get(key)
    incoming_val = incoming.get(key)
    if _metric_numeric(incoming, key) > _metric_numeric(current, key):
        return incoming_val
    if _metric_numeric(current, key) > 0:
        return current_val
    return incoming_val if incoming_val not in (None, "") else current_val


def _format_money_str(value: Any) -> str:
    amount = parse_money_text(value)
    if amount <= 0:
        return ""
    return f"{amount:,.2f}"


def catalog_metrics_by_asin(*sources: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """从未过滤的库存/目录行提取 ASIN 级指标（避免 filter 丢弃仅库存行）。"""
    index: dict[str, dict[str, Any]] = {}
    metric_keys = (
        "inventory",
        "page_views",
        "conversion_rate",
        "orders_30d",
        "revenue_30d",
        "sku",
        "product_name",
    )
    for source in sources:
        for row in source:
            if not isinstance(row, dict):
                continue
            asin = str(row.get("asin") or "").strip().upper()
            if not _ASIN_RE.match(asin):
                continue
            current = index.setdefault(asin, {"asin": asin})
            for key in metric_keys:
                incoming = row.get(key)
                if incoming in (None, ""):
                    continue
                if key in {"inventory", "page_views", "orders_30d", "revenue_30d", "conversion_rate"}:
                    if _metric_numeric(row, key) >= _metric_numeric(current, key):
                        current[key] = incoming
                elif key == "product_name":
                    existing = str(current.get(key) or "").strip()
                    incoming_name = str(incoming or "").strip()
                    if len(incoming_name) > len(existing) and not is_junk_product_name(incoming_name):
                        current[key] = incoming_name
                else:
                    current[key] = incoming
    return index


def merge_catalog_metrics_into_products(
    products: list[dict[str, Any]],
    metrics_by_asin: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    if not products or not metrics_by_asin:
        return products
    merged = [dict(item) for item in products if isinstance(item, dict)]
    for row in merged:
        asin = str(row.get("asin") or "").strip().upper()
        metrics = metrics_by_asin.get(asin)
        if not metrics:
            continue
        for key in ("inventory", "page_views", "conversion_rate", "orders_30d", "revenue_30d"):
            if _metric_numeric(row, key) <= 0 and _metric_numeric(metrics, key) > 0:
                row[key] = metrics[key]
            elif key == "inventory" and row.get(key) in (None, "") and metrics.get(key) not in (None, ""):
                row[key] = metrics[key]
        catalog_name = str(metrics.get("product_name") or "").strip()
        if catalog_name and (
            is_junk_product_name(str(row.get("product_name") or ""))
            or str(row.get("product_name") or "").upper() == asin
        ):
            row["product_name"] = catalog_name
    return merged


def merge_product_catalog(
    primary: list[dict[str, Any]],
    fallback: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    metric_keys = (
        "revenue_30d",
        "orders_30d",
        "page_views",
        "ad_spend_30d",
        "acos",
        "tacos",
        "conversion_rate",
        "inventory",
        "sku",
    )
    merged: dict[str, dict[str, Any]] = {}
    for row in [*fallback, *primary]:
        if not isinstance(row, dict):
            continue
        asin = str(row.get("asin") or "").strip().upper()
        if not asin:
            continue
        current = merged.get(asin, {})
        combined = {**current, **row, "asin": asin}
        for key in metric_keys:
            combined[key] = _pick_richer_metric(current, row, key)
        current_name = str(current.get("product_name") or "").strip()
        incoming_name = str(row.get("product_name") or "").strip()
        if len(incoming_name) > len(current_name) and not is_junk_product_name(incoming_name):
            combined["product_name"] = incoming_name
        elif current_name and not combined.get("product_name"):
            combined["product_name"] = current_name
        merged[asin] = combined
    rows = list(merged.values())
    rows.sort(
        key=lambda item: (
            parse_money_text(item.get("revenue_30d")),
            parse_money_text(item.get("orders_30d")),
        ),
        reverse=True,
    )
    return rows[:50]


def aggregate_orders_into_products(
    products: list[dict[str, Any]],
    orders: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_asin: dict[str, dict[str, float | str]] = {}
    for order in orders:
        if not isinstance(order, dict):
            continue
        asin = str(order.get("asin") or "").strip().upper()
        if not asin or not _ASIN_RE.match(asin):
            continue
        bucket = by_asin.setdefault(asin, {"orders": 0.0, "revenue": 0.0, "name": ""})
        bucket["orders"] = float(bucket["orders"]) + max(parse_money_text(order.get("quantity") or 1), 1.0)
        bucket["revenue"] = float(bucket["revenue"]) + parse_money_text(order.get("amount"))
        name = str(order.get("product_name") or "").strip()
        if len(name) > len(str(bucket["name"])):
            bucket["name"] = name

    if not by_asin:
        return products

    merged = [dict(item) for item in products if isinstance(item, dict)]
    index = {str(item.get("asin") or "").upper(): item for item in merged}
    for asin, stats in by_asin.items():
        target = index.get(asin)
        if target is None:
            target = {
                "asin": asin,
                "product_name": stats["name"] or asin,
                "revenue_30d": "",
                "orders_30d": "0",
            }
            merged.append(target)
            index[asin] = target
        if parse_money_text(target.get("orders_30d")) <= 0 and float(stats["orders"]) > 0:
            target["orders_30d"] = str(int(float(stats["orders"])))
        if parse_money_text(target.get("revenue_30d")) <= 0 and float(stats["revenue"]) > 0:
            target["revenue_30d"] = _format_money_str(float(stats["revenue"]))
        if not str(target.get("product_name") or "").strip() and stats["name"]:
            target["product_name"] = stats["name"]
    return merged


def cap_suspicious_order_metrics(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """订单页误解析的汇总值不应覆盖 BR 指标。"""
    capped = [dict(item) for item in products if isinstance(item, dict)]
    for row in capped:
        orders = parse_money_text(row.get("orders_30d"))
        revenue = parse_money_text(row.get("revenue_30d"))
        name = str(row.get("product_name") or "").strip().upper()
        asin = str(row.get("asin") or "").strip().upper()
        if orders > 50 and revenue > 0 and orders / max(revenue, 1) > 5:
            row["orders_30d"] = "0"
        if name == asin and orders > 30:
            row["orders_30d"] = "0"
            row["revenue_30d"] = ""
    return capped


def merge_campaign_ads_into_products(
    products: list[dict[str, Any]],
    campaigns: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not products or not campaigns:
        return products
    merged = [dict(item) for item in products if isinstance(item, dict)]
    for campaign in campaigns:
        if not isinstance(campaign, dict):
            continue
        spend = parse_money_text(campaign.get("ad_spend_30d"))
        if spend <= 0:
            continue
        asin = str(campaign.get("asin") or "").strip().upper()
        campaign_name = str(campaign.get("campaign_name") or "").strip().lower()
        acos_raw = campaign.get("acos")
        try:
            acos = float(str(acos_raw).replace("%", "").strip()) if acos_raw not in (None, "") else 0.0
        except ValueError:
            acos = 0.0

        target = None
        if asin:
            target = next((p for p in merged if str(p.get("asin") or "").upper() == asin), None)
        if target is None and campaign_name:
            for product in merged:
                name = str(product.get("product_name") or "").strip().lower()
                if len(name) >= 6 and name in campaign_name:
                    target = product
                    break
        if target is None:
            continue

        existing_spend = parse_money_text(target.get("ad_spend_30d"))
        total_spend = existing_spend + spend
        target["ad_spend_30d"] = _format_money_str(total_spend)
        revenue = parse_money_text(target.get("revenue_30d"))
        if acos > 0:
            target["acos"] = acos
        elif revenue > 0 and total_spend > 0:
            target["acos"] = round(total_spend / revenue * 100, 1)
    return merged


def enrich_product_rows(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for raw in products:
        if not isinstance(raw, dict) or not is_valid_product_row(raw):
            continue
        row = dict(raw)
        revenue = parse_money_text(row.get("revenue_30d"))
        spend = parse_money_text(row.get("ad_spend_30d"))
        if revenue > 0:
            row["revenue_30d"] = _format_money_str(revenue)
        if spend <= 0:
            row["ad_spend_30d"] = ""
            row["acos"] = ""
            row["tacos"] = ""
        else:
            row["ad_spend_30d"] = _format_money_str(spend)
            acos_raw = row.get("acos")
            try:
                acos = float(str(acos_raw).replace("%", "").strip()) if acos_raw not in (None, "") else 0.0
            except ValueError:
                acos = 0.0
            if acos <= 0 and revenue > 0:
                acos = round(spend / revenue * 100, 1)
                row["acos"] = acos
            if revenue > 0:
                row["tacos"] = round(spend / revenue * 100, 1)
            else:
                row["tacos"] = ""
        if not row.get("conversion_rate"):
            page_views = parse_money_text(row.get("page_views"))
            orders = parse_money_text(row.get("orders_30d"))
            if page_views > 0 and orders > 0:
                row["conversion_rate"] = round(orders / page_views * 100, 2)
        if parse_money_text(row.get("inventory")) <= 0:
            row.setdefault("inventory", "0")
        row.setdefault("period_days", report_period_days())
        enriched.append(row)
    return enriched


def compose_product_rows(
    report_rows: list[dict[str, Any]],
    inventory_rows: list[dict[str, Any]],
    catalog_rows: list[dict[str, Any]],
    order_rows: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    raw_metrics = catalog_metrics_by_asin(inventory_rows, catalog_rows)
    catalog = filter_valid_product_rows(
        merge_product_catalog([], merge_product_catalog(inventory_rows, catalog_rows))
    )
    catalog_by_asin: dict[str, dict[str, Any]] = {}
    for row in catalog:
        asin = str(row.get("asin") or "").strip().upper()
        if asin:
            catalog_by_asin[asin] = dict(row)
    base_by_asin: dict[str, dict[str, Any]] = {}
    for row in catalog:
        asin = str(row.get("asin") or "").strip().upper()
        if not asin:
            continue
        base_by_asin[asin] = dict(row)

    report_rows = sanitize_br_rows(filter_valid_product_rows(report_rows))
    for row in report_rows:
        asin = str(row.get("asin") or "").strip().upper()
        if not asin:
            continue
        current = base_by_asin.get(asin, {"asin": asin, "product_name": asin})
        merged = {**current, **row, "asin": asin}
        catalog_name = str(current.get("product_name") or "").strip()
        report_name = str(merged.get("product_name") or "").strip()
        if (is_junk_product_name(report_name) or report_name.upper() == asin) and catalog_name:
            merged["product_name"] = catalog_name
        base_by_asin[asin] = merged

    composed = list(base_by_asin.values())
    if order_rows:
        composed = aggregate_orders_into_products(composed, order_rows)

    composed = merge_catalog_metrics_into_products(composed, raw_metrics)
    for row in composed:
        asin = str(row.get("asin") or "").strip().upper()
        catalog = catalog_by_asin.get(asin)
        if not catalog:
            continue
        for key in ("inventory", "page_views", "conversion_rate", "revenue_30d", "orders_30d"):
            if parse_money_text(row.get(key)) <= 0 and parse_money_text(catalog.get(key)) > 0:
                row[key] = catalog[key]

    composed.sort(
        key=lambda item: (
            parse_money_text(item.get("revenue_30d")),
            parse_money_text(item.get("orders_30d")),
        ),
        reverse=True,
    )
    if composed:
        return cap_suspicious_order_metrics(composed)[:50]

    fallback = merge_product_catalog(report_rows, catalog)
    if order_rows:
        fallback = aggregate_orders_into_products(fallback, order_rows)
    return cap_suspicious_order_metrics(fallback)[:50]
