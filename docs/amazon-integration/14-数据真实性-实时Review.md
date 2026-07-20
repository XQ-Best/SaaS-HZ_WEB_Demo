# Amazon 运营数据真实性 — 实时 Review

> **用途**：联调 / Code Review / 验收时**边测边记**；每次 Review 复制「会话记录」一节追加条目。  
> **版本**：v3.0-live  
> **基线日期**：2026-07-13  
> **PoC**：YOTO美国账号 · `browserId=16505337258263` · `merchantId=A3B69JEON4HA6`  
> **关联**：[10-需求](./10-数据真实性-需求方案.md) · [11-技术设计](./11-数据真实性-技术设计.md) · [12-实施包](./12-数据真实性-PRD实施包.md) · [13-测试用例](./13-数据真实性-测试用例.md)

---

## 0. 一句话结论（每次 Review 后更新）

| 日期 | 结论 | Review 人 |
|------|------|-----------|
| 2026-07-13 | **阻塞发布**：SKU 广告指标为账户级 40.84% 推算值；会话/库存/转化未采集；利润率列占位 0%。AUTH-P0 未落地。 | 初始诊断 |

**当前判定**：🔴 **不可用于运营决策**（ACOS/花费不可信） · 🟡 销售额/订单基本可信 · 🟡 账户状况可信

---

## 1. 实时状态看板

> 刷新命令见 §8。下表为 **2026-07-13 09:41** 快照，Review 时覆盖更新。

### 1.1 基础设施

| 组件 | 目标 | 当前 | 判定 |
|------|------|------|------|
| Java API `:18080` | LISTEN | 曾 DOWN | 🔴 需重启 |
| Agent `:18765` | `/health` → ok | ok | 🟢 |
| 紫鸟 WebDriver `:16851` | LISTEN | 未测 | ⚪ |
| Vue `:5173` | 可访问 | 未测 | ⚪ |
| `VITE_USE_TEMU_BACKEND` | true | 默认 true | 🟢 |

### 1.2 最近同步任务（`amazon_sync_job`）

| scope | 最近状态 | 时间 | 备注 |
|-------|---------|------|------|
| `account_health` | failed | 07-13 09:32 | 同步任务被中断 |
| `daily` | failed | 07-13 09:34 | 同步任务被中断 |
| `reports` | failed | 07-11 16:31 | 卖家后台未登录 |
| `insights` | failed | 07-10 11:40 | 页面未解析到数据 |
| `full` | — | — | **未实现** |

### 1.3 数据可信度（`amazon_product_snapshot` n=39）

| 字段 | 有值率 | 可信？ | 说明 |
|------|--------|--------|------|
| ASIN / 商品名 | 100% | 🟡 | 名称大量截断 |
| orders / revenue | 100% | 🟢 | BR 主路径 |
| ad_spend / acos / tacos | 100% | 🔴 | **全为账户 40.84% 推算** |
| page_views | 0% | 🔴 | 未采集 |
| conversion_rate | 0% | 🔴 | 未采集 |
| inventory | 0% | 🔴 | 未采集 |
| profit_margin（UI） | 显示 0% | 🔴 | **无数据源占位** |

### 1.4 功能模块

| 模块 | 记录数 | 数据年龄 | 判定 |
|------|--------|----------|------|
| 产品 TOP20 | 39 | ~07-11 前 | 🟡 陈旧 + 指标假 |
| 出库单 | 288 | 07-11 | 🟡 |
| 账户状况 | 16 metrics | 部分较新 | 🟢 |
| 买家消息 | 0 | — | ⚪ 可能真无 |
| 差评 | 2 | 07-11 | 🟢 |
| 优惠券 / 货件 / 资讯 | 1 / 20 / 3 | 07-10～11 | 🟡 |
| Case | 0 | — | 🔴 未采集 |

---

## 2. 造假风险 Review（AUTH 快检）

Review 时逐项打勾；**任一项 🔴 即阻塞合并**。

