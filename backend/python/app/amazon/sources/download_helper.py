"""Playwright 文件下载辅助。"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from app.amazon.sources.amazon_sync_config import download_root


@dataclass(frozen=True)
class DownloadResult:
    path: Path
    bytes: int
    source: str
    duration_ms: int


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^\w.\-]+", "_", value.strip(), flags=re.UNICODE)
    return slug[:80] or "store"


def build_download_dir(*, store_name: str = "", job_tag: str = "") -> Path:
    stamp = time.strftime("%Y%m%d_%H%M%S")
    parts = [_safe_slug(store_name or "amazon"), stamp]
    if job_tag:
        parts.append(_safe_slug(job_tag))
    dest = download_root() / "_".join(parts)
    dest.mkdir(parents=True, exist_ok=True)
    return dest


def save_download(
    page,
    click_fn: Callable[[], None],
    dest: Path,
    *,
    timeout_ms: int = 120_000,
    source: str = "csv",
) -> DownloadResult:
    dest.parent.mkdir(parents=True, exist_ok=True)
    started = time.time()
    with page.expect_download(timeout=timeout_ms) as download_info:
        click_fn()
    download = download_info.value
    suggested = download.suggested_filename or dest.name
    if dest.suffix == "" and "." in suggested:
        dest = dest.with_suffix(Path(suggested).suffix)
    download.save_as(str(dest))
    size = dest.stat().st_size if dest.exists() else 0
    return DownloadResult(
        path=dest,
        bytes=size,
        source=source,
        duration_ms=int((time.time() - started) * 1000),
    )
