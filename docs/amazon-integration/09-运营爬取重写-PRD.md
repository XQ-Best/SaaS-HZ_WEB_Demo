# Amazon 运营侧数据爬取 — PRD（V2 重写）

> **版本**：v2.0-draft  
> **日期**：2026-07-11  
> **产品**：CrossHub — Amazon 运营模块  
> **读者**：产品、运营、研发、测试  
> **依赖**：[07-需求方案](./07-运营爬取重写-需求方案.md) · [08-技术设计](./08-运营爬取重写-技术设计.md)

---

## 1. 产品概述

### 1.1 一句话

**让 Boss 和运营在 CrossHub 里看到的 Amazon 数据，与 Seller Central / Advertising 后台可对账。**

### 1.2 问题（用户原话还原）

> 「你对于亚马逊商家页里的不同页面的定位有漏洞，导致项目亚马逊运营侧吃不到数据。」

具体表现：

- 产品 TOP20：订单、销售额、广告花费、ACOS、TACoS、转化率大量为 `—`
- 出库单：与后台 pending / canceled 列表不一致
- 刷新后 SKU 数从 25 降到 11，有效指标仅 4～6 条

### 1.3 解决方案概述

重写 Python 爬取管道：**按卖家后台真实页面拆分采集 → 统一解析 → 按 ASIN 合成 → 入库展示**，并提供分页面同步诊断。

---

## 2. 用户角色与场景

| 角色 | 典型场景 | 成功标准 |
|------|----------|----------|
| **Boss 刘洋** | 早会看 TOP20、出库积压、ACOS 过高 SKU | 一页看清「卖多少、花多少、哪些要调价」 |
| **运营** | 处理买家消息、差评、优惠券过期、FBA 货件短缺 | 日报 Tab 有待办条数与列表 |
| **Boss（设置）** | 绑定紫鸟店铺、看 Agent 是否在线 | 离线时有指引，不显示 Demo 假数据 |
| **运维** | 同步失败排查 | 5 分钟内定位到具体 SC 页面 |

---

## 3. 产品功能清单

### 3.1 数据采集（后端 / Agent，用户无感）

| 功能 ID | 功能 | 优先级 | 说明 |
|---------|------|--------|------|
| F-01 | 订单全路径采集 | P0 | 8 个 orders-v3 子页，含 hub / pending / canceled / shipped |
| F-02 | Campaign Manager 广告采集 | P0 | `merchantId` + `locale=zh_CN` 主入口 |
| F-03 | BR 子 ASIN 指标采集 | P0 | 销售额、订单、会话、转化率 |
| F-04 | 库存目录采集 | P0 | ASIN、SKU、品名、FBA 库存 |
| F-05 | 账户首页指标 | P0 | 待处理订单、买家消息等 |
| F-06 | 日常运营列表 | P1 | 消息、差评、优惠券、货件、Case |
| F-07 | 分页面诊断 | P0 | 同步结果可查看每页采集行数与耗时 |
| F-08 | merchantId 记忆 | P1 | 首次解析后写入店铺配置，下次广告直连 |

### 3.2 数据展示（Vue，用户可见）

| 功能 ID | 模块 | 优先级 | 数据字段 |
|---------|------|--------|----------|
| U-01 | 产品 TOP20 | P0 | 商品、ASIN、7日订单、7日销售额、广告花费、ACOS、TACoS、转化率、会话、FBA库存 |
| U-02 | 出库单 | P0 | 订单号、ASIN、状态、FBM/FBA、金额、品名 |
| U-03 | 账户状况 | P0 | ODR、迟发率、买家消息、待处理订单等 |
| U-04 | 买家消息 | P1 | 买家、主题、订单号、SLA |
| U-05 | 差评 | P1 | 1～3 星、订单号、内容 |
| U-06 | 优惠券 | P1 | 名称、折扣、状态 |
| U-07 | 入库货件 | P1 | 货件号、短缺、状态 |
| U-08 | Case | P1 | 首页 Case 卡片同步 |
| U-09 | 空态与错误 | P0 | 区分「未同步」「同步失败」「后台确实无数据」 |
| U-10 | 运营总览卡片 | P1 | Amazon 待办数来自 API |

### 3.3 同步交互

| 功能 ID | 按钮/入口 | scope | 用户文案 |
|---------|-----------|-------|----------|
| S-01 | 产品 TOP20「刷新数据」 | `reports` | 已刷新产品数据 |
| S-02 | 「Business Report 刷新」 | `reports` | 已刷新 Business Report 产品数据 |
| S-03 | 今日运营「刷新」 | `daily` | 已刷新今日运营数据 |
| S-04 | 账户状况「刷新」 | `account_health` | 已刷新账户状况 |
| S-05 | Boss「一键同步 Amazon」 | `daily` + `reports` | 全部 Amazon 数据已更新 |
| S-06 | 同步失败 Toast | — | 展示 `error_message`，可含「订单页解析 0 行」 |