| # | 检查项 | 命令/方法 | 2026-07-13 | 本次 |
|---|--------|-----------|------------|------|
| A1 | 是否存在 ≥10 SKU **完全相同**非零 ACOS | `audit` / SQL `COUNT(DISTINCT acos)` | 🔴 39/39=40.84 | ☐ |
| A2 | `ad_spend/revenue` 是否**固定比率**（如 0.408） | 抽 5 行手算 | 🔴 是 | ☐ |
| A3 | 代码是否仍调用 `allocate_account_ads_by_revenue` | `rg allocate_account` | 🔴 存在 | ☐ |
| A4 | `test_allocate_ads_from_acos_only` 是否仍通过 | pytest | 🔴 存在该测例 | ☐ |
| A5 | UI 利润率列是否隐藏或全 `—` | 目视产品 Tab | 🔴 显示 0% | ☐ |
| A6 | Agent 离线是否泄漏 Demo | 停 Agent 刷新 | 待测 | ☐ |
| A7 | 后端失败是否静默 Local 回退 | 断 Java 开页 | 待测 | ☐ |

**SQL 快查（复制到 sqlite 工具）**：

```sql
-- 相同 ACOS 集中度
SELECT acos, COUNT(*) AS n FROM amazon_product_snapshot GROUP BY acos ORDER BY n DESC;

-- 固定 spend 比率
SELECT asin, revenue_30d, ad_spend_30d,
       CAST(REPLACE(REPLACE(ad_spend_30d,',',''),'US$','') AS REAL)
       / NULLIF(CAST(REPLACE(REPLACE(revenue_30d,',',''),'US$','') AS REAL),0) AS ratio
FROM amazon_product_snapshot WHERE revenue_30d != '' LIMIT 10;
```

---

## 3. 全链路 Review 检查表

按数据流从上到下；每项：**🟢通过 / 🟡部分 / 🔴失败 / ⚪未测**。

### L1 绑定与配置

| ID | 检查点 | 预期 | 2026-07-13 |
|----|--------|------|------------|
| L1-01 | `platform_account` Amazon 店铺 | ≥1，含 `external_shop_id` | 🟢 2 条 |
| L1-02 | 同 browserId 重复绑定 | 应去重或仅 1 条 | 🔴 2 条同 browserId |
| L1-03 | `amazon_merchant_id` 缓存 | 有广告页必填 | 🟡 1/2 有值 |
| L1-04 | Boss 账户绑定 UI 与 DB 一致 | 店铺名 YOTO美国账号 | 待核 |

### L2 触发与策略

| ID | 检查点 | 预期 | 2026-07-13 |
|----|--------|------|------------|
| L2-01 | 打开 Amazon 页不自动 crawl | 仅 GET | 🟢 |
| L2-02 | 登录自动同步 scope | 应 gated / full | 🔴 仅 account_health 且失败 |
| L2-03 | 一键刷新 job 数 | 1 个 full | 🔴 并行 daily+reports |
| L2-04 | 手动刷新 scope=reports | 触发 Agent | 🟡 最近失败 |

### L3 Java 任务队列

| ID | 检查点 | 预期 | 2026-07-13 |
|----|--------|------|------------|
| L3-01 | POST sync → 202 + job_id | 是 | 待测（Java DOWN） |
| L3-02 | pending→running→success | 状态机 | 🔴 多 failed/pending |
| L3-03 | 409 同 scope 冲突 | 第二次 409 | 待测 |
| L3-04 | complete 后入库 | snapshot 更新 | 🟡 旧数据仍在 |

### L4 Agent / 紫鸟

| ID | 检查点 | 预期 | 2026-07-13 |
|----|--------|------|------------|
| L4-01 | Agent 心跳 | 在线 | 🟢 |
| L4-02 | 紫鸟 WebDriver | :16851 | ⚪ |
| L4-03 | SC 已登录 | crawl 不报 LOGIN | 🔴 reports 未登录 |
| L4-04 | `page_diagnostics` 回传 | 每页行数 | 🟡 需查最近 success job |

