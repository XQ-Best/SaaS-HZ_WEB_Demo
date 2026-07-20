"""Inventory / Ads CSV parser tests."""
from __future__ import annotations

from pathlib import Path

from app.amazon.parsers.csv_ads import parse_ads_asin_csv
from app.amazon.parsers.csv_inventory import parse_inventory_csv

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_parse_inventory_csv() -> None:
    rows = parse_inventory_csv(FIXTURES / "inventory_export.csv")
    assert len(rows) == 2
    by_asin = {row["asin"]: row for row in rows}
    assert by_asin["B0C96B8MPV"]["inventory"] == "120"
    assert by_asin["B0C4P5VXFQ"]["inventory"] == "45"


def test_parse_ads_asin_csv() -> None:
    rows = parse_ads_asin_csv(FIXTURES / "ads_asin_7d.csv")
    assert len(rows) == 2
    by_asin = {row["asin"]: row for row in rows}
    assert by_asin["B0C96B8MPV"]["ad_spend_30d"] == "42.50"
    assert float(by_asin["B0C96B8MPV"]["acos"]) == 28.5
    assert by_asin["B0C4P5VXFQ"]["ad_spend_30d"] == "18.00"