---

## 4. 字段规格（产品 TOP20）

### 4.1 列定义与数据来源

| 列名（UI） | 字段 | 主数据源 | 备用数据源 | 空值展示 |
|------------|------|----------|------------|----------|
| 商品 | `productName` | 库存目录 | BR 表 | —（无效行不展示） |
| ASIN | `asin` | 库存 / BR | — | — |
| 7日订单 | `orders7d` | BR `units ordered` | 订单页 ASIN 聚合 | `0` |
| 7日销售额 | `revenue7d` | BR `ordered product sales` | — | `—` |
| 广告花费 | `adSpend7d` | Campaign Manager | — | `—` |
| ACOS | `acos` | Campaign Manager | 账户广告汇总（仅看板） | `—` |
| TACoS | `tacos` | 计算：`adSpend / revenue` | — | `—` |
| 转化率 | `conversionRate` | BR `unit session %` | — | `—` |
| 会话 | `sessions7d` | BR `sessions` | — | `0` |
| FBA库存 | `unitsOnHand` | 库存页 | — | `0` |
| 利润率 | `profitMargin` | —（V2 无成本源） | — | `—` |

### 4.2 TOP20 排序规则（与现网一致）

1. 过滤无效行（`isValidAmazonProduct`）
2. 有指标 SKU 优先：按 `revenue7d` → `orders7d` → `sessions7d` 降序
3. 无指标 SKU 按商品名字母序接在后面
4. 取前 20，显示 `displayRank`

### 4.3 广告数据提示（已有 UI）

当 TOP20 有商品但 `hasAdData=false` 时，展示 Info Alert：

> 广告数据尚未同步 — 请点击「Business Report 刷新」…

V2 完成后该 Alert 应仅在**店铺确实无广告**时出现。

---

## 5. 出库单规格

### 5.1 状态枚举

| status | 含义 | 来源页面 |
|--------|------|----------|
| `pending` | 待处理 / 等待中 | hub、pending、unshipped |
| `packed` | 待揽收 | 行文本识别 |
| `shipped` | 已发货 | shipped |
| `canceled` | 已取消 | fba/mfn canceled |

### 5.2 履约类型

| fulfillmentType | 含义 |
|-----------------|------|
| `fba` | FBA 订单 |
| `fbm` | 自发货 / MFN |

### 5.3 展示汇总（`summarizeOutboundOrders`）

- 待处理 `pending`、待揽收 `packed`、已发货 `shipped`
- FBM / FBA 分列统计

---

## 6. 同步状态与任务（用户可见）

### 6.1 任务状态机

```
用户点击刷新 → POST /api/amazon/sync → job pending
       → Agent 领取 → running（前端轮询）
       → success | failed
       → 前端 reload GET daily / insights
```

### 6.2 用户可感知结果

| 状态 | UI 表现 |
|------|---------|
| `success` + 有数据 | Toast 成功 + 表格更新 + `syncedAt` 更新 |
| `success` + 空数据 | 空态组件 + 文案「后台暂无数据」 |
| `failed` | Toast/Alert 红色 + `error_message` |
| Agent 离线 | 操作指引，**不**加载 Demo |
| 紫鸟未登录 | 「请在紫鸟窗口完成 Seller Central 登录」 |

### 6.3 部分成功（V2 新增）

`success` + `result_summary.warnings` 含 `PARTIAL_BR` 时：

- TOP20 仍展示已采集 SKU
- Panel 顶部 Warning：「部分商品指标未从 Business Report 加载，请稍后重试」

---

## 7. 页面地图（产品对照表）

运营同学可用此表在紫鸟中手工对账：

| 后台菜单 | URL 路径 | CrossHub 位置 |
|----------|----------|---------------|
| 首页 | `/home` | 账户状况、Case、资讯 |
| 订单 → 管理订单 | `/orders-v3/?page=1` | 出库单 |
| 订单 → FBA → 等待中 | `/orders-v3/fba/pending?page=1` | 出库单（pending） |
| 订单 → FBA → 已取消 | `/orders-v3/fba/canceled?page=1` | 出库单（canceled） |
| 库存 → 管理所有库存 | `/myinventory/inventory?fulfilledBy=all` | TOP20 商品名/库存 |
| 报告 → 业务报告 → 子 ASIN | `/business-reports/detail/sales-traffic-by-asin` | TOP20 销售指标 |
| 广告 → 广告活动管理 | `advertising.amazon.com/campaign-manager/all-campaigns` | TOP20 广告列 |
| 绩效 → 账户状况 | `/performance/account/health` | 账户状况 |
| 买家消息 | `/messaging/inbox` | 消息 Tab |
| 反馈管理器 | `/feedback-manager/index.html` | 差评 Tab |

**紫鸟快捷打开**（运维）：

