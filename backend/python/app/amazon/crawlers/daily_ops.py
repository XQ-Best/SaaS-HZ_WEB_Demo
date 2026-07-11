"""日常运营列表爬取（消息/差评/优惠券/货件）。"""
from __future__ import annotations

from typing import Any

from app.amazon.crawlers._page_js import crawl_first_match, crawl_page_list
from app.amazon.page_urls import CASE_URLS, COUPON_URLS, MESSAGES_URL, REVIEWS_URL, SHIPMENT_URLS
from app.amazon.parsers.seller_pages import (
    EXTRACT_CASES_JS,
    EXTRACT_COUPONS_JS,
    EXTRACT_MESSAGES_JS,
    EXTRACT_REVIEWS_JS,
    EXTRACT_SHIPMENTS_JS,
    parse_cases_from_text,
    parse_coupons_from_text,
    parse_reviews_from_text,
    parse_shipments_from_text,
)
from app.amazon.session_context import goto, looks_login_page


def crawl_operational_lists(page) -> tuple[list, list]:
    coupons = crawl_first_match(
        page,
        COUPON_URLS,
        EXTRACT_COUPONS_JS,
        parse_coupons_from_text,
        14000,
    )
    shipments = crawl_first_match(
        page,
        SHIPMENT_URLS,
        EXTRACT_SHIPMENTS_JS,
        parse_shipments_from_text,
        14000,
        scroll=True,
    )
    return coupons, shipments


def crawl_messages(page) -> list[dict[str, Any]]:
    msg_text = goto(page, MESSAGES_URL, 8000)
    if looks_login_page(msg_text, page.url):
        return []
    messages = page.evaluate(EXTRACT_MESSAGES_JS) or []
    return messages if isinstance(messages, list) else []


def crawl_reviews(page) -> list[dict[str, Any]]:
    page.goto(REVIEWS_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(15000)
    rev_text = page.inner_text("body")
    if looks_login_page(rev_text, page.url):
        return []
    reviews = page.evaluate(EXTRACT_REVIEWS_JS) or []
    if isinstance(reviews, list) and reviews:
        return reviews
    return parse_reviews_from_text(rev_text)


def crawl_cases(page) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    seen: set[str] = set()
    for url in CASE_URLS:
        try:
            text = goto(page, url, 10000)
            if looks_login_page(text, page.url):
                continue
            rows = page.evaluate(EXTRACT_CASES_JS) or []
            if not isinstance(rows, list) or not rows:
                rows = parse_cases_from_text(text)
            for row in rows:
                if not isinstance(row, dict):
                    continue
                case_id = str(row.get("case_id") or row.get("id") or "")
                if case_id and case_id in seen:
                    continue
                if case_id:
                    seen.add(case_id)
                cases.append(row)
            if cases:
                break
        except Exception:
            continue
    return cases
