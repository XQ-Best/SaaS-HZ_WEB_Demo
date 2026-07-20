"""Amazon 同步采集配置（环境变量）。"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def report_period_days() -> int:
    raw = os.getenv("AMAZON_REPORT_PERIOD_DAYS", "7").strip()
    try:
        value = int(raw)
    except ValueError:
        value = 7
    return max(1, min(value, 90))


def br_dom_fallback_enabled() -> bool:
    return os.getenv("AMAZON_BR_DOM_FALLBACK", "0").strip().lower() in ("1", "true", "yes")


def inventory_dom_fallback_enabled() -> bool:
    return os.getenv("AMAZON_INV_DOM_FALLBACK", "1").strip().lower() in ("1", "true", "yes")


def ads_dom_fallback_enabled() -> bool:
    return os.getenv("AMAZON_ADS_DOM_FALLBACK", "1").strip().lower() in ("1", "true", "yes")


def download_root() -> Path:
    raw = os.getenv("AMAZON_DOWNLOAD_DIR", str(ROOT / "data" / "amazon-downloads")).strip()
    return Path(raw)


def csv_retention_hours() -> int:
    raw = os.getenv("AMAZON_CSV_RETENTION_HOURS", "24").strip()
    try:
        return max(1, int(raw))
    except ValueError:
        return 24