```powershell
py scripts/open_amazon_sc.py orders
py scripts/open_amazon_sc.py orders_pending
py scripts/open_amazon_sc.py orders_canceled
py scripts/open_amazon_sc.py ads
py scripts/open_amazon_sc.py br
```

---

## 8. 验收用例（测试可执行）

### 8.1 P0 必过

| 用例 ID | 步骤 | 期望 |
|---------|------|------|
| TC-01 | 紫鸟+Agent 在线，Boss 点「Business Report 刷新」 | job success；`amazon_product_snapshot` ≥ 10 行 |
| TC-02 | 打开 TOP20 | ≥ 10 行有商品名；≥ 5 行 `revenue7d` > 0（有销售时） |
| TC-03 | 店铺有广告投放 | ≥ 1 行 `adSpend7d` > 0 或账户级广告 metric 有值 |
| TC-04 | 对比 SC 订单 pending 数与 CrossHub 出库单 | 差异 ≤ 10% |
| TC-05 | 对比 SC canceled 列表 | CrossHub 含 canceled 状态订单 |
| TC-06 | Agent 离线点刷新 | 明确错误，页面无 Demo 数据 |
| TC-07 | 随机 3 ASIN 人工对账 BR 销售额 | 误差 ≤ $1 或 1 件 |

### 8.2 P1 应过

| 用例 ID | 步骤 | 期望 |
|---------|------|------|
| TC-11 | 点「今日运营刷新」 | 消息/差评/优惠券/货件至少一类有数据或空态 |
| TC-12 | 员工账号仅有 Amazon scope | 只见授权店铺 |
| TC-13 | 同步失败 | `result_summary.page_diagnostics` 可查失败页 |
| TC-14 | TOP20 过滤「ACOS 过高」 | 仅展示 acos ≥ danger 阈值 SKU |

### 8.3 回归（不可破坏）

- 后端模式 **零** `amazonDailyLocal` 注入
- `VITE_USE_TEMU_BACKEND=false` Demo 行为不变
- 写操作 M4（发货/回复）不受读同步影响

---

## 9. 发布计划

| 阶段 | 内容 | 用户可见变化 | 预计 |
|------|------|--------------|------|
| **R1** | 页面 URL + 订单/广告解析修复 | TOP20/出库单数据明显增加 | 第 1 周 |
| **R2** | Pipeline 拆分 + 诊断 | 失败时可看哪一页出问题 | 第 2 周 |
| **R3** | DB 字段 tacos/conversion + API | TACoS、转化率列有值 | 第 2～3 周 |
| **R4** | 快照回归 + 文档定稿 | 稳定版本，可对外演示 | 第 3 周 |

### 9.1 发布检查清单

- [ ] Agent 已重启
- [ ] 租户 5 YOTO US `reports` sync success
- [ ] `py scripts/_check_amazon_metrics.py` 通过
- [ ] Boss 截图 TOP20 与 SC 对账确认
- [ ] 运营总览 Amazon 卡片数字一致

---

## 10. 风险与开放问题

| 风险 | 产品决策 |
|------|----------|
| BR 默认 30 日，UI 写 7 日 | R3 统一：要么改 UI 为「近 30 日」，要么 BR 选 7 日日期 |
| 利润率无数据源 | V2 保持 `—`，不从 PRD 承诺 |
| 多站点（EU/FE） | V2 仅验证 NA；其他区域 URL 进 backlog |
| 同步 > 8 分钟 | 产品接受异步；前端轮询进度（已有） |

---

## 11. 附录：开发任务拆解（与 PRD 对齐）

| 模块 | 任务 | 负责人建议 |
|------|------|------------|
| Python | `page_registry` + `crawl_pipeline` | 后端 |
| Python | orders/ads/br parser + fixtures | 后端 |
| Python | `composer` + diagnostics | 后端 |
| Java | V11 migration `tacos`/`conversion_rate`/`amazon_merchant_id` | 后端 |
| Java | `result_summary` 解析展示 API | 后端 |
| Vue | 空态区分 partial_success | 前端 |
| 运维 | Agent 重启、E2E 脚本、open_amazon_sc | 运维 |
| QA | TC-01～TC-07 对账报告 | 测试 |

---

## 12. 文档索引

| 文档 | 用途 |
|------|------|
| [07-运营爬取重写-需求方案.md](./07-运营爬取重写-需求方案.md) | 为什么要做、范围、验收 |
| [08-运营爬取重写-技术设计.md](./08-运营爬取重写-技术设计.md) | 怎么做、模块、契约 |
| [09-运营爬取重写-PRD.md](./09-运营爬取重写-PRD.md) | 本文：产品功能与测试 |
| [04-测试用例清单.md](./04-测试用例清单.md) | 一期联调用例（需合并 TC） |
| [05-回归基准.md](./05-回归基准.md) | 指标阈值基准 |

---

**状态**：待产品/运营评审 Q1～Q4（见需求方案 §10）后进入 M1 开发。
