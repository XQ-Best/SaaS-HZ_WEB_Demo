"""Amazon Seller Central / Advertising 页面 URL 地图（爬虫与 open_amazon_sc 共用）。"""
from __future__ import annotations

from typing import Any

# --- 首页 / 账户 ---
HOME_URL = "https://sellercentral.amazon.com/home"
HEALTH_URL = "https://sellercentral.amazon.com/performance/account/health"

# --- 订单 orders-v3（与卖家后台侧栏一致）---
ORDERS_HUB_URL = "https://sellercentral.amazon.com/orders-v3/?page=1"
ORDERS_URL = ORDERS_HUB_URL  # 兼容旧引用

ORDER_LIST_SPECS: list[dict[str, str]] = [
    {"key": "hub", "url": "https://sellercentral.amazon.com/orders-v3/?page=1", "status": "pending"},
    {"key": "unshipped", "url": "https://sellercentral.amazon.com/orders-v3/unshipped?page=1", "status": "pending"},
    {"key": "pending", "url": "https://sellercentral.amazon.com/orders-v3/pending?page=1", "status": "pending"},
    {"key": "mfn_unshipped", "url": "https://sellercentral.amazon.com/orders-v3/mfn/unshipped?page=1", "status": "pending"},
    {"key": "fba_unshipped", "url": "https://sellercentral.amazon.com/orders-v3/fba/unshipped?page=1", "status": "pending"},
    {"key": "fba_pending", "url": "https://sellercentral.amazon.com/orders-v3/fba/pending?page=1", "status": "pending"},
    {"key": "mfn_pending", "url": "https://sellercentral.amazon.com/orders-v3/mfn/pending?page=1", "status": "pending"},
    {"key": "fba_canceled", "url": "https://sellercentral.amazon.com/orders-v3/fba/canceled?page=1", "status": "canceled"},
    {"key": "mfn_canceled", "url": "https://sellercentral.amazon.com/orders-v3/mfn/canceled?page=1", "status": "canceled"},
    {"key": "shipped", "url": "https://sellercentral.amazon.com/orders-v3/shipped?page=1", "status": "shipped"},
]

ORDER_LIST_URLS = [spec["url"] for spec in ORDER_LIST_SPECS]

# --- Business Report / 商品指标 ---
# 测绘结论（discover_amazon_sc）：直连 detail URL 可落地 #/dashboard；勿全页匹配「下载」
REPORTS_URL = "https://sellercentral.amazon.com/business-reports/detail/sales-traffic-by-asin"
BR_DASHBOARD_URL = "https://sellercentral.amazon.com/business-reports/#/dashboard"
BR_CHILD_REPORT_URL = (
    "https://sellercentral.amazon.com/business-reports/detail/sales-traffic-by-asin"
    "#/report?id=102:DetailSalesTrafficByChildItem"
)
REPORT_URLS = [
    BR_CHILD_REPORT_URL,
    "https://sellercentral.amazon.com/business-reports/detail/sales-traffic-by-asin?cols=%2F0%2F1%2F2%2F3%2F4%2F5%2F6%2F7",
    "https://sellercentral.amazon.com/business-reports/detail/sales-traffic-by-asin?columns=0%2F1%2F2%2F3%2F4%2F5%2F6%2F7",
    BR_DASHBOARD_URL,
    REPORTS_URL,
]

# --- 库存 / 目录 ---
INVENTORY_URLS = [
    "https://sellercentral.amazon.com/myinventory/inventory?fulfilledBy=all&mons_sel_locale=en_US",
    "https://sellercentral.amazon.com/myinventory/inventory?fulfilledBy=all",
    "https://sellercentral.amazon.com/myinventory/inventory",
    "https://sellercentral.amazon.com/inventory",
    "https://sellercentral.amazon.com/inventoryplanning/manageinventoryhealth",
]