### L5 Python 解析与合成

| ID | 检查点 | 预期 | 2026-07-13 |
|----|--------|------|------------|
| L5-01 | `br_child_asin` 行数 | >0 | 🟡 有 revenue 无 sessions |
| L5-02 | `inventory_all` 行数 | >0 | 🔴 inventory 全 0 |
| L5-03 | `ads_campaign_manager` | SKU 级 spend | 🔴 fallback 账户 ACOS |
| L5-04 | 无 `allocate_account_ads` | 代码已删 | 🔴 仍存在 |
| L5-05 | 商品名完整 | 非截断 | 🔴 大量截断 |

### L6 入库与 API

| ID | 检查点 | 预期 | 2026-07-13 |
|----|--------|------|------------|
| L6-01 | GET insights products | 与 DB 一致 | 🟢 39 |
| L6-02 | GET daily metrics | ≥1 | 🟢 8 |
| L6-03 | 无二义性 0（未采集 vs 真 0） | provenance | 🔴 未实现 |

### L7 前端展示

| ID | 检查点 | 预期 | 2026-07-13 |
|----|--------|------|------------|
| L7-01 | ACOS 全相同是否仍展示 | 应 `—` 或分 SKU 真实值 | 🔴 全 40.8% |
| L7-02 | 利润率列 | 隐藏 | 🔴 0% |
| L7-03 | 空广告 Alert 文案 | 准确 | 🟡 |
| L7-04 | syncedAt 与 DB 一致 | 是 | 待核 |

---

## 4. 人工对账记录（RECON）

每次 Review 至少抽 **3 个 ASIN**（1 大卖 + 1 中卖 + 1 无广告）。

### 4.1 对账模板（复制使用）

| 日期 | ASIN | 字段 | Seller Central | CrossHub | Δ | 判定 |
|------|------|------|----------------|----------|---|------|
| | B08B8X3Q6C | revenue_30d | | US$1,868.13 | | |
| | B08B8X3Q6C | orders_30d | | 66 | | |
| | B08B8X3Q6C | page_views | | 0 | | |
| | B08B8X3Q6C | ad_spend | | US$762.94 | | 🔴推算 |
| | B08B8X3Q6C | acos | | 40.8% | | 🔴推算 |
| | | | | | | |

### 4.2 2026-07-13 基线对账（待补 SC 截图）

| ASIN | revenue | orders | sessions | ad_spend | acos | 备注 |
|------|---------|--------|----------|----------|------|------|
| B08B8X3Q6C | CH 有 | CH 有 | CH 0 | CH 推算 | CH 40.84% | 需 SC 核对 |
| B0C96B8MPV | CH 有 | CH 有 | CH 0 | CH 推算 | CH 40.84% | |
| B07Z3LCDX9 | CH 有 | CH 有 | CH 0 | CH 推算 | CH 40.84% | |

---

## 5. Code Review 发现清单（静态）

| # | 严重度 | 位置 | 问题 | 修复任务 | 状态 |
|---|--------|------|------|----------|------|
| CR-01 | **P0** | `product_composer.allocate_account_ads_by_revenue` | 账户 ACOS 摊到全 SKU | PY-A01～A02 | ☐ 未修 |
| CR-02 | **P0** | `enrich_product_rows` tacos=acos | 假 TACoS | PY-A03 | ☐ |
| CR-03 | **P0** | `enrich_from_related_inventory` | 名称 fuzzy 补数不可溯源 | PY-A04 | ☐ |
| CR-04 | **P0** | `AmazonProductsPanel` 利润率列 | 无源显示 0% | F-A02 | ☐ |
| CR-05 | **P1** | `seller_pages.js` BR 列映射 | 标题截断、sessions 未映射 | PY-B01 | ☐ |
| CR-06 | **P1** | `merge_campaign_ads` len==1 兜底 | 误配广告到单 SKU | PY-A05 | ☐ |
| CR-07 | **P2** | `refreshAmazonAllWithSync` | 并行 daily+reports 双 job | F-C01 | ☐ |
| CR-08 | **P2** | `platformSync.syncAmazonStores` | 登录即 crawl 无新鲜度 | F-C02 | ☐ |
| CR-09 | **P2** | 重复 `platform_account` | 同 browserId 双 job | J + 数据清理 | ☐ |
| CR-10 | **P1** | `test_allocate_ads_from_acos_only` | 测例固化造假行为 | PY-A06 删除 | ☐ |

