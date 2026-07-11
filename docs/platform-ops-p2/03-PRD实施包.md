# 三平台运营增强 — PRD 实施包

> 需求：[01-需求文档.md](./01-需求文档.md) · 技术方案：[02-技术方案.md](./02-技术方案.md) · 测试：[04-测试用例.md](./04-测试用例.md)

---

## 里程碑总览

| 阶段 | 代号 | 范围 | 工期估 | 依赖 |
|------|------|------|--------|------|
| **M1** | OPS-AE-V | AliExpress 违规纳入顶栏同步 | 2～3 天 | 无 |
| **M2** | OPS-TM-C | Temu 竞品 monitor + 顶栏触发 | 4～5 天 | monitor worker 运行 |
| **M3** | OPS-AMZ-W0 | Amazon 写回（消息+发货 P0） | 7～10 天 | Agent + 紫鸟 |
| **M4** | OPS-AMZ-W1 | Amazon 写回（评论+Case+审计） | 3～5 天 | M3 |

---

## M1：AliExpress 违规顶栏同步（OPS-AE-V）

### 后端 Java

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| AE-J01 | `AliExpressCrawlRequest` 增加 `scope`：`orders` \| `violations` \| `all` | `dto/AliExpressCrawlRequest.java` | ☐ |
| AE-J02 | `triggerCrawl` 传 `--scope` 给 Python | `AliExpressCrawlServiceImpl.java` | ☐ |
| AE-J03 | job 完成时写入 `violations_count`（scope 含 violations 时） | 同上 | ☐ |
| AE-J04 | `AppErrorCode` 文档化 partial + violations 失败语义 | `AppErrorCode.java` | ☐ |
| AE-J05 | 回归：`POST /crawl` 无 body 仍默认 orders | 集成测试 | ☐ |

### Python

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| AE-P01 | CLI `--scope all` 先 orders 后 violations 同 session | `crawl.py` / `aliexpress_crawler.py` | ☐ |
| AE-P02 | 输出 JSON 含 `orders`、`violations` 计数 | crawler return | ☐ |
| AE-P03 | violations 失败时 orders 仍 commit（partial 标记） | ingest | ☐ |

### 前端 Vue

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| AE-F01 | `triggerAliExpressCrawl({ scope: 'all' })` | `aliexpressApi.js` | ☐ |
| AE-F02 | `syncAliExpressStores` 顶栏传 `scope: 'all'` | `platformSync.js` | ☐ |
| AE-F03 | 顶栏 message 展示违规条数 | `platformSync.js` | ☐ |
| AE-F04 | partial：订单有数、违规失败 → `status=partial` | `platformSync.js` | ☐ |
| AE-F05 | AliExpress 模块页「刷新」与顶栏行为一致（可选 scope） | `AliExpressModuleView.vue` | ☐ |

### M1 验收

- [ ] 顶栏同步 tenant 5：`/api/aliexpress/violations` → `syncedAt` 更新
- [ ] `aliexpress_crawl_job` 最新一条 scope=all 或 violations_count 有值
- [ ] 无双 job 409（单 scope=all job）

---

## M2：Temu 竞品自动监控（OPS-TM-C）

### 后端 Java

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| TM-J01 | 竞品 CRUD 对接 `monitor_target`（platform=temu） | `MonitorController` / Service | ☐ |
| TM-J02 | `GET /api/monitor/targets?platform=temu` 列表 | 已有，补文档 | ☐ |
| TM-J03 | 从 `temu_competitor` 迁移脚本 V10 | `config/migration/` | ☐ |
| TM-J04 | Scheduler 启用竞品默认定时 1440min | `MonitorScheduler` | ☐ |
| TM-J05 | `can_trigger_now` 考虑 `snapshot_date=today` | `MonitorServiceImpl` | ☐ |

### Python

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| TM-P01 | monitor worker 消费 temu competitor target | `platforms/temu_monitor_adapter.py` | ☐ |
| TM-P02 | 顶栏批量 trigger 限流 3 目标/租户 | worker 或 Java | ☐ |
| TM-P03 | 错误码对齐 `COMPETITOR_*` → Java job | worker | ☐ |

### 前端 Vue

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| TM-F01 | 添加竞店 → POST monitor target | `CompetitorAnalysis.vue` | ☐ |
| TM-F02 | 后端模式读 monitor latest 替代 local | `temuCompetitorsApi.js` | ☐ |
| TM-F03 | `syncTemuStores` 末尾 trigger auto_sync 目标 | `platformSync.js` | ☐ |
| TM-F04 | UI：上次快照时间、job 状态、登录指引 | `CompetitorAnalysis.vue` | ☐ |
| TM-F05 | 设置：自动策略（顶栏/定时/手动） | 竞品 Tab 或设置页 | ☐ |

### 运维

| # | 任务 | 完成 |
|---|------|------|
| TM-O01 | 文档：`py backend/python/frontend_login.py --tenant-id 5` | ☐ |
| TM-O02 | `scripts/start-local.ps1` 可选启动 monitor worker | ☐ |

