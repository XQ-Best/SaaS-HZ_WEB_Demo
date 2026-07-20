"""Business Report CSV 解析（子 ASIN · 销售与流量）。"""
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

from app.amazon.composer.product_filters import (
    filter_valid_product_rows,
    has_report_metrics,
    parse_money_text,
    sanitize_br_rows,
)

_ASIN_RE = re.compile(r"^[A-Z0-9]{10}$", re.I)

# 列名候选（小写归一后匹配）
_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "asin": (
        "(child) asin",
        "child asin",
        "子 asin",
        "子asin",
        "子（asin）",
        "子(asin)",
        "子asin）",
        "asin",
    ),
    "product_name": (
        "title",
        "product title",
        "商品名称",
        "商品名",
        "标题",
    ),
    "sku": ("sku", "seller sku", "卖家 sku"),
    "orders_30d": (
        "units ordered",
        "ordered units",
        "已订购商品数量",
        "已订购数量",
        "销量",
    ),
    "revenue_30d": (
        "ordered product sales",
        "product sales",
        "已订购商品销售额",
        "销售额",
    ),
    "page_views": (
        "sessions",
        "session",
        "会话",
        "会话数",
        "会话数 - 总计",
        "会话数-总计",
        "page views",
        "页面浏览量",
    ),
    "conversion_rate": (
        "unit session percentage",
        "unit session %",
        "子商品转化率",
        "转化率",
        "转化率 - 总计",
        "转化率-总计",
    ),
}


def _normalize_header(text: str) -> str:
    cleaned = (text or "").strip().lower()
    cleaned = cleaned.replace("（", "(").replace("）", ")")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _map_headers(fieldnames: list[str] | None) -> dict[str, int]:
    if not fieldnames:
        return {}
    normalized = {_normalize_header(name): idx for idx, name in enumerate(fieldnames)}
    mapping: dict[str, int] = {}
    for key, aliases in _COLUMN_ALIASES.items():
        for alias in aliases:
            norm = _normalize_header(alias)
            if norm in normalized:
                mapping[key] = normalized[norm]
                break
    # 子 ASIN 列优先于父 ASIN（Amazon 导出含两列 ASIN）
    child_idx = None
    for idx, name in enumerate(fieldnames):
        norm = _normalize_header(name)
        if re.search(r"子.*asin|child.*asin", norm):
            child_idx = idx
            break
    if child_idx is not None:
        mapping["asin"] = child_idx
    return mapping


def _cell(row: list[str], mapping: dict[str, int], key: str) -> str:
    idx = mapping.get(key)
    if idx is None or idx >= len(row):
        return ""
    return str(row[idx] or "").strip()


def _money(value: str) -> str:
    amount = parse_money_text(value)
    if amount <= 0:
        return ""
    return f"{amount:,.2f}"


def _integer(value: str) -> str:
    amount = parse_money_text(value)
    if amount <= 0:
        return "0"
    return str(int(round(amount)))


def _percent(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    cleaned = text.replace("%", "").strip()
    try:
        num = float(cleaned.replace(",", ""))
    except ValueError:
        return ""
    if num <= 0:
        return ""
    return str(round(num, 2))


def _read_csv_rows(path: Path) -> tuple[list[str], list[list[str]]]:
    raw = path.read_bytes()
    text = ""
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if not text:
        text = raw.decode("utf-8", errors="replace")

    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return [], []

    # 跳过 BOM / 说明行，找到表头
    header_idx = 0
    for idx, line in enumerate(lines[:15]):
        lower = line.lower()
        if "asin" in lower and ("session" in lower or "ordered" in lower or "销售额" in lower or "会话" in lower):
            header_idx = idx
            break

    reader = csv.reader(lines[header_idx:])
    try:
        headers = next(reader)
    except StopIteration:
        return [], []

    body: list[list[str]] = []
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        body.append(row)
    return headers, body


def parse_business_report_csv(path: Path, *, period_days: int = 7) -> list[dict[str, Any]]:
    headers, body = _read_csv_rows(path)
    if not headers or not body:
        return []

    mapping = _map_headers(headers)
    if "asin" not in mapping:
        return []

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in body:
        asin = _cell(raw, mapping, "asin").upper()
        if not _ASIN_RE.match(asin) or asin in seen:
            continue
        seen.add(asin)
        name = _cell(raw, mapping, "product_name")
        rows.append(
            {
                "rank_no": len(rows) + 1,
                "product_name": (name or asin)[:180],
                "asin": asin,
                "sku": _cell(raw, mapping, "sku")[:80],
                "revenue_30d": _money(_cell(raw, mapping, "revenue_30d")),
                "orders_30d": _integer(_cell(raw, mapping, "orders_30d")),
                "page_views": _integer(_cell(raw, mapping, "page_views")),
                "conversion_rate": _percent(_cell(raw, mapping, "conversion_rate")),
                "ad_spend_30d": "",
                "acos": "",
                "tacos": "",
                "inventory": "0",
                "currency": "USD",
                "period_days": period_days,
                "field_sources": {
                    "revenue_30d": "br_csv",
                    "orders_30d": "br_csv",
                    "page_views": "br_csv",
                    "conversion_rate": "br_csv",
                },
            }
        )

    cleaned = [
        row
        for row in sanitize_br_rows(filter_valid_product_rows(rows))
        if has_report_metrics(row)
    ]
    cleaned.sort(
        key=lambda item: (
            parse_money_text(item.get("revenue_30d")),
            parse_money_text(item.get("orders_30d")),
        ),
        reverse=True,
    )
    return cleaned[:50]
