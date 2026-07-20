"""FBA / Manage Inventory CSV 解析。"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from app.amazon.parsers.csv_common import cell, map_headers, read_spreadsheet_table

_ASIN_RE = re.compile(r"^[A-Z0-9]{10}$", re.I)

_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "asin": ("asin", "(child) asin", "child asin", "子 asin"),
    "sku": ("sku", "seller sku", "卖家 sku", "msku"),
    "product_name": ("product-name", "product name", "title", "商品名称", "商品名"),
    "inventory": (
        "available",
        "afn-fulfillable-quantity",
        "afn fulfillable quantity",
        "fulfillable quantity",
        "fulfillable",
        "可售",
        "可售数量",
        "available quantity",
        "quantity",
    ),
}


def _integer(value: str) -> str:
    cleaned = re.sub(r"[^\d-]", "", value or "")
    if not cleaned or cleaned == "-":
        return "0"
    try:
        return str(max(0, int(cleaned)))
    except ValueError:
        return "0"


def parse_inventory_csv(path: Path) -> list[dict[str, Any]]:
    headers, body = read_spreadsheet_table(path)
    if not headers or not body:
        return []

    mapping = map_headers(headers, _COLUMN_ALIASES)
    if "asin" not in mapping and "sku" not in mapping:
        return []

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in body:
        asin = cell(raw, mapping, "asin").upper()
        if not _ASIN_RE.match(asin):
            continue
        if asin in seen:
            continue
        seen.add(asin)
        rows.append(
            {
                "asin": asin,
                "sku": cell(raw, mapping, "sku")[:80],
                "product_name": cell(raw, mapping, "product_name")[:180],
                "inventory": _integer(cell(raw, mapping, "inventory")),
                "revenue_30d": "",
                "orders_30d": "0",
                "field_sources": {"inventory": "inv_csv"},
            }
        )
    return rows
