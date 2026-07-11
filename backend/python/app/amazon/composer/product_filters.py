"""Amazon 产品行过滤与校验。"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

_STATUS_ONLY_RE = re.compile(
    r"^(在售|停售|缺货|active|inactive|out of stock|–|-)$",
    re.I,
)
_PRICE_ONLY_NAME_RE = re.compile(
    r"^(?:US\$|USD\$?|\$|EUR€?|£|¥|CN¥|R\$)?\s*[\d,]+(?:\.\d+)?(?:\s*(?:USD|EUR|GBP|CNY|JPY))?\s*$",
    re.I,
)
_UI_ACTION_NAME_RES = (
    re.compile(r"^了解更多", re.I),
    re.compile(r"^创建\s*A/?B\s*试验", re.I),
    re.compile(r"^查看建议", re.I),
    re.compile(r"^编辑未来", re.I),
    re.compile(r"^报告缺失", re.I),
    re.compile(r"^(learn more|create a/?b test|view suggestion|edit future|report missing)", re.I),
)
_ASIN_RE = re.compile(r"^[A-Z0-9]{10}$", re.I)
_GCID_LIKE_RE = re.compile(r"^G\d{9}$", re.I)
_DATETIME_NAME_RE = re.compile(
    r"(\d{4}[/-]\d{1,2}[/-]\d{1,2}.*(?:GMT|UTC|AM|PM))|(\d{4}[/-]\d{1,2}[/-]\d{1,2}$)",
    re.I,
)


def parse_money_text(value: Any) -> float:
    if value is None:
        return 0.0
    cleaned = re.sub(r"[^\d.-]", "", str(value))
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0


def is_junk_product_name(name: str) -> bool:
    text = str(name or "").strip()
    if not text or _STATUS_ONLY_RE.match(text) or _PRICE_ONLY_NAME_RE.match(text):
        return True
    for pattern in _UI_ACTION_NAME_RES:
        if pattern.search(text):
            return True
    if _DATETIME_NAME_RE.search(text):
        return True
    if len(text) <= 10 and not re.search(r"[A-Za-z]{4,}", text):
        if re.fullmatch(r"[\u4e00-\u9fff/A-B\\s]+", text):
            return True
    return False


def looks_like_product_title(name: str) -> bool:
    text = str(name or "").strip()
    if is_junk_product_name(text):
        return False
    if len(text) >= 24:
        return True
    words = re.findall(r"[A-Za-z\u4e00-\u9fff]{2,}", text)
    return len(words) >= 4


def has_product_activity(raw: dict[str, Any]) -> bool:
    revenue = parse_money_text(raw.get("revenue_30d") or raw.get("revenue7d"))
    orders = parse_money_text(raw.get("orders_30d") or raw.get("orders7d"))
    inventory = parse_money_text(raw.get("inventory") or raw.get("units_on_hand"))
    page_views = parse_money_text(raw.get("page_views"))
    spend = parse_money_text(raw.get("ad_spend_30d"))
    return revenue > 0 or orders > 0 or inventory > 0 or page_views > 0 or spend > 0


def has_report_metrics(raw: dict[str, Any]) -> bool:
    revenue = parse_money_text(raw.get("revenue_30d"))
    orders = parse_money_text(raw.get("orders_30d"))
    page_views = parse_money_text(raw.get("page_views"))
    return revenue > 0 or orders > 0 or page_views > 0


def sanitize_br_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(rows) < 2:
        return rows
    orders_counter = Counter(
        int(parse_money_text(row.get("orders_30d")))
        for row in rows
        if parse_money_text(row.get("orders_30d")) > 0
    )
    revenue_counter = Counter(
        round(parse_money_text(row.get("revenue_30d")), 2)
        for row in rows
        if parse_money_text(row.get("revenue_30d")) > 0
    )
    duplicated_orders = {value for value, count in orders_counter.items() if count >= 2 and value >= 10}
    duplicated_revenue = {value for value, count in revenue_counter.items() if count >= 2 and value > 0}
    cleaned: list[dict[str, Any]] = []
    for raw in rows:
        row = dict(raw)
        orders = int(parse_money_text(row.get("orders_30d")))
        revenue = round(parse_money_text(row.get("revenue_30d")), 2)
        if orders in duplicated_orders:
            row["orders_30d"] = "0"
        if revenue in duplicated_revenue:
            row["revenue_30d"] = ""
        cleaned.append(row)
    return cleaned


def is_valid_product_row(raw: dict[str, Any]) -> bool:
    asin = str(raw.get("asin") or "").strip().upper()
    if not _ASIN_RE.match(asin) or _GCID_LIKE_RE.match(asin):
        return False
    name = str(raw.get("product_name") or raw.get("productName") or "").strip()
    if is_junk_product_name(name):
        return False
    if not re.search(r"[A-Za-z\u4e00-\u9fff]", name):
        return False
    return has_product_activity(raw) or looks_like_product_title(name)


def filter_valid_product_rows(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in products if isinstance(row, dict) and is_valid_product_row(row)]
