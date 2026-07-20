# Amazon 产品 TOP20 — PRD 实施包（V4）

> **版本**：v4.0  
> **日期**：2026-07-13  
> **读者**：研发、测试、运维  
> **依赖**：[15-需求分析](./15-TOP20分源采集-需求分析.md) · [16-技术方案](./16-TOP20分源采集-技术方案.md) · [18-测试用例](./18-TOP20分源采集-测试用例.md)

---

## 里程碑总览

| 阶段 | 范围 | 工期估 | 阻塞发布 |
|------|------|--------|----------|
| **TOP-P0** | BR CSV + 合成链路 + 去 DOM 主路径 | 2～3 天 | 是 |
| **TOP-P1** | 库存 CSV + 广告 ASIN CSV + ACOS 阈值 | 2～3 天 | 是 |
| **TOP-P2** | XHR 降级 + data_quality + 审计脚本 | 1～2 天 | 是 |
| **TOP-P3** | SP-API 库存备选 + `scope=products` | 2～3 天 | 否 |

**发布闸门**：TOP-P0 + TOP-P1 + TOP-P2 完成，且 [18-测试用例](./18-TOP20分源采集-测试用例.md) **TOP-P0 / TOP-P1** 全 PASS。

---

## TOP-P0：Business Report CSV（必须先做）

### Python — 新增

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| PY-T01 | `DownloadResult` + `save_download` 工具 | `sources/download_helper.py` | ☑ |
| PY-T02 | BR 页导航：7 日 + Apply + Download | `sources/business_report_csv.py` | ☑ |
| PY-T03 | BR CSV 解析 + 列名映射 | `parsers/csv_br.py` | ☑ |
| PY-T04 | 单测：夹具 CSV → 标准 `BrRow` | `tests/fixtures/br_child_asin_7d.csv` + `test_csv_br.py` | ☑ |
| PY-T05 | `crawl_pipeline` reports 改调 CSV 源 | `crawl_pipeline.py` | ☑ |
| PY-T06 | DOM `crawl_business_report` 标记 deprecated，默认不调用 | `crawlers/business_report.py` | ☑ |
| PY-T07 | `reports` scope 禁用 `fast` 跳过 BR | `crawl_pipeline.py` | ☑ |
| PY-T08 | `compose` 时 `order_rows=None`（reports） | `crawl_pipeline.py` | ☑ |
| PY-T09 | `period_days=7` 写入产品行 | `product_composer.py` | ☑ |
| PY-T10 | 下载目录 `.gitignore` | `backend/data/amazon-downloads/.gitignore` | ☑ |

### Python — 配置

| # | 任务 | 完成 |
|---|------|------|
| PY-T11 | `AMAZON_REPORT_PERIOD_DAYS=7` 读取 | `sources/amazon_sync_config.py` | ☑ |
| PY-T12 | `AMAZON_BR_DOM_FALLBACK=0` 默认 | `sources/amazon_sync_config.py` | ☑ |

### 数据

| # | 任务 | 完成 |
|---|------|------|
| O-T01 | 备份 `crosshub.db` | ☐ |
| O-T02 | 清空 YOTO 租户 `amazon_product_snapshot` | ☐ |
| O-T03 | Boss 触发 `scope=reports` 全量同步 | ☐ |

### P0 验收

- [ ] `revenue_30d` 非空 ≥ 80%（37 行中 ≥30）  
- [ ] `orders_30d` 与 SC BR 抽 3 ASIN 一致  
- [ ] 无新增 `br_nodata_*.png`（或仅 CSV+XHR 均失败时）  
- [ ] `pytest test_csv_br.py` PASS  

---

## TOP-P1：库存 + 广告 CSV + 前端阈值

### Python

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| PY-T13 | 库存 Export CSV 下载 | `sources/inventory_csv.py` | ☑ |
| PY-T14 | 库存 CSV 解析 | `parsers/csv_inventory.py` | ☑ |
| PY-T15 | 广告 SP ASIN 报表 CSV 下载 | `sources/ads_asin_report_csv.py` | ☑ |
| PY-T16 | 广告 CSV 解析 + merge 到 products | `parsers/csv_ads.py` + `product_composer.py` | ☑ |
| PY-T17 | 废弃 `crawl_ads_data` DOM 主路径 | `crawlers/campaign_manager.py` | ☑ |
| PY-T18 | 夹具 + 单测 `test_csv_inventory_ads.py` | `tests/` | ☑ |
| PY-T19 | `build_data_quality()` 写入 result | `crawl_pipeline.py` | ☑ |

### Java

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| J-T01 | insights 响应透传 `data_quality` | `AmazonOperationalServiceImpl.java` | ☑ |
| J-T02 | partial 状态：BR 成功、广告失败 | `AmazonSyncServiceImpl.java` | ☑ |

### Vue

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| F-T01 | ACOS 阈值 35 / 50 | `constants/amazonBoss.js` | ☑ |
| F-T02 | 展示 `data_quality` 警告条 | `AmazonProductsPanel.vue` | ☑ |
| F-T03 | insights 映射 `data_quality` | `amazonApi.js` | ☑ |

### P1 验收

- [ ] 有广告 SKU：`ad_spend_30d` 非空  
- [ ] ACOS 偏高/过高筛选有数据（存在 ≥35% SKU 时）  
- [ ] TOP20 内 `inventory` 覆盖率 ≥ 70%  
- [ ] V3 AUTH-01～08 仍 PASS（无假 ACOS 回归）  

