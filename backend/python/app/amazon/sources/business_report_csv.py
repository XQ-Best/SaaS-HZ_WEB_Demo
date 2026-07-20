"""Business Report CSV 下载（子 ASIN · 最近 N 天）。

导航原则（见 docs/amazon-integration/19-SC站点测绘-方法.md）：
- 先 discover_amazon_sc 测绘 URL / XHR，再写采集
- 禁止 document.body 全页 querySelector 匹配「下载/导出」
- 点击限定 main / kat-side-nav；URL 黑名单含 sellermobileapp
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.amazon.navigation_guard import (
    assert_allowed_url,
    click_scoped,
    is_blocked_url,
    navigate_to_br_child_asin,
)
from app.amazon.page_urls import HOME_URL, REPORT_URLS
from app.amazon.parsers.csv_br import parse_business_report_csv
from app.amazon.session_context import looks_login_page, save_capture
from app.amazon.sources.amazon_sync_config import report_period_days
from app.amazon.sources.click_export import click_download_csv
from app.amazon.sources.download_helper import DownloadResult, build_download_dir, save_download


@dataclass
class BusinessReportCsvResult:
    rows: list[dict[str, Any]]
    source: str
    artifact: str
    duration_ms: int
    warning: str
    page_url: str


def _wait_br_spa(page, *, timeout_ms: int = 60_000) -> None:
    """等待 BR SPA 报表区加载（非 sellermobileapp）。"""
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        assert_allowed_url(page.url, context="br_spa_wait")
        ready = page.evaluate(
            """
            () => {
              const url = location.href || '';
              if (/sellermobileapp/i.test(url)) return 'blocked';
              const inBr = /business-reports|sales-traffic/i.test(url);
              const hasMain = !!document.querySelector('kat-side-nav, aside nav, main, [data-testid="report-page"]');
              const hasSpinner = !!document.querySelector('kat-spinner, [class*="spinner"]');
              return JSON.stringify({ inBr, hasMain, hasSpinner });
            }
            """
        )
        if "blocked" in str(ready):
            raise RuntimeError(f"BR 等待时落入禁止页: {page.url}")
        try:
            import json

            info = json.loads(str(ready))
            if info.get("inBr") and info.get("hasMain") and not info.get("hasSpinner"):
                return
        except Exception:
            pass
        page.wait_for_timeout(2000)


def _click_report_apply(page) -> None:
    click_scoped(page, r"apply|应用|run report|刷新|更新|generate", kinds="button, kat-button, input[type=submit]")
    page.wait_for_timeout(6000)


def _assert_on_child_br(page) -> None:
    url = page.url or ""
    if is_blocked_url(url):
        raise RuntimeError(f"BR 落入禁止页: {url}")
    if re.search(r"DetailSalesTrafficByChild", url, re.I):
        return
    body = page.inner_text("body")[:1200]
    if re.search(r"按子商品|child.?asin|子\s*asin", body, re.I):
        return
    raise RuntimeError(f"不在子 ASIN 业务报告页: {url}")


def _set_br_period_and_apply(page, *, period_days: int) -> None:
    _assert_on_child_br(page)
    period_re = (
        r"last\s*7|最近\s*7|7\s*days?|7\s*天|过去\s*7"
        if period_days <= 7
        else r"last\s*30|最近\s*30|30\s*days?|30\s*天|过去\s*30"
    )
    click_scoped(page, r"^日期$|^date range$|^date$", kinds="kat-button, kat-dropdown-button, button, [role='button']")
    page.wait_for_timeout(800)
    click_scoped(
        page,
        period_re,
        kinds="kat-option, [role='option'], li, button, kat-button, span",
    )
    page.wait_for_timeout(1500)
    click_scoped(page, r"^应用$|^apply$", kinds="kat-button, button, [role='button']")
    page.wait_for_timeout(5000)
    _assert_on_child_br(page)


def _on_br_page(body: str, url: str) -> bool:
    if is_blocked_url(url):
        return False
    if re.search(r"DetailSalesTrafficByChild|按子商品", f"{url}{body[:600]}", re.I):
        return True
    return bool(re.search(r"(child).*(asin)|子.*asin|按子", body, re.I))


def _try_download_br_csv(
    page,
    *,
    store_name: str,
    dest_file: Path,
    period: int,
) -> tuple[list[dict[str, Any]], str, str]:
    _wait_br_spa(page)
    _assert_on_child_br(page)
    try:
        _set_br_period_and_apply(page, period_days=period)
    except RuntimeError:
        # 默认区间可接受时继续尝试下载
        pass
    _assert_on_child_br(page)
    page.wait_for_timeout(2000)
    try:
        download: DownloadResult = save_download(
            page,
            lambda: click_download_csv(page),
            dest_file,
            timeout_ms=120_000,
            source="csv",
        )
        rows = parse_business_report_csv(download.path, period_days=period)
        if rows:
            return rows, str(download.path), ""
        return [], str(download.path), "CSV_EMPTY"
    except Exception as exc:
        save_capture(page, store_name=store_name, suffix="br_csv_fail")
        return [], "", f"CSV_DOWNLOAD_FAILED:{exc.__class__.__name__}"


def crawl_business_report_csv(
    page,
    *,
    store_name: str = "",
    download_dir: Path | None = None,
    period_days: int | None = None,
) -> BusinessReportCsvResult:
    period = period_days if period_days is not None else report_period_days()
    started = time.time()
    dest_dir = download_dir or build_download_dir(store_name=store_name, job_tag="br_csv")
    dest_file = dest_dir / "br_child_asin.csv"
    warning = ""
    artifact = ""
    nav_warnings: list[str] = []

    # 1) 已在子 ASIN 页则跳过重复导航
    body = page.inner_text("body")
    try:
        if not _on_br_page(body, page.url):
            navigate_to_br_child_asin(page, home_url=HOME_URL)
            body = page.inner_text("body")
        if looks_login_page(body, page.url):
            warning = "LOGIN_PAGE"
        elif _on_br_page(body, page.url):
            rows, artifact, dl_warning = _try_download_br_csv(
                page, store_name=store_name, dest_file=dest_file, period=period
            )
            if rows:
                return BusinessReportCsvResult(
                    rows=rows,
                    source="br_csv",
                    artifact=artifact,
                    duration_ms=int((time.time() - started) * 1000),
                    warning="",
                    page_url=page.url,
                )
            warning = dl_warning or warning
        else:
            nav_warnings.append("NAV_NOT_BR")
    except RuntimeError as exc:
        nav_warnings.append(str(exc))
    except Exception as exc:
        nav_warnings.append(exc.__class__.__name__)

    # 2) 备用：仅子 ASIN 相关 URL
    fallback_urls = [u for u in REPORT_URLS if "DetailSalesTrafficByChild" in u] or [REPORT_URLS[0]]
    for url in fallback_urls:
        try:
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)
            if is_blocked_url(page.url):
                nav_warnings.append(f"BLOCKED:{page.url}")
                continue
            assert_allowed_url(page.url, context="br_goto")
            body = page.inner_text("body")
            if looks_login_page(body, page.url):
                warning = "LOGIN_PAGE"
                break
            if not _on_br_page(body, page.url):
                continue
            rows, artifact, dl_warning = _try_download_br_csv(
                page, store_name=store_name, dest_file=dest_file, period=period
            )
            if rows:
                return BusinessReportCsvResult(
                    rows=rows,
                    source="br_csv",
                    artifact=artifact,
                    duration_ms=int((time.time() - started) * 1000),
                    warning="",
                    page_url=page.url,
                )
            warning = dl_warning or warning
        except RuntimeError as exc:
            nav_warnings.append(str(exc))
        except Exception:
            continue

    combined = warning or "ZERO_ROWS"
    if nav_warnings:
        combined = f"{combined}|{'|'.join(nav_warnings[:3])}"
    return BusinessReportCsvResult(
        rows=[],
        source="br_csv",
        artifact=artifact,
        duration_ms=int((time.time() - started) * 1000),
        warning=combined,
        page_url=page.url if page.url else HOME_URL,
    )
