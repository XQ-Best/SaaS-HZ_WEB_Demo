"""Manage Inventory CSV 下载。"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.amazon.page_urls import INVENTORY_URLS
from app.amazon.parsers.csv_inventory import parse_inventory_csv
from app.amazon.session_context import looks_login_page, save_capture
from app.amazon.sources.click_export import click_inventory_export
from app.amazon.sources.download_helper import build_download_dir, save_download


@dataclass
class InventoryCsvResult:
    rows: list[dict[str, Any]]
    source: str
    artifact: str
    duration_ms: int
    warning: str
    page_url: str


def _inventory_page_has_export(page) -> bool:
    try:
        body = page.inner_text("body")
        if re.search(r"\bexport\b|导出", body, re.I):
            return True
        return bool(
            page.evaluate(
                """
                () => {
                  const walk = (root) => {
                    if (!root) return false;
                    for (const node of root.querySelectorAll('button, kat-button, kat-dropdown-button, a, [role="button"]')) {
                      const text = (node.innerText || node.getAttribute('label') || node.getAttribute('aria-label') || '').trim();
                      if (/^export$/i.test(text) || text === '导出') return true;
                    }
                    for (const node of root.querySelectorAll('*')) {
                      if (node.shadowRoot && walk(node.shadowRoot)) return true;
                    }
                    return false;
                  };
                  return walk(document.body);
                }
                """
            )
        )
    except Exception:
        return False


def crawl_inventory_csv(
    page,
    *,
    store_name: str = "",
    download_dir: Path | None = None,
) -> InventoryCsvResult:
    started = time.time()
    dest_dir = download_dir or build_download_dir(store_name=store_name, job_tag="inv_csv")
    dest_file = dest_dir / "inventory.csv"
    artifact = ""
    warning = ""

    for url in INVENTORY_URLS[:1]:
        try:
            page.goto(url, wait_until="domcontentloaded")
            try:
                page.wait_for_load_state("networkidle", timeout=20000)
            except Exception:
                pass
            page.wait_for_timeout(8000)
            body = page.inner_text("body")
            if looks_login_page(body, page.url):
                warning = "LOGIN_PAGE"
                break
            if not re.search(r"(inventory|库存|manage all)", body, re.I):
                continue
            if not _inventory_page_has_export(page):
                warning = "NO_EXPORT_BUTTON"
                break
            download = save_download(
                page,
                lambda: click_inventory_export(page),
                dest_file,
                timeout_ms=120_000,
                source="csv",
            )
            artifact = str(download.path)
            rows = parse_inventory_csv(download.path)
            if rows:
                return InventoryCsvResult(
                    rows=rows,
                    source="inv_csv",
                    artifact=artifact,
                    duration_ms=int((time.time() - started) * 1000),
                    warning="",
                    page_url=page.url,
                )
            warning = "CSV_EMPTY"
        except Exception as exc:
            warning = f"CSV_DOWNLOAD_FAILED:{exc.__class__.__name__}"
            try:
                save_capture(page, store_name=store_name, suffix="inv_csv_fail")
            except Exception:
                pass

    # CSV 导出失败时，从当前库存页 DOM 提取 Available 列
    try:
        from app.amazon.crawlers.inventory import crawl_inventory_products

        dom_rows = crawl_inventory_products(page, store_name=store_name, max_pages=5, fast=False)
        if dom_rows:
            return InventoryCsvResult(
                rows=dom_rows,
                source="inv_dom",
                artifact=artifact,
                duration_ms=int((time.time() - started) * 1000),
                warning=warning or "CSV_FALLBACK_DOM",
                page_url=page.url if page.url else INVENTORY_URLS[0],
            )
    except Exception:
        pass

    return InventoryCsvResult(
        rows=[],
        source="inv_csv",
        artifact=artifact,
        duration_ms=int((time.time() - started) * 1000),
        warning=warning or "ZERO_ROWS",
        page_url=page.url if page.url else INVENTORY_URLS[0],
    )
