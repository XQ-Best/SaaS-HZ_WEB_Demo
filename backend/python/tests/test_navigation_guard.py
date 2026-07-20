"""navigation_guard 单元测试。"""
from app.amazon.navigation_guard import is_blocked_url


def test_blocked_sellermobileapp():
    url = "https://sellercentral.amazon.com/sellermobileapp?ref=xx_sellermobileapp_foot_xx"
    assert is_blocked_url(url)


def test_allowed_business_reports():
    url = "https://sellercentral.amazon.com/business-reports/detail/sales-traffic-by-asin"
    assert not is_blocked_url(url)
