"""Sponsored Products ASIN 级广告报表 CSV/XLSX 解析。"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from app.amazon.composer.product_filters import parse_money_text
from app.amazon.parsers.csv_common import cell, map_headers, read_spreadsheet_table

_ASIN_RE = re.compile(r"\b(B0[A-Z0-9]{8})\b", re.I)

_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "asin": (
        "asin",
        "advertised asin",
        "advertised product",
        "广告 asin",
        "广告asin",
        "子 asin",
        "advertised product (asin)",
    ),
    "ad_spend_30d": (
        "spend",
        "花费",
        "广告花费",
        "7 day total spend",
        "total cost",
        "spend (usd)",
    ),
    "acos": (
        "acos",
        "广告投入产出比 (acos) 总计",
        "广告成本销售比",
        "total advertising cost of sales (acos)",
        "acos (%)",
    ),
    "sales": ("sales", "7 day total sales", "销售额", "7 day advertised sku sales", "7天内广告sku销售额"),
    "campaign_name": ("campaign name", "campaign", "广告活动名称", "广告组合名称"),
}


def _money(value: str) -> str:
    amount = parse_money_text(value)
    if amount <= 0:
        return ""
    return f"{amount:,.2f}"


def _percent(value: str) -> str:
    text = str(value or "").strip().replace("%", "")
    if not text:
        return ""
    try:
        num = float(text.replace(",", ""))
    except ValueError:
        return ""
    if num <= 0:
        return ""
    return str(round(num, 1))


def _asin_from_row(row: list[str], mapping: dict[str, int]) -> str:
    asin = cell(row, mapping, "asin").upper()
    if _ASIN_RE.match(asin):
        return asin
    for key in ("campaign_name",):
        idx = mapping.get(key)
        if idx is None or idx >= len(row):
            continue
        match = _ASIN_RE.search(str(row[idx] or ""))
        if match:
            return match.group(1).upper()
    blob = " ".join(str(v) for v in row[:8])
    match = _ASIN_RE.search(blob)
    return match.group(1).upper() if match else ""


def _map_ads_headers(headers: list[str]) -> dict[str, int]:
    mapping = map_headers(headers, _COLUMN_ALIASES)
    for idx, name in enumerate(headers):
        norm = (name or "").strip().lower()
        if norm == "花费" or norm.endswith("花费"):
            mapping["ad_spend_30d"] = idx
        if "acos" in norm or "广告投入产出比" in name:
            mapping["acos"] = idx
        if norm in {"asin", "广告 asin", "广告asin"} or "advertised asin" in norm:
            mapping["asin"] = idx
        if "广告活动名称" in name or norm == "campaign name":
            mapping["campaign_name"] = idx
        if "广告组合名称" in name and "campaign_name" not in mapping:
            mapping["campaign_name"] = idx
    return mapping


def parse_ads_asin_csv(path: Path) -> list[dict[str, Any]]:
    headers, body = read_spreadsheet_table(path)
    if not headers or not body:
        return []

    mapping = _map_ads_headers(headers)
    if "ad_spend_30d" not in mapping and "acos" not in mapping:
        return []

    by_asin: dict[str, dict[str, Any]] = {}
    for raw in body:
        asin = _asin_from_row(raw, mapping)
        if not _ASIN_RE.match(asin):
            continue
        spend = parse_money_text(cell(raw, mapping, "ad_spend_30d"))
        acos_raw = _percent(cell(raw, mapping, "acos"))
        acos = float(acos_raw) if acos_raw else 0.0
        bucket = by_asin.setdefault(
            asin,
            {
                "asin": asin,
                "campaign_name": "",
                "ad_spend_30d": "",
                "acos": "",
                "field_sources": {"ad_spend_30d": "ads_csv", "acos": "ads_csv"},
            },
        )
        existing_spend = parse_money_text(bucket.get("ad_spend_30d"))
        total_spend = existing_spend + spend
        if total_spend > 0:
            bucket["ad_spend_30d"] = _money(total_spend)
        if acos > 0:
            bucket["acos"] = acos
        name = cell(raw, mapping, "campaign_name")
        if name:
            bucket["campaign_name"] = name

    return list(by_asin.values())
