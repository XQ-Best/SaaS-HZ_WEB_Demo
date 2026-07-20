"""Sponsored Products ASIN 广告报表 CSV 下载。"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.amazon.navigation_guard import click_scoped
from app.amazon.page_urls import ADS_CAMPAIGN_MANAGER_BASE, HOME_URL, build_ads_urls
from app.amazon.parsers.csv_ads import parse_ads_asin_csv
from app.amazon.session_context import looks_login_page, resolve_merchant_id, save_capture
from app.amazon.sources.click_export import click_download_csv
from app.amazon.sources.download_helper import build_download_dir, save_download


@dataclass
class AdsAsinCsvResult:
    rows: list[dict[str, Any]]
    source: str
    artifact: str
    duration_ms: int
    warning: str
    page_url: str
    merchant_id: str


def _ads_report_urls(merchant_id: str) -> list[str]:
    urls = [
        "https://sellercentral.amazon.com/ads/reports",
        "https://sellercentral.amazon.com/ads/campaigns",
        *build_ads_urls(merchant_id),
        "https://advertising.amazon.com/reports",
        ADS_CAMPAIGN_MANAGER_BASE,
    ]
    seen: set[str] = set()
    ordered: list[str] = []
    for item in urls:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


ADS_REPORTS_HISTORY_URL = "https://advertising.amazon.com/reports"

_ADVERTISED_PRODUCT_RE = re.compile(
    r"advertised\s*product|推广的产品|已推广产品|已推广商品|推广的商品|advertised\s*asin|按\s*asin",
    re.I,
)
_SEARCH_TERM_RE = re.compile(r"搜索词|search\s*term", re.I)

_FIND_ADS_DOWNLOAD_JS = """
() => {
  const wanted = /advertised\\s*product|推广的产品|已推广产品|已推广商品|推广的商品|advertised\\s*asin|按\\s*asin/i;
  const blocked = /搜索词|search\\s*term/i;
  const out = [];
  const seen = new Set();
  const contextText = (node) => {
    let el = node;
    for (let i = 0; i < 6 && el; i += 1) {
      const text = (el.innerText || '').replace(/\\s+/g, ' ').trim();
      if (text.length > 12) return text.slice(0, 400);
      el = el.parentElement;
    }
    return '';
  };
  for (const dl of document.querySelectorAll('a[href*="download-report"]')) {
    const href = dl.href || dl.getAttribute('href') || '';
    if (!href || seen.has(href)) continue;
    const text = contextText(dl);
    if (!text || blocked.test(text)) continue;
    if (!wanted.test(text)) continue;
    seen.add(href);
    out.push({ href, text: text.slice(0, 160) });
  }
  return out;
}
"""


def _try_download_ads_report_history(page, dest_file: Path) -> Path | None:
    """从广告报告历史页下载最近的「推广的产品 / Advertised product」报表。"""
    page.goto(ADS_REPORTS_HISTORY_URL, wait_until="domcontentloaded", timeout=60_000)
    page.wait_for_timeout(5000)
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass
    body = page.inner_text("body")
    if looks_login_page(body, page.url):
        return None
    candidates = page.evaluate(_FIND_ADS_DOWNLOAD_JS)
    if not isinstance(candidates, list) or not candidates:
        return None
    href = str(candidates[0].get("href") or "")
    if not href:
        return None
    if href.startswith("/"):
        href = f"https://advertising.amazon.com{href}"

    def _click_download() -> None:
        clicked = page.evaluate(
            """
            (url) => {
              const target = [...document.querySelectorAll('a[href*="download-report"]')].find((a) => {
                const h = a.href || a.getAttribute('href') || '';
                return h === url || h.endsWith(url.replace('https://advertising.amazon.com', ''));
              });
              if (target) { target.click(); return true; }
              const a = document.createElement('a');
              a.href = url;
              a.download = '';
              a.click();
              return true;
            }
            """,
            href,
        )
        if not clicked:
            raise RuntimeError("ads download link click failed")

    download = save_download(
        page,
        _click_download,
        dest_file,
        timeout_ms=90_000,
        source="ads_history",
    )
    return download.path


def _prepare_ads_report_page(page, *, period_days: int) -> None:
    period_re = (
        r"last\s*7|最近\s*7|7\s*days?"
        if period_days <= 7
        else r"last\s*30|最近\s*30|30\s*days?"
    )
    click_scoped(page, r"sponsored\s*products|商品推广|sp\b", kinds="button, a, kat-tab, [role='tab'], label, span")
    page.wait_for_timeout(800)
    click_scoped(page, r"advertised\s*product|广告产品|asin|按\s*asin", kinds="button, a, kat-tab, [role='tab'], label, span, option")
    page.wait_for_timeout(800)
    click_scoped(page, period_re, kinds="button, kat-tab, kat-button, kat-option, [role='tab'], [role='option'], label, li, span")
    page.wait_for_timeout(800)
    click_scoped(
        page,
        r"create\s*report|生成报告|run report|应用|apply|download|下载|export|导出",
        kinds="button, kat-button, a, [role='button']",
    )
    page.wait_for_timeout(3000)


def crawl_ads_asin_csv(
    page,
    *,
    store_name: str = "",
    merchant_id: str = "",
    download_dir: Path | None = None,
    period_days: int = 7,
) -> AdsAsinCsvResult:
    started = time.time()
    dest_dir = download_dir or build_download_dir(store_name=store_name, job_tag="ads_csv")
    dest_file = dest_dir / "ads_asin.xlsx"
    artifact = ""
    warning = ""
    resolved_merchant = merchant_id

    try:
        page.goto(HOME_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        if not resolved_merchant:
            resolved_merchant = resolve_merchant_id(page) or ""
    except Exception:
        pass

    try:
        history_path = _try_download_ads_report_history(page, dest_file)
        if history_path:
            artifact = str(history_path)
            rows = parse_ads_asin_csv(history_path)
            if rows:
                return AdsAsinCsvResult(
                    rows=rows,
                    source="ads_csv",
                    artifact=artifact,
                    duration_ms=int((time.time() - started) * 1000),
                    warning="",
                    page_url=ADS_REPORTS_HISTORY_URL,
                    merchant_id=resolved_merchant,
                )
            warning = "CSV_EMPTY"
    except Exception as exc:
        warning = f"CSV_DOWNLOAD_FAILED:{exc.__class__.__name__}"
        try:
            save_capture(page, store_name=store_name, suffix="ads_history_fail")
        except Exception:
            pass

    for url in _ads_report_urls(resolved_merchant):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            page.wait_for_timeout(6000)
            try:
                page.wait_for_load_state("networkidle", timeout=12000)
            except Exception:
                pass
            body = page.inner_text("body")
            if looks_login_page(body, page.url):
                warning = "LOGIN_PAGE"
                continue
            if not re.search(r"(campaign|广告|sponsored|report|acos|spend|花费)", body, re.I):
                continue
            if not resolved_merchant:
                resolved_merchant = resolve_merchant_id(page) or ""
            _prepare_ads_report_page(page, period_days=period_days)
            page.wait_for_timeout(4000)
            download = save_download(
                page,
                lambda: click_download_csv(page),
                dest_file,
                timeout_ms=120_000,
                source="csv",
            )
            artifact = str(download.path)
            rows = parse_ads_asin_csv(download.path)
            if rows:
                return AdsAsinCsvResult(
                    rows=rows,
                    source="ads_csv",
                    artifact=artifact,
                    duration_ms=int((time.time() - started) * 1000),
                    warning="",
                    page_url=page.url,
                    merchant_id=resolved_merchant,
                )
            warning = "CSV_EMPTY"
        except Exception as exc:
            warning = f"CSV_DOWNLOAD_FAILED:{exc.__class__.__name__}"
            try:
                save_capture(page, store_name=store_name, suffix="ads_csv_fail")
            except Exception:
                pass

    return AdsAsinCsvResult(
        rows=[],
        source="ads_csv",
        artifact=artifact,
        duration_ms=int((time.time() - started) * 1000),
        warning=warning or "ADS_CSV_EMPTY",
        page_url=page.url if page.url else _ads_report_urls(resolved_merchant)[0],
        merchant_id=resolved_merchant,
    )
