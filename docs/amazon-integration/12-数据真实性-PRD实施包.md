# Amazon 运营数据真实性 — PRD 实施包（V3）

> **版本**：v3.0  
> **日期**：2026-07-13  
> **读者**：研发、测试、运维  
> **依赖**：[10-数据真实性-需求方案.md](./10-数据真实性-需求方案.md) · [11-数据真实性-技术设计.md](./11-数据真实性-技术设计.md) · [13-数据真实性-测试用例.md](./13-数据真实性-测试用例.md)

---

## 里程碑总览

| 阶段 | 范围 | 工期估 | 阻塞发布 |
|------|------|--------|----------|
| **AUTH-P0** | 下架造假逻辑 + UI 诚实化 | 1～2 天 | 是 |
| **AUTH-P1** | BR / 库存 / 广告解析修复 | 3～5 天 | 是 |
| **AUTH-P2** | `scope=full` 单任务 + 登录同步策略 | 2～3 天 | 是 |
| **AUTH-P3** | provenance + 平台 snapshot 新鲜度（可选） | 2～3 天 | 否 |

**发布闸门**：AUTH-P0 + AUTH-P1 + AUTH-P2 全部完成，且 [13-测试用例](./13-数据真实性-测试用例.md) 中 **AUTH-*** P0 全 PASS。

---

## AUTH-P0：禁止造假（必须先做）

### Python

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| PY-A01 | 删除 `crawl_pipeline` 对 `allocate_account_ads_by_revenue` 的调用 | `crawl_pipeline.py` | ☑ |
| PY-A02 | `allocate_account_ads_by_revenue` 标 `@deprecated` 或删除 | `product_composer.py` | ☑ |
| PY-A03 | `enrich_product_rows`：去掉 `tacos=acos`；tacos 仅 derived | `product_composer.py` | ☑ |
| PY-A04 | 删除 `enrich_from_related_inventory` 名称 fuzzy 逻辑 | `product_composer.py` | ☑ |
| PY-A05 | `merge_campaign_ads` 去掉 `len(merged)==1` 兜底匹配 | `product_composer.py` | ☑ |
| PY-A06 | 删除/改写 `test_allocate_ads_from_acos_only` | `test_amazon_parsers.py` | ☑ |
| PY-A07 | 新增 `test_no_synthetic_acos_on_products` | `test_amazon_parsers.py` | ☑ |

### Java

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| J-A01 | 确认入库不二次计算 acos/tacos | `AmazonOperationalPersistenceServiceImpl.java` | ☑ |
| J-A02 | `normalizeScope` 预留 `full`（可先透传） | `AmazonSyncServiceImpl.java` | ☑ |

### Vue

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| F-A01 | `mapProduct`：`profitMargin` 不默认 0 | `amazonApi.js` | ☑ |
| F-A02 | 产品表隐藏「利润率」列 | `AmazonProductsPanel.vue` | ☑ |
| F-A03 | ACOS/花费为 0 显示 `—` + tooltip | `AmazonProductsPanel.vue` | ☑ |
| F-A04 | 收紧 `hasAdData` 判定：需真实 spend>0 | `amazonBoss.js` | ☑ |

### 审计

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| O-A01 | `audit_amazon_data_coverage.py` 增加 `audit_synthetic_acos` | `scripts/` | ☑ |
| O-A02 | 文档索引更新 | `docs/amazon-integration/README.md` | ☐ |

### P0 验收

- [ ] 同步后不再出现 39/39 相同 ACOS（除非人工确认后台一致）
- [ ] `ad_spend` 不再严格等于 `revenue × 固定比例`
- [ ] 产品表无利润率 0% 列
- [ ] `pytest test_amazon_parsers.py` PASS

---

## AUTH-P1：真实数据采集修复

### Python 解析

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| PY-B01 | BR 表头映射：sessions、conversion、完整标题列 | `parsers/seller_pages.py` | ☐ |
| PY-B02 | 库存页按 ASIN merge，输出 `page_views` 仅当同行有 | `crawlers/inventory.py` | ☐ |
| PY-B03 | Campaign Manager SKU spend 解析加强 | `parsers/seller_pages.js` / `campaign_manager.py` | ☐ |
| PY-B04 | `compose_product_rows` 仅 ASIN 键合并 catalog | `product_composer.py` | ☐ |
| PY-B05 | `data_quality` 写入 `result_summary` | `crawl_pipeline.py` | ☐ |
| PY-B06 | 商品名截断回归用例（B08B8X3Q6C 等） | `test_amazon_parsers.py` | ☐ |

### 数据清理

| # | 任务 | 完成 |
|---|------|------|
| O-B01 | 备份 `crosshub.db` | ☐ |
| O-B02 | 删除租户 Amazon `product_snapshot` 脏行 | ☐ |
| O-B03 | 触发 `scope=reports` 或 `full` 全量同步 | ☐ |
| O-B04 | 跑 `audit_amazon_data_coverage.py` 截图归档 | ☐ |

