"""Business Report CSV parser tests."""
from __future__ import annotations

from pathlib import Path

from app.amazon.parsers.csv_br import parse_business_report_csv

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_parse_br_csv_en() -> None:
    rows = parse_business_report_csv(FIXTURES / "br_child_asin_7d_en.csv", period_days=7)
    assert len(rows) == 3
    top = rows[0]
    assert top["asin"] == "B0C96B8MPV"
    assert top["orders_30d"] == "12"
    assert top["revenue_30d"] == "518.40"
    assert top["page_views"] == "1787"
    assert top["conversion_rate"] == "0.06"
    assert top["period_days"] == 7
    assert top["field_sources"]["revenue_30d"] == "br_csv"


def test_parse_br_csv_zh() -> None:
    rows = parse_business_report_csv(FIXTURES / "br_child_asin_7d_zh.csv", period_days=7)
    assert len(rows) == 2
    assert rows[0]["asin"] in {"B0C96B8MPV", "B0C4P5VXFQ"}
    assert rows[0]["revenue_30d"]


def test_parse_br_csv_sorts_by_revenue() -> None:
    rows = parse_business_report_csv(FIXTURES / "br_child_asin_7d_en.csv", period_days=7)
    revenues = [float(r["revenue_30d"].replace(",", "")) for r in rows]
    assert revenues == sorted(revenues, reverse=True)
