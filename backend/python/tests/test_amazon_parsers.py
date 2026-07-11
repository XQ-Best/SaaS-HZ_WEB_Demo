"""Parser regression checks for Amazon daily sync."""
from __future__ import annotations

from pathlib import Path

from app.amazon.parsers.account_health import parse_seller_home_text
from app.amazon.parsers.seller_pages import parse_reviews_from_text
from app.amazon.report_crawler import filter_valid_product_rows, is_valid_product_row

ROOT = Path(__file__).resolve().parents[1]
HOME_SAMPLE = ROOT / "data" / "amazon-probe-home.txt"

FEEDBACK_SAMPLE = """
反馈管理器
最新反馈
日期	评级	订单编号	评论	操作
2026/07/07	5	113-7966774-9300250	good
2026/06/29	1	113-9587851-5301049	Ordered empty envelope
2026/06/25	5	112-2744115-9981016	Arrived fine
"""


def test_home_buyer_messages_from_snapshot() -> None:
    if not HOME_SAMPLE.exists():
        return
    text = HOME_SAMPLE.read_text(encoding="utf-8")
    metrics = {item["metric_key"]: item["value_text"] for item in parse_seller_home_text(text)}
    assert metrics.get("buyer_messages") == "0", metrics.get("buyer_messages")
    assert metrics.get("open_orders") == "237", metrics.get("open_orders")


def test_reviews_parser_finds_one_star() -> None:
    rows = parse_reviews_from_text(FEEDBACK_SAMPLE)
    assert len(rows) == 1
    assert rows[0]["order_no"] == "113-9587851-5301049"
    assert rows[0]["rating"] == 1


def test_product_row_rejects_price_only_name() -> None:
    assert not is_valid_product_row({"asin": "B0H8BTLNL9", "product_name": "US$9,995"})
    assert not is_valid_product_row({"asin": "B0D7ZQL3XQ", "product_name": "$2,823.00"})
    assert not is_valid_product_row({"asin": "G200205250", "product_name": "了解更多信息"})
    assert not is_valid_product_row({"asin": "B08G56D1BV", "product_name": "创建 A/B 试验"})
    assert not is_valid_product_row({"asin": "B0H4LGPGVK", "product_name": "编辑未来的开始日期"})
    assert not is_valid_product_row({"asin": "B0C96B8MPV", "product_name": "2026/7/10"})
    assert is_valid_product_row({
        "asin": "B0H8BTLNL9",
        "product_name": "YOTO Dual Hook Catfish Rig for Live Bait Fishing",
        "orders_30d": 1,
    })
    filtered = filter_valid_product_rows([
        {"asin": "B0H8BTLNL9", "product_name": "US$9,995"},
        {"asin": "B0H8C2BNQS", "product_name": "YOTO Dual Hook Catfish Rig", "revenue_30d": "12.3"},
    ])
    assert len(filtered) == 1
    assert filtered[0]["asin"] == "B0H8C2BNQS"


def test_compose_product_rows_prefers_report_metrics() -> None:
    from app.amazon.report_crawler import _compose_product_rows

    report = [{"asin": "B0H8BTLNL9", "product_name": "Short", "revenue_30d": "88.00", "orders_30d": "5"}]
    catalog = [
        {"asin": "B0H8BTLNL9", "product_name": "YOTO Dual Hook Catfish Rig for Live Bait Fishing", "revenue_30d": "", "orders_30d": "0"},
        {"asin": "B0H8C2BNQS", "product_name": "YOTO Dual Hook Catfish Rig", "revenue_30d": "", "orders_30d": "0"},
    ]
    composed = _compose_product_rows(report, catalog, [], [{"asin": "B0H8C2BNQS", "amount": "12.50", "quantity": 2}])
    assert len(composed) == 2
    by_asin = {row["asin"]: row for row in composed}
    assert by_asin["B0H8BTLNL9"]["revenue_30d"] == "88.00"
    assert "Live Bait" in by_asin["B0H8BTLNL9"]["product_name"]
    assert by_asin["B0H8C2BNQS"]["orders_30d"] == "2"


def test_merge_product_catalog_prefers_report_metrics() -> None:
    from app.amazon.report_crawler import _merge_product_catalog

    catalog = [{
        "asin": "B0H8BTLNL9",
        "product_name": "YOTO Dual Hook Catfish Rig for Live Bait Fishing",
        "revenue_30d": "",
        "orders_30d": "0",
    }]
    report = [{
        "asin": "B0H8BTLNL9",
        "product_name": "YOTO Dual Hook",
        "revenue_30d": "123.45",
        "orders_30d": "7",
        "page_views": "120",
    }]
    merged = _merge_product_catalog(report, catalog)
    assert len(merged) == 1
    assert merged[0]["revenue_30d"] == "123.45"
    assert merged[0]["orders_30d"] == "7"
    assert "Live Bait" in merged[0]["product_name"]


