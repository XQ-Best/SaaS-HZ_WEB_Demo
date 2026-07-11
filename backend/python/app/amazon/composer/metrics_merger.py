"""Amazon 广告账户指标合并。"""
from __future__ import annotations

import re
from typing import Any


def _metric_text(metrics: list[dict[str, Any]], metric_key: str) -> str:
    for item in metrics or []:
        if isinstance(item, dict) and item.get("metric_key") == metric_key:
            return str(item.get("value_text") or "").strip()
    return ""


def coalesce_ads_summary(
    ads_summary: dict[str, Any] | None,
    metrics: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    """合并广告页摘要与首页/账户级 ad 指标，供 SKU 分摊使用。"""
    summary = dict(ads_summary or {})
    spend_text = _metric_text(metrics or [], "ad_spend_today")
    if spend_text and not summary.get("ad_spend_30d"):
        match = re.search(r"([\d,]+\.?\d*)", spend_text)
        if match:
            summary["ad_spend_30d"] = match.group(1).replace(",", "")
    acos_text = _metric_text(metrics or [], "ad_acos_snapshot")
    if acos_text and not summary.get("acos"):
        match = re.search(r"([\d.]+)", acos_text)
        if match:
            summary["acos"] = match.group(1)
    return summary


def merge_ads_metrics(metrics: list[dict[str, Any]], ads_summary: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(ads_summary, dict):
        return metrics
    merged = list(metrics)
    seen = {item.get("metric_key") for item in merged if isinstance(item, dict)}
    spend = ads_summary.get("ad_spend_30d") or ads_summary.get("adSpend30d")
    if spend and "ad_spend_today" not in seen:
        merged.append(
            {
                "metric_key": "ad_spend_today",
                "metric_label": "广告花费（广告后台）",
                "value_text": f"US${spend}",
                "threshold_text": "",
                "status": "normal",
                "trend": "stable",
                "note_text": "来自广告活动页",
            }
        )
    acos = ads_summary.get("acos")
    if acos and "ad_acos_snapshot" not in seen:
        merged.append(
            {
                "metric_key": "ad_acos_snapshot",
                "metric_label": "广告 ACOS",
                "value_text": f"{acos}%",
                "threshold_text": "",
                "status": "normal",
                "trend": "stable",
                "note_text": "来自广告活动页",
            }
        )
    return merged