---

## TOP-P2：XHR 降级 + 可观测性

### Python

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| PY-T20 | BR XHR 拦截解析 | `sources/business_report_xhr.py` | ☐ |
| PY-T21 | CSV 失败 → XHR 自动降级 | `crawl_pipeline.py` | ☐ |
| PY-T22 | `field_sources` 写入 product 行（可选 JSON 列） | `product_composer.py` | ☐ |
| PY-T23 | diagnostics 含 `source`/`artifact` | `diagnostics.py` | ☐ |

### 审计 / 运维

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| O-T04 | `audit_top20_field_coverage` | `scripts/audit_amazon_data_coverage.py` | ☐ |
| O-T05 | `check_amazon_pipeline.py` 检查 CSV 路径 | `scripts/` | ☐ |
| O-T06 | 文档索引更新 | `docs/amazon-integration/README.md` | ☐ |

### P2 验收

- [ ] 人为移除 Download 按钮时，XHR 降级可采到 BR 行  
- [ ] 审计脚本输出 TOP20 覆盖率表  
- [ ] job `result_summary.data_quality` 可在 API 读到  

---

## TOP-P3：增强（可选）

| # | 任务 | 完成 |
|---|------|------|
| PY-T24 | SP-API FBA Inventory 备选 | ☐ |
| PY-T25 | 新增 `scope=products`（仅三源 CSV） | ☐ |
| J-T03 | sync API 文档 `scope=products` | ☐ |
| F-T04 | 「BR 刷新」改调 `scope=products` 降耗时 | ☐ |

---

## 实施顺序（建议 7 个工作日）

```
Day 1   TOP-P0  download_helper + csv_br + 单测夹具
Day 2   TOP-P0  business_report_csv + pipeline 接入 + 联调 YOTO
Day 3   TOP-P0  验收 revenue/orders + 清库重 sync
Day 4   TOP-P1  inventory_csv + ads_csv + parser 单测
Day 5   TOP-P1  前端阈值 + data_quality + Java 透传
Day 6   TOP-P2  XHR 降级 + 审计脚本扩展
Day 7   全量回归 18-测试用例 + audit 归档 + restart-java-api
```

---

## 联调检查表（每次发布前）

```powershell
# 1. 环境
netstat -ano | findstr ":18080 :18765 :16851"
cd D:\NIUBI\SaaS-HZ_WEB_Demo\backend\python
$env:PYTHONPATH=(Get-Location)
py scripts\probe_ziniao.py

# 2. 重启 Java（有 backend/java 变更时）
powershell -File scripts\restart-java-api.ps1

# 3. Agent
# 确保 run-agent.ps1 运行，紫鸟 YOTO美国账号已登录 SC

# 4. 同步
# Boss → Amazon → Business Report 刷新（scope=reports）

# 5. 验收
py scripts\audit_amazon_data_coverage.py
py -m pytest backend\python\tests\test_csv_br.py backend\python\tests\test_amazon_parsers.py -q
```

---

## API 变更摘要

### POST `/api/amazon/sync`

新增可选 scope（P3）：

```json
{ "scope": "products", "platform_account_id": "uuid-optional" }
```

`products`：仅 BR + 库存 + 广告 CSV，不跑 daily 消息/差评。

`reports` 行为变更（P0 起）：

- 内部走 CSV 三源，不再 DOM 滚 BR 表  
- `period_days` 固定 7（可配置）  

### GET `/api/amazon/insights`

扩展字段（P1 起）：

```json
{
  "products": [...],
  "synced_at": "...",
  "data_quality": {
    "period_days": 7,
    "br_source": "csv",
    "br_rows": 42,
    "products_with_revenue": 35,
    "products_with_ad_spend": 12,
    "warnings": []
  }
}
```

---

## 文件清单（新增 / 大改）

| 路径 | 动作 |
|------|------|
| `backend/python/app/amazon/sources/*.py` | 新增 |
| `backend/python/app/amazon/parsers/csv_*.py` | 新增 |
| `backend/python/tests/fixtures/*.csv` | 新增 |
| `backend/python/tests/test_csv_*.py` | 新增 |
| `backend/python/app/amazon/crawl_pipeline.py` | 大改 |
| `backend/python/app/amazon/crawlers/business_report.py` | 降级 |
| `backend/python/app/amazon/crawlers/campaign_manager.py` | 降级 |
| `dev/vue-site/src/constants/amazonBoss.js` | 小改 |
| `dev/vue-site/src/components/amazon/AmazonProductsPanel.vue` | 小改 |
| `scripts/audit_amazon_data_coverage.py` | 扩展 |

---

## 回滚方案

| 层级 | 操作 |
|------|------|
| 紧急 | 设 `AMAZON_BR_DOM_FALLBACK=1`，恢复旧 Agent 包 |
| 数据 | 还原 `crosshub.db` 备份 |
| 前端 | 回滚 `ACOS_THRESHOLDS` 至 30/40 |
| 禁止 | 不得恢复 V3 已删除的 `allocate_account_ads_by_revenue` |

---

## PR 检查清单

- [ ] 附 `audit_amazon_data_coverage.py` 同步前后对比片段  
- [ ] 附 1 份 BR CSV 样例行数（脱敏）  
- [ ] `pytest` 新增用例 PASS  
- [ ] Java 变更已 `restart-java-api.ps1`  
- [ ] 无 `*Local.js` 回退逻辑  
