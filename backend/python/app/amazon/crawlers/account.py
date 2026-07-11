"""账户首页 / 健康页解析。"""
from __future__ import annotations

from app.amazon.parsers.account_health import parse_seller_central_text
from app.amazon.parsers.seller_pages import parse_cases_from_text, parse_seller_news_from_text
from app.amazon.page_urls import HEALTH_URL
from app.amazon.session_context import goto


def parse_home_metrics(home_text: str) -> list:
    return parse_seller_central_text(home_text)


def parse_home_news_and_cases(home_text: str) -> tuple[list, list]:
    return parse_seller_news_from_text(home_text), parse_cases_from_text(home_text)


def cases_from_seller_news(news_items: list) -> list:
    """无 Case 日志时，将业绩通知类卖家新闻映射为待办 Case。"""
    cases: list[dict] = []
    seen: set[str] = set()
    for item in news_items or []:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        if not title:
            continue
        lowered = title.lower()
        if "业绩通知" not in title and "performance notification" not in lowered:
            continue
        case_id = str(item.get("id") or "performance_notifications")
        if case_id in seen:
            continue
        seen.add(case_id)
        cases.append(
            {
                "id": item.get("id") or "news_case_1",
                "case_id": case_id,
                "title": title[:160],
                "status": item.get("status") or "pending",
                "opened_at": item.get("published_at") or "",
                "note": str(item.get("summary") or title)[:220],
            }
        )
    return cases


def crawl_account_health_metrics(page) -> list:
    health_text = goto(page, HEALTH_URL, 8000)
    return parse_seller_central_text(health_text)
