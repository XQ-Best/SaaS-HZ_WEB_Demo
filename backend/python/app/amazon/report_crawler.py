"""Amazon 紫鸟 WebDriver 爬取（兼容入口，内部委托 crawl_pipeline）。"""
from __future__ import annotations

from typing import Any

from app.amazon.composer.product_composer import (
    compose_product_rows as _compose_product_rows,
    merge_product_catalog as _merge_product_catalog,
)
from app.amazon.composer.product_filters import (
    filter_valid_product_rows,
    is_valid_product_row,
)
from app.amazon.crawl_pipeline import (
    PRODUCT_SYNC_SCOPES,
    crawl_account_health,
    run_crawl,
)
from app.amazon.page_urls import (
    CATALOG_URLS,
    COUPON_URLS,
    HEALTH_URL,
    HOME_URL,
    INVENTORY_URLS,
    MESSAGES_URL,
    ORDERS_URL,
    REPORT_URLS,
    REVIEWS_URL,
    SHIPMENT_URLS,
)
from app.amazon.session_context import (
    AmazonLoginRequiredError,
    CAPTURE_DIR,
    extract_debug_port,
    goto as _goto,
    looks_login_page as _looks_login_page,
    looks_logged_in as _looks_logged_in,
    require_seller_logged_in as _require_seller_logged_in,
    save_capture as _save_capture,
)

# 向后兼容：测试与 write_actions 仍可从本模块 import
compose_product_rows = _compose_product_rows
merge_product_catalog = _merge_product_catalog


def crawl_amazon(
    *,
    scope: str = "account_health",
    browser_id: str = "",
    browser_oauth: str = "",
    store_name: str = "",
    merchant_id: str = "",
) -> dict[str, Any]:
    return run_crawl(
        scope=scope,
        browser_id=browser_id,
        browser_oauth=browser_oauth,
        store_name=store_name,
        merchant_id=merchant_id,
    )


__all__ = [
    "AmazonLoginRequiredError",
    "CAPTURE_DIR",
    "CATALOG_URLS",
    "COUPON_URLS",
    "HEALTH_URL",
    "HOME_URL",
    "INVENTORY_URLS",
    "MESSAGES_URL",
    "ORDERS_URL",
    "PRODUCT_SYNC_SCOPES",
    "REPORT_URLS",
    "REVIEWS_URL",
    "SHIPMENT_URLS",
    "crawl_account_health",
    "crawl_amazon",
    "filter_valid_product_rows",
    "is_valid_product_row",
    "compose_product_rows",
    "merge_product_catalog",
]
