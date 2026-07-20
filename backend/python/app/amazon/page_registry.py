"""Amazon 页面注册表（URL、等待、解析器、分页）。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.amazon.page_urls import (
    ADS_CAMPAIGN_MANAGER_BASE,
    COUPON_URLS,
    HEALTH_URL,
    HOME_URL,
    INVENTORY_URLS,
    MESSAGES_URL,
    ORDER_LIST_SPECS,
    REPORT_URLS,
    REVIEWS_URL,
    SHIPMENT_URLS,
    build_ads_urls,
)


@dataclass(frozen=True)
class PageTask:
    key: str
    url: str
    area: str
    parser_key: str
    wait_ms: int = 10000
    paginate: bool = False
    max_pages: int = 8
    default_status: str = ""
    required: bool = False
    fallback_urls: tuple[str, ...] = ()


def _order_tasks() -> list[PageTask]:
    tasks: list[PageTask] = []
    for spec in ORDER_LIST_SPECS:
        tasks.append(
            PageTask(
                key=f"orders_{spec['key']}",
                url=spec["url"],
                area="orders",
                parser_key="orders_v3",
                wait_ms=9000,
                paginate=True,
                max_pages=8,
                default_status=spec["status"],
            )
        )
    return tasks


PAGE_TASKS: dict[str, PageTask] = {
    "home": PageTask("home", HOME_URL, "account", "account_home", wait_ms=5000, required=True),
    "account_health": PageTask("account_health", HEALTH_URL, "account", "account_health", wait_ms=8000),
    "br_child_asin": PageTask(
        "br_child_asin",
        REPORT_URLS[0],
        "products",
        "business_report",
        wait_ms=12000,
        fallback_urls=tuple(REPORT_URLS[1:]),
        required=True,
    ),
    "inventory_all": PageTask(
        "inventory_all",
        INVENTORY_URLS[0],
        "products",
        "inventory",
        wait_ms=12000,
        fallback_urls=tuple(INVENTORY_URLS[1:]),
    ),
    "messages": PageTask("messages", MESSAGES_URL, "ops", "messages", wait_ms=8000),
    "reviews": PageTask("reviews", REVIEWS_URL, "ops", "reviews", wait_ms=15000),
    "coupons": PageTask(
        "coupons",
        COUPON_URLS[0],
        "ops",
        "coupons",
        wait_ms=14000,
        fallback_urls=tuple(COUPON_URLS[1:]),
    ),
    "shipments": PageTask(
        "shipments",
        SHIPMENT_URLS[0],
        "ops",
        "shipments",
        wait_ms=14000,
        fallback_urls=tuple(SHIPMENT_URLS[1:]),
    ),
    "ads_campaign_manager": PageTask(
        "ads_campaign_manager",
        ADS_CAMPAIGN_MANAGER_BASE,
        "ads",
        "campaign_manager",
        wait_ms=16000,
    ),
}

for _task in _order_tasks():
    PAGE_TASKS[_task.key] = _task


SCOPE_TASK_KEYS: dict[str, list[str]] = {
    "account_health": ["home", "account_health"],
    "daily": ["home", "messages", "reviews", "coupons", "shipments"],
    "reports": [
        "home",
        "br_child_asin",
        "inventory_all",
        "ads_campaign_manager",
    ],
    "insights": [
        "home",
        "br_child_asin",
        "inventory_all",
        *[f"orders_{spec['key']}" for spec in ORDER_LIST_SPECS],
        "ads_campaign_manager",
    ],
}


def resolve_task(key: str) -> PageTask | None:
    return PAGE_TASKS.get(key)


def ads_urls_for_merchant(merchant_id: str) -> list[str]:
    return build_ads_urls(merchant_id)


def page_map_summary() -> list[dict[str, Any]]:
    from app.amazon.page_urls import page_map_summary as _legacy_summary

    return _legacy_summary()
