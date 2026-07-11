#!/usr/bin/env python3
"""Amazon 运营侧全量数据覆盖审查（非抽样）。"""
from __future__ import annotations

import json
import sqlite3
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "backend" / "data" / "crosshub.db"
JAVA = "http://127.0.0.1:18080"
LOGIN = {"account": "HangZhouYiTuo", "password": "HangZhouYiTuo", "portalRole": "boss"}

FEATURES = [
    {
        "id": "products_top20",
        "ui": "Boss · 产品 TOP20",
        "api": "GET /api/amazon/insights → products",
        "scope": "reports",
        "table": "amazon_product_snapshot",
    },
    {
        "id": "outbound_orders",
        "ui": "订单发货",
        "api": "GET /api/amazon/insights → outbound_orders",
        "scope": "reports",
        "table": "amazon_operational_item[outbound_order]",
    },
    {
        "id": "account_metrics",
        "ui": "账户状况",
        "api": "GET /api/amazon/daily → account_metrics",
        "scope": "account_health | reports(daily 叠加)",
        "table": "amazon_account_metric",
    },
    {
        "id": "buyer_messages",
        "ui": "买家消息",
        "api": "GET /api/amazon/daily → buyer_messages",
        "scope": "daily",
        "table": "amazon_operational_item[buyer_message]",
    },
    {
        "id": "reviews",
        "ui": "差评处理",
        "api": "GET /api/amazon/daily → reviews",
        "scope": "daily",
        "table": "amazon_operational_item[review]",
    },
    {
        "id": "coupons",
        "ui": "优惠券",
        "api": "GET /api/amazon/daily → coupons",
        "scope": "daily | reports",
        "table": "amazon_operational_item[coupon]",
    },
    {
        "id": "seller_news",
        "ui": "卖家资讯",
        "api": "GET /api/amazon/daily → seller_news",
        "scope": "daily",
        "table": "amazon_operational_item[seller_news]",
    },
    {
        "id": "shipments",
        "ui": "入库货件",
        "api": "GET /api/amazon/daily → shipments",
        "scope": "daily | reports",
        "table": "amazon_operational_item[shipment]",
    },
    {
        "id": "cases",
        "ui": "Case 工单",
        "api": "GET /api/amazon/daily → cases",
        "scope": "daily",
        "table": "amazon_operational_item[case]",
    },
    {
        "id": "boss_overview",
        "ui": "Boss 总览卡片",
        "api": "operationsOverview buildAmazonSection",
        "scope": "daily + insights",
        "table": "聚合",
    },
]

PRODUCT_FIELDS = [
    ("product_name", "商品名", "非空且非 ASIN"),
    ("asin", "ASIN", "10 位"),
    ("orders_30d", "7日订单", ">0"),
    ("revenue_30d", "7日销售额", "非空"),
    ("page_views", "会话", ">0"),
    ("ad_spend_30d", "广告花费", "非空"),
    ("acos", "ACOS", ">0"),
    ("tacos", "TACoS", ">0"),
    ("conversion_rate", "转化率", ">0"),
    ("inventory", "FBA库存", ">=0 有值"),
]


def api_get(path: str, token: str) -> dict:
    req = urllib.request.Request(
        f"{JAVA}{path}",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode())
    return body.get("data") or body


