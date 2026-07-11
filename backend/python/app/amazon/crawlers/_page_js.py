"""页面 JS 执行与通用导航辅助。"""
from __future__ import annotations

from typing import Any, Callable

from app.amazon.session_context import looks_login_page


def evaluate_js(page, js: str) -> list:
    try:
        rows = page.evaluate(js) or []
        if isinstance(rows, list) and rows:
            return rows
    except Exception:
        pass
    for frame in page.frames:
        try:
            rows = frame.evaluate(js) or []
            if isinstance(rows, list) and rows:
                return rows
        except Exception:
            continue
    return []


def crawl_page_list(
    page,
    url: str,
    js: str,
    text_parser: Callable[[str], list] | None,
    wait_ms: int = 12000,
    scroll: bool = False,
) -> list:
    try:
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(wait_ms)
        if scroll:
            page.evaluate("() => { window.scrollTo(0, document.body.scrollHeight); }")
            page.wait_for_timeout(2500)
        body = page.inner_text("body")
        if looks_login_page(body, page.url):
            return []
        rows = page.evaluate(js) or []
        if isinstance(rows, list) and rows:
            return rows
        return text_parser(body) if text_parser else []
    except Exception:
        return []


def crawl_first_match(
    page,
    urls: list[str],
    js: str,
    text_parser: Callable[[str], list] | None,
    wait_ms: int = 12000,
    scroll: bool = False,
) -> list:
    for url in urls:
        rows = crawl_page_list(page, url, js, text_parser, wait_ms, scroll)
        if rows:
            return rows
    return []