def test_page_urls_cover_orders_and_ads() -> None:
    from app.amazon.page_urls import (
        ORDER_LIST_SPECS,
        build_ads_urls,
        order_status_from_url,
        page_map_summary,
    )

    keys = {spec["key"] for spec in ORDER_LIST_SPECS}
    assert "hub" in keys
    assert "fba_pending" in keys
    assert "fba_canceled" in keys
    assert order_status_from_url("https://sellercentral.amazon.com/orders-v3/fba/canceled?page=1") == "canceled"
    assert order_status_from_url("https://sellercentral.amazon.com/orders-v3/fba/pending?page=1") == "pending"
    ads = build_ads_urls("A3B69JEON4HA6")
    assert ads[0].startswith("https://advertising.amazon.com/campaign-manager/all-campaigns")
    assert "merchantId=A3B69JEON4HA6" in ads[0]
    assert any(item["area"] == "订单" for item in page_map_summary())


def test_scope_planner_reports_includes_orders_and_ads() -> None:
    from app.amazon.scope_planner import plan_tasks

    keys = {task.key for task in plan_tasks("reports")}
    assert "br_child_asin" in keys
    assert "orders_fba_pending" in keys
    assert "ads_campaign_manager" in keys


def test_crawl_pipeline_empty_result_shape() -> None:
    from app.amazon.crawl_pipeline import _empty_result

    payload = _empty_result()
    assert "result_summary" in payload
    assert "page_diagnostics" in payload
    assert "merchant_id" in payload


def test_allocate_ads_from_acos_only() -> None:
    from app.amazon.composer.metrics_merger import coalesce_ads_summary
    from app.amazon.composer.product_composer import allocate_account_ads_by_revenue

    products = [
        {"asin": "B08B8X3Q6C", "revenue_30d": "1,868.13", "orders_30d": "5"},
        {"asin": "B07ZPMPKBT", "revenue_30d": "199.90", "orders_30d": "2"},
    ]
    metrics = [{"metric_key": "ad_acos_snapshot", "value_text": "40.84%"}]
    summary = coalesce_ads_summary({}, metrics)
    merged = allocate_account_ads_by_revenue(products, summary)
    assert parse_money(str(merged[0].get("ad_spend_30d"))) > 0
    assert float(merged[0].get("acos") or 0) == 40.84


def test_cap_suspicious_order_metrics() -> None:
    from app.amazon.composer.product_composer import cap_suspicious_order_metrics
    from app.amazon.composer.product_filters import parse_money_text

    rows = cap_suspicious_order_metrics([
        {"asin": "B0D7ZQL3XQ", "product_name": "B0D7ZQL3XQ", "orders_30d": "148", "revenue_30d": "1,576.47"},
    ])
    assert parse_money_text(rows[0].get("orders_30d")) == 0


def parse_money(value: str) -> float:
    from app.amazon.composer.product_filters import parse_money_text

    return parse_money_text(value)


def test_parse_cases_from_home_text() -> None:
    from app.amazon.parsers.seller_pages import parse_cases_from_text

    text = "Manage your case log\n3 cases requiring action\nPerformance notifications\n5"
    cases = parse_cases_from_text(text)
    assert len(cases) >= 1


def test_parse_orders_from_text() -> None:
    from app.amazon.parsers.seller_pages import parse_orders_from_text

    text = "Order 113-7966774-9300250 B08B8X3Q6C US$19.99 Qty 2\n113-9587851-5301049 shipped"
    rows = parse_orders_from_text(text)
    assert len(rows) == 2
    assert rows[1]["status"] == "shipped"


def test_parse_inventory_cards_from_text() -> None:
    from app.amazon.parsers.seller_pages import parse_inventory_cards_from_text

    text = """
    YOTO Fishing Leaders
    ASIN
    B08B8X3Q6C
    SKU
    sku-1
    页面浏览量
    128
    售出件数
    12
    可售
    45
    在库
    50
    """
    rows = parse_inventory_cards_from_text(text)
    assert len(rows) == 1
    assert rows[0]["asin"] == "B08B8X3Q6C"
    assert rows[0]["inventory"] == "45"
    assert rows[0]["page_views"] == "128"
    assert rows[0]["orders_30d"] == "12"


def test_compose_merges_raw_inventory_metrics() -> None:
    from app.amazon.report_crawler import _compose_product_rows

    report = [{
        "asin": "B08B8X3Q6C",
        "product_name": "YOTO Dual Hook Catfish Rig for Live Bait Fishing",
        "revenue_30d": "100.00",
        "orders_30d": "5",
    }]
    inventory = [{
        "asin": "B08B8X3Q6C",
        "product_name": "YOTO Dual Hook Catfish Rig",
        "inventory": "45",
        "page_views": "128",
        "revenue_30d": "",
        "orders_30d": "0",
    }]
    composed = _compose_product_rows(report, inventory, [], None)
    by_asin = {row["asin"]: row for row in composed}
    assert by_asin["B08B8X3Q6C"]["inventory"] == "45"
    assert by_asin["B08B8X3Q6C"]["page_views"] == "128"


def test_parse_cases_multiline_performance_notifications() -> None:
    from app.amazon.parsers.seller_pages import parse_cases_from_text

    text = "业绩通知\n120 天\n3\n卖家新闻"
    cases = parse_cases_from_text(text)
    assert any(item.get("case_id") == "performance_notifications" for item in cases)


if __name__ == "__main__":
    test_home_buyer_messages_from_snapshot()
    test_reviews_parser_finds_one_star()
    print("ok")