def login() -> str:
    req = urllib.request.Request(
        f"{JAVA}/api/auth/login",
        data=json.dumps(LOGIN).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = json.loads(resp.read().decode())
    return (body.get("data") or body)["token"]


def is_real_name(name: str, asin: str) -> bool:
    text = (name or "").strip()
    if not text or text.upper() == (asin or "").upper():
        return False
    if text.startswith("US$") or text.startswith("$"):
        return False
    return True


def field_filled(row: dict, field: str) -> bool:
    val = row.get(field)
    if field == "product_name":
        return is_real_name(str(val or ""), str(row.get("asin") or ""))
    if field in {"orders_30d", "page_views", "inventory"}:
        try:
            return int(val or 0) > 0
        except (TypeError, ValueError):
            return False
    if field in {"acos", "tacos", "conversion_rate"}:
        try:
            return float(val or 0) > 0
        except (TypeError, ValueError):
            return False
    if field == "revenue_30d":
        return bool(str(val or "").strip())
    if field == "ad_spend_30d":
        return bool(str(val or "").strip())
    return bool(val)


def main() -> int:
    if not DB.exists():
        print(f"DB missing: {DB}", file=sys.stderr)
        return 2

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    print("=" * 72)
    print("Amazon 运营侧 · 全量数据覆盖审查")
    print("=" * 72)

    accounts = conn.execute(
        """
        SELECT id, tenant_id, store_name, external_shop_id, amazon_merchant_id, bound_at
        FROM platform_account
        WHERE lower(platform)='amazon'
        ORDER BY bound_at DESC
        """
    ).fetchall()
    print(f"\n[店铺] 共 {len(accounts)} 个 Amazon platform_account：")
    for acc in accounts:
        print(
            f"  - {acc['store_name']} | id={acc['id']} | browserId={acc['external_shop_id']} "
            f"| merchantId={acc['amazon_merchant_id'] or '(空)'}"
        )

    tenant_ids = sorted({acc["tenant_id"] for acc in accounts})
    missing_features: list[dict] = []

    # --- sync jobs per scope ---
    print("\n[同步任务] 各 scope 最近一次：")
    for scope in ("account_health", "daily", "reports", "insights"):
        job = conn.execute(
            """
            SELECT id, status, finished_at, error_message, result_summary
            FROM amazon_sync_job
            WHERE scope=?
            ORDER BY finished_at DESC
            LIMIT 1
            """,
            (scope,),
        ).fetchone()
        if job:
            summary = {}
            try:
                summary = json.loads(job["result_summary"] or "{}")
            except json.JSONDecodeError:
                pass
            err = (job["error_message"] or "")[:80]
            print(
                f"  {scope:16} {job['status']:8} @ {job['finished_at']} "
                f"products={summary.get('products_count', '-')} orders={summary.get('orders_count', '-')} {err}"
            )
        else:
            print(f"  {scope:16} (无记录)")
            missing_features.append({
                "feature": f"sync:{scope}",
                "ui": f"scope={scope} 从未同步",
                "count": 0,
                "reason": "无 amazon_sync_job 记录",
            })

    # --- account metrics full list ---
    metrics = conn.execute(
        """
        SELECT metric_key, metric_label, value_text, status, synced_at, platform_account_id
        FROM amazon_account_metric
        ORDER BY synced_at DESC, metric_key
        """
    ).fetchall()
    print(f"\n[账户状况] amazon_account_metric 全量 {len(metrics)} 条：")
    for row in metrics:
        print(f"  {row['metric_key']:24} {row['value_text']:18} ({row['status']})")

    home_open_orders = next(
        (r["value_text"] for r in metrics if r["metric_key"] == "open_orders"),
        "",
    )

    # --- operational items by type (full) ---
    print("\n[运营列表] amazon_operational_item 按类型全量：")
    item_types = conn.execute(
        """
        SELECT item_type, COUNT(*) AS c,
               MAX(synced_at) AS last_sync
        FROM amazon_operational_item
        GROUP BY item_type
        ORDER BY item_type
        """
    ).fetchall()
    item_counts = {r["item_type"]: r["c"] for r in item_types}
    for row in item_types:
        print(f"  {row['item_type']:16} count={row['c']:4} last_sync={row['last_sync']}")

    outbound_status = conn.execute(
        """
        SELECT json_extract(payload_json, '$.status') AS status, COUNT(*) AS c
        FROM amazon_operational_item
        WHERE item_type='outbound_order'
        GROUP BY status
        """
    ).fetchall()
    if outbound_status:
        print("  outbound 状态分布:", {r["status"]: r["c"] for r in outbound_status})

    # --- products full audit ---
    products = conn.execute(
        """
        SELECT asin, product_name, sku, orders_30d, revenue_30d, page_views,
               ad_spend_30d, acos, tacos, conversion_rate, inventory,
               period_days, synced_at, platform_account_id
        FROM amazon_product_snapshot
        ORDER BY rank_no ASC, synced_at DESC
        """
    ).fetchall()
    print(f"\n[产品 TOP20] amazon_product_snapshot 全量 {len(products)} 行：")
    field_stats = {f[0]: 0 for f in PRODUCT_FIELDS}
    sku_gaps: list[dict] = []
    for row in products:
        missing_cols = [label for key, label, _ in PRODUCT_FIELDS if not field_filled(dict(row), key)]
        for key, _, _ in PRODUCT_FIELDS:
            if field_filled(dict(row), key):
                field_stats[key] += 1
        flag = "OK" if not missing_cols else f"缺: {', '.join(missing_cols)}"
        print(
            f"  {row['asin']} | {(row['product_name'] or '')[:36]:36} | "
            f"ord={row['orders_30d']:3} rev={str(row['revenue_30d'] or '-'):10} "
            f"ad={str(row['ad_spend_30d'] or '-'):8} acos={row['acos']} conv={row['conversion_rate']} | {flag}"
        )
        if missing_cols:
            sku_gaps.append({"asin": row["asin"], "missing": missing_cols})

    print("\n[产品字段覆盖率]（全量 SKU，非 TOP20 抽样）：")
    total = len(products) or 1
    for key, label, rule in PRODUCT_FIELDS:
        filled = field_stats[key]
        pct = round(filled / total * 100, 1)
        print(f"  {label:10} ({key:18}) {filled:3}/{total} = {pct}%")
        if filled == 0:
            missing_features.append({
                "feature": f"products.{key}",
                "ui": f"产品 TOP20 · {label}",
                "count": 0,
                "reason": f"全部 {total} 个 SKU 的 {label} 为空 — 需 scope=reports + 对应页面解析",
            })

    # --- feature-level pass/fail ---
    print("\n[功能模块] 全量审查结果：")
    feature_checks = {
        "products_top20": len(products),
        "outbound_orders": item_counts.get("outbound_order", 0),
        "account_metrics": len(metrics),
        "buyer_messages": item_counts.get("buyer_message", 0),
        "reviews": item_counts.get("review", 0),
        "coupons": item_counts.get("coupon", 0),
        "seller_news": item_counts.get("seller_news", 0),
        "shipments": item_counts.get("shipment", 0),
        "cases": item_counts.get("case", 0),
    }

    for feat in FEATURES:
        fid = feat["id"]
        if fid == "boss_overview":
            count = "聚合"
            ok = feature_checks["account_metrics"] > 0
        else:
            count = feature_checks.get(fid, 0)
            ok = count > 0 if fid != "products_top20" else count >= 1
        status = "有数据" if ok else "无数据"
        print(f"  [{status:4}] {feat['ui']:12} | 记录数={count} | scope={feat['scope']}")
        if not ok:
            missing_features.append({
                "feature": fid,
                "ui": feat["ui"],
                "count": count,
                "reason": _missing_reason(fid, conn),
            })

    # --- API cross-check (full arrays) ---
    print("\n[API 交叉验证] Java 返回条数（Boss token）：")
    try:
        token = login()
        daily = api_get("/api/amazon/daily", token)
        insights = api_get("/api/amazon/insights", token)
        api_counts = {
            "daily.account_metrics": len(daily.get("account_metrics") or []),
            "daily.buyer_messages": len(daily.get("buyer_messages") or []),
            "daily.reviews": len(daily.get("reviews") or []),
            "daily.coupons": len(daily.get("coupons") or []),
            "daily.seller_news": len(daily.get("seller_news") or []),
            "daily.shipments": len(daily.get("shipments") or []),
            "daily.cases": len(daily.get("cases") or []),
            "insights.products": len(insights.get("products") or []),
            "insights.outbound_orders": len(insights.get("outbound_orders") or []),
        }
        for key, val in api_counts.items():
            print(f"  {key:28} {val}")
            if val == 0 and not key.endswith("buyer_messages"):
                # buyer_messages=0 may be valid if home says 0
                if key == "daily.buyer_messages" and home_open_orders == "0":
                    continue
    except Exception as exc:  # noqa: BLE001
        print(f"  API 验证失败: {exc}")

    # --- 未抓取成功清单 ---
    print("\n" + "=" * 72)
    print("数据未抓取成功 / 未覆盖清单（全量）")
    print("=" * 72)
    if not missing_features and not sku_gaps:
        print("  (无 — 所有模块与 SKU 字段均有数据)")
    else:
        seen = set()
        for item in missing_features:
            key = item["feature"]
            if key in seen:
                continue
            seen.add(key)
            print(f"\n  ■ {item['ui']}")
            print(f"    功能ID: {item['feature']}")
            print(f"    当前记录数: {item['count']}")
            print(f"    原因: {item['reason']}")

        if sku_gaps:
            print(f"\n  ■ 产品 SKU 级字段缺口（共 {len(sku_gaps)} 个 SKU 至少缺 1 列）")
            by_field: dict[str, list[str]] = defaultdict(list)
            for gap in sku_gaps:
                for col in gap["missing"]:
                    by_field[col].append(gap["asin"])
            for col, asins in sorted(by_field.items(), key=lambda x: -len(x[1])):
                print(f"    - {col}: {len(asins)} 个 SKU 缺失 → {', '.join(asins)}")

    # reconciliation
    outbound_total = item_counts.get("outbound_order", 0)
    if home_open_orders and outbound_total:
        try:
            home_n = int(str(home_open_orders).replace(",", ""))
            if home_n > 0 and outbound_total < home_n * 0.5:
                print(f"\n  ■ 订单对账异常")
                print(f"    首页 open_orders={home_n}，但 outbound_orders 仅 {outbound_total}")
                print(f"    原因: orders-v3 分页/子页未全量采集，或最近 reports sync 失败")
        except ValueError:
            pass

    print()
    return 0


def _missing_reason(feature_id: str, conn: sqlite3.Connection) -> str:
    reasons = {
        "buyer_messages": "scope=daily 未跑或 /messaging/inbox 解析 0 行；首页 buyer_messages=0 时可能确实无待办",
        "reviews": "scope=daily 未跑或 /feedback-manager 仅抓 1-3 星；无差评时可能为 0",
        "coupons": "scope=daily/reports 未跑或促销页 DOM 未匹配",
        "seller_news": "scope=daily 未跑或首页卖家资讯卡片未解析",
        "shipments": "scope=daily/reports 未跑或 FBA 入库页未解析",
        "cases": "scope=daily 未跑或首页 Case 卡片未解析",
        "products_top20": "scope=reports 失败或未跑；最近 success 在 13:17 之前",
    }
    if feature_id in reasons:
        return reasons[feature_id]

    last_reports = conn.execute(
        """
        SELECT status, error_message FROM amazon_sync_job
        WHERE scope='reports' ORDER BY finished_at DESC LIMIT 1
        """
    ).fetchone()
    if last_reports and last_reports["status"] != "success":
        return f"最近 reports sync {last_reports['status']}: {(last_reports['error_message'] or '')[:120]}"
    return "需检查对应页面 URL / 解析器 / 紫鸟 WebDriver 是否在线"


if __name__ == "__main__":
    raise SystemExit(main())