### M2 验收

- [ ] Boss 添加 1 竞店并设 auto_sync=顶栏
- [ ] 顶栏 Temu 同步后 `temu_competitor_snapshot` 或 monitor snapshot 有当日行
- [ ] 竞品 Tab 展示分析结果，非 Demo localStorage

---

## M3：Amazon 写回 P0（OPS-AMZ-W0）

### 后端 Java

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| AMZ-J01 | 迁移 `amazon_write_job` | `V10AmazonWriteJobMigration.java` | ☐ |
| AMZ-J02 | `AmazonWriteService.enqueueWrite()` | `AmazonWriteServiceImpl.java` | ☐ |
| AMZ-J03 | `AgentService` task_type=`amazon_write` | `AgentServiceImpl.java` | ☐ |
| AMZ-J04 | `AmazonAgentWriteBridge.onComplete` | 新类 + SyncBridge 模式 | ☐ |
| AMZ-J05 | 店铺级读写互斥 409 | `AmazonSyncServiceImpl` | ☐ |
| AMZ-J06 | `GET /api/amazon/write/{jobId}` | `AmazonController.java` | ☐ |
| AMZ-J07 | PATCH API 返回 `{ write_job_id, status: pending }` | Controller + DTO | ☐ |

### Python Agent

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| AMZ-P01 | `amazon/write_actions.py` 策略基类 | 新建 | ☐ |
| AMZ-P02 | `buyer_message_reply` 实现 | write_actions | ☐ |
| AMZ-P03 | `outbound_ship` 实现 | write_actions | ☐ |
| AMZ-P04 | `agent/handlers/amazon_write.py` | agent | ☐ |
| AMZ-P05 | 失败截图 `amazon-captures/write_*` | report_crawler 复用 _save_capture | ☐ |
| AMZ-P06 | complete payload snake_case 对齐 | handlers | ☐ |

### 前端 Vue

| # | 任务 | 文件 | 完成 |
|---|------|------|------|
| AMZ-F01 | PATCH 后轮询 write job | `amazonApi.js` | ☐ |
| AMZ-F02 | `AmazonBuyerMessagesPanel` pending UI | component | ☐ |
| AMZ-F03 | `AmazonOutboundPanel` 发货 pending UI | component | ☐ |
| AMZ-F04 | 失败保留表单 + 错误码文案 | `appErrorCode.js` | ☐ |

### M3 验收

- [ ] tenant 5 YOTO：1 条测试消息回复 job success + SC 截图
- [ ] 1 条出库发货（测试单）job success 或明确 DOM 失败码
- [ ] 写进行中触发 sync → 409

---

## M4：Amazon 写回 P1（OPS-AMZ-W1）

| # | 任务 | 完成 |
|---|------|------|
| AMZ-P07 | `review_handle` WebDriver | ☐ |
| AMZ-P08 | `case_ack` WebDriver | ☐ |
| AMZ-J08 | 审计表 `amazon_write_audit` 或 job 扩展 | ☐ |
| AMZ-F05 | Reviews / Cases Panel 联调 | ☐ |

---

## 发布与回归清单

### 发布前

- [ ] `powershell -File scripts/restart-java-api.ps1`
- [ ] Agent 重启；紫鸟 WebDriver 16851 监听
- [ ] `py scripts/diag_three_platforms.py --tenant-id 5`
- [ ] `py scripts/diag_three_platforms.py --trigger all --wait`（可选）

### 发布后 smoke

| 步骤 | 命令/操作 | 期望 |
|------|-----------|------|
| 1 | 顶栏同步三平台 | Temu/AE success；Amazon health success |
| 2 | AE violations API | syncedAt 非空 |
| 3 | Temu 竞品 Tab | 有当日快照或 skipped 原因 |
| 4 | Amazon 写测试 | write_job success 或明确 failed |

### 回滚

- Java：Revert migration V10 前备份 `crosshub.db`
- 前端：Feature flag `VITE_AMAZON_WRITE_ENABLED=false`（建议新增）
- AliExpress：顶栏 scope 改回 `orders`

---

## 排期表示例（2 人周）

| 周 | 开发者 A | 开发者 B |
|----|----------|----------|
| W1 | M1 Java+Python scope=all | M1 前端 platformSync + 验收 |
| W2 | M2 monitor 迁移 + Java | M2 竞品 Tab + 顶栏 trigger |
| W3-W4 | M3 Amazon write 后端+Agent | M3 前端 Panel + E2E |
| W5 | M4 评论/Case + 审计 | 全量回归 + 文档 |

---

## 相关脚本（实施后新增建议）

```powershell
# 三平台诊断（已有）
py scripts/diag_three_platforms.py --tenant-id 5 --trigger all --wait

# Temu 前台登录（竞品前置）
py backend/python/frontend_login.py --tenant-id 5

# Amazon 写操作 E2E（待建）
py backend/python/scripts/e2e_amazon_write.py --tenant-id 5 --action buyer_message_reply --item-id msg_xxx
```