# --- 广告（Campaign Manager 为当前主入口）---
ADS_CAMPAIGN_MANAGER_BASE = "https://advertising.amazon.com/campaign-manager/all-campaigns"
ADS_LEGACY_URLS = [
    "https://advertising.amazon.com/cm/campaigns",
    "https://advertising.amazon.com/cm/products",
    "https://advertising.amazon.com/cm/product-traffic",
    "https://sellercentral.amazon.com/cm/campaigns",
    "https://sellercentral.amazon.com/ads/campaigns",
    "https://sellercentral.amazon.com/ads/reports",
]

# --- 运营日常 ---
MESSAGES_URL = "https://sellercentral.amazon.com/messaging/inbox"
REVIEWS_URL = "https://sellercentral.amazon.com/feedback-manager/index.html"
COUPON_URLS = [
    "https://sellercentral.amazon.com/seller-promotions/coupon/home",
    "https://sellercentral.amazon.com/promotions/manage",
    "https://sellercentral.amazon.com/promotions/list",
]
SHIPMENT_URLS = [
    "https://sellercentral.amazon.com/fba/inbound-shipment/summary",
    "https://sellercentral.amazon.com/fba/shippingqueue",
    "https://sellercentral.amazon.com/gp/fba/inbound-shipment-workflow/index.html",
]

CASE_URLS = [
    "https://sellercentral.amazon.com/cu/case-lobby",
    "https://sellercentral.amazon.com/performance/notifications",
    "https://sellercentral.amazon.com/home",
]

CATALOG_URLS = [HOME_URL, *INVENTORY_URLS, *REPORT_URLS]

OPEN_PAGE_URLS = {
    "home": HOME_URL,
    "inventory": INVENTORY_URLS[0],
    "br": REPORT_URLS[0],
    "orders": ORDERS_HUB_URL,
    "orders_pending": "https://sellercentral.amazon.com/orders-v3/fba/pending?page=1",
    "orders_canceled": "https://sellercentral.amazon.com/orders-v3/fba/canceled?page=1",
    "ads": ADS_CAMPAIGN_MANAGER_BASE,
    "health": HEALTH_URL,
}


def order_status_from_url(url: str) -> str:
    path = (url or "").lower()
    if "/canceled" in path or "/cancelled" in path:
        return "canceled"
    if "/shipped" in path:
        return "shipped"
    if "/pending" in path or "/unshipped" in path:
        return "pending"
    return "pending"


def order_status_for_spec(url: str) -> str:
    for spec in ORDER_LIST_SPECS:
        if spec["url"].split("?")[0] == url.split("?")[0]:
            return spec["status"]
    return order_status_from_url(url)


def build_ads_urls(merchant_id: str = "", *, locale: str = "zh_CN") -> list[str]:
    urls: list[str] = []
    if merchant_id:
        urls.append(f"{ADS_CAMPAIGN_MANAGER_BASE}?merchantId={merchant_id}&locale={locale}")
    urls.append(f"{ADS_CAMPAIGN_MANAGER_BASE}?locale={locale}")
    urls.extend(ADS_LEGACY_URLS)
    seen: set[str] = set()
    ordered: list[str] = []
    for item in urls:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def page_map_summary() -> list[dict[str, Any]]:
    """供诊断脚本 / 文档生成使用的页面一览。"""
    return [
        {"area": "订单", "key": s["key"], "url": s["url"], "data": "outbound_orders", "status": s["status"]}
        for s in ORDER_LIST_SPECS
    ] + [
        {"area": "商品指标", "key": "br_child", "url": REPORT_URLS[0], "data": "products"},
        {"area": "库存", "key": "inventory", "url": INVENTORY_URLS[0], "data": "products(catalog)"},
        {"area": "广告", "key": "campaign_manager", "url": ADS_CAMPAIGN_MANAGER_BASE, "data": "ad_spend/acos/campaigns"},
        {"area": "账户", "key": "home", "url": HOME_URL, "data": "account_metrics"},
    ]