### P1 验收

- [ ] `page_views` 覆盖率 ≥ 80%（BR 成功时）
- [ ] `inventory` 覆盖率 ≥ 80%
- [ ] 有广告 SKU 的 `ad_spend` 来自 Campaign Manager（人工抽 3 ASIN）
- [ ] 商品名无大面积截断（`ter Bass Tr` 类 < 5%）

---

## AUTH-P2：单任务全量同步

### Python

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| PY-C01 | `page_registry` 增加 `full` scope | `page_registry.py` | ☐ |
| PY-C02 | `scope_planner.normalize_scope` 支持 `full` | `scope_planner.py` | ☐ |
| PY-C03 | `run_crawl` 按 §5 页序执行 | `crawl_pipeline.py` | ☐ |

### Java

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| J-C01 | `NEEDS_PRODUCT_ROWS` 含 `full` | `AmazonSyncServiceImpl.java` | ☐ |
| J-C02 | insights API 附带最近 job `data_quality` | `AmazonOperationalServiceImpl.java` | ☐ |

### Vue

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| F-C01 | `refreshAmazonAllWithSync` → 单次 `scope=full` | `amazonApi.js` | ☐ |
| F-C02 | `platformSync.syncAmazonStores` 新鲜度 gated（有数据则跳过） | `platformSync.js` | ☐ |
| F-C03 | 打开 Amazon 页不触发 crawl（保持 `refresh=false`） | `AmazonModuleView.vue` | ☐ |

### P2 验收

- [ ] 「一键刷新」只产生 **1** 个 `amazon_sync_job`（非 daily+reports 两个）
- [ ] 登录自动同步在 5h 内有 snapshot 时不 crawl
- [ ] `full` 同步 `page_diagnostics` 含全部关键页

---

## AUTH-P3：可观测性增强（可选）

| # | 任务 | 完成 |
|---|------|------|
| J-D01 | migration `field_sources_json` on `amazon_product_snapshot` | ☐ |
| J-D02 | `platform_snapshot` 表（tenant+platform TTL） | ☐ |
| F-D04 | UI 展示 `snapshot_id` + 同步时间 | ☐ |
| F-D05 | Boss 设置页展示最近 `page_diagnostics` 摘要 | ☐ |

---

## 实施顺序

```
Day 1   AUTH-P0  Python 下架 + pytest + 前端隐藏利润率
Day 2   AUTH-P0  审计脚本 + 清库 + 验证「不再假 ACOS」
Day 3-5 AUTH-P1  BR/库存/广告解析 + 全量同步
Day 6-7 AUTH-P2  full scope + 前端单 job + platformSync 新鲜度
Day 8   全量回归 13-测试用例 P0 + audit 脚本
```

---

## 联调检查表（每次发布前）

```powershell
# 环境
netstat -ano | findstr ":18080 :18765 :16851"
py scripts\probe_ziniao.py

# 服务
powershell -File scripts\restart-java-api.ps1
py backend\python\agent\main.py   # 或既有启动方式

# 同步
# Boss 登录 → Amazon → 一键刷新（full）

# 验收
py scripts\audit_amazon_data_coverage.py
py -m pytest backend\python\tests\test_amazon_parsers.py -q
```

---

## API 变更摘要

### POST `/api/amazon/sync`

新增合法 `scope` 值：

```json
{ "scope": "full", "platform_account_id": "optional-uuid" }
```

`full` 行为：单次 Agent 任务采集 account_health + daily + reports 全集。

**废弃（前端不再发送）**：并行两次 sync `daily` + `reports`。

### GET `/api/amazon/insights`（P2+）

响应可选扩展：

```json
{
  "products": [...],
  "outbound_orders": [...],
  "synced_at": "2026-07-13 10:00:00",
  "data_quality": {
    "products_with_real_ad_spend": 12,
    "products_with_sessions": 35,
    "synthetic_fields_blocked": true
  }
}
```

---

## 回滚方案

| 层级 | 回滚 |
|------|------|
| Python Agent | 恢复上一版 wheel / 进程；**不建议**恢复 `allocate_account_ads` |
| Java | 回滚 JAR；`full` scope 未识别时忽略 |
| Vue | 回滚 dist；利润率列恢复隐藏即可 |
| 数据 | 从备份 `crosshub.db` 还原；或重跑 full sync |

---

## 原则（再次强调）

1. **宁可空，不可假**  
2. 后端模式 **禁止** Local Demo 回退  
3. 所有 PR 必须附 `audit_amazon_data_coverage.py` 输出片段  
4. Java 变更后 **必须** `restart-java-api.ps1`