---

## 6. 实施进度跟踪（对照 12-实施包）

| 阶段 | 完成度 | 阻塞项 | 目标日期 | 实际 |
|------|--------|--------|----------|------|
| AUTH-P0 禁止造假 | 0% | CR-01～04 | | |
| AUTH-P1 解析修复 | 0% | CR-05～06 | | |
| AUTH-P2 full 单任务 | 0% | CR-07～08 | | |
| AUTH-P3 可观测性 | 0% | 可选 | | |

**合并闸门**：§2 AUTH 快检全 🟢 + [13-测试用例](./13-数据真实性-测试用例.md) AUTH-01～08 PASS。

---

## 7. Review 会话记录（追加式）

>  newest on top

---

### REV-2026-07-13-01 · 初始全链路诊断

| 项 | 内容 |
|----|------|
| **参与** | 研发（AI 辅助诊断） |
| **环境** | Agent ok；Java 曾 DOWN；DB `crosshub.db` |
| **动作** | `audit_amazon_data_coverage.py`、`check_amazon_pipeline.py`、代码走读 |
| **结论** | 销售额/订单可信；广告指标全假；解析层缺 sessions/inventory；同步近期失败 |
| **决议** | 输出 V3 文档包 10～13；**禁止合并**直至 AUTH-P0 |
| **待办** | ① 重启 Java ② 紫鸟登录 ③ 落地 P0 代码 ④ 清 snapshot 重 sync |

---

### REV-______-__ · （模板）

| 项 | 内容 |
|----|------|
| **参与** | |
| **分支 / commit** | |
| **环境** | Java / Agent / 紫鸟 / Vue |
| **动作** | |
| **AUTH 快检** | A1 ☐ … A7 ☐ |
| **RECON ASIN** | |
| **结论** | 🟢可发布 / 🟡有条件 / 🔴阻塞 |
| **待办** | |

---

## 8. 刷新命令（Review 前必跑）

```powershell
cd D:\NIUBI\SaaS-HZ_WEB_Demo

# 基础设施
netstat -ano | findstr ":18080 :18765 :16851 :5173"
curl -s http://127.0.0.1:18765/health
curl -s http://127.0.0.1:18080/api/health

# 数据审计（输出贴到 §1 / §2）
py scripts\audit_amazon_data_coverage.py
py scripts\check_amazon_pipeline.py

# 单测
py -m pytest backend\python\tests\test_amazon_parsers.py -q

# 静态：是否仍有造假代码
rg "allocate_account_ads_by_revenue" backend/python
rg "profitMargin" dev/vue-site/src/components/amazon
```

---

## 9. 发布签字（Review 结束时）

| 角色 | 姓名 | 日期 | AUTH P0 | RECON 3ASIN | 签字 |
|------|------|------|---------|-------------|------|
| 研发 | | | ☐ | ☐ | |
| 测试 | | | ☐ | ☐ | |
| 产品/运营 | | | ☐ | ☐ | |

**发布条件**：§2 无 🔴 · §6 AUTH-P0+P1+P2 完成 · [13-测试用例](./13-数据真实性-测试用例.md) 发布回归套件 PASS。

---

## 10. 变更日志（本文档）

| 日期 | 变更 |
|------|------|
| 2026-07-13 | 初版：基线诊断快照 + Review 模板 + CR 清单 |
