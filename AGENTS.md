# Agent Instructions

## Package Manager
- Frontend (`dev/vue-site`): **npm**
- Temu Python crawler (`backend/python`): **py** + Playwright（建议本机 Chrome）
- Temu Java API (`backend/java`): 便携 JDK/Maven → `scripts/setup-java.ps1`
- Optional Express demo (`script/api-server`): **npm**

## Commands

| Task | Command |
|------|---------|
| 安装 JDK 17 + Maven（便携） | `powershell -File scripts/setup-java.ps1` |
| 启用 Java 环境 | `. .\scripts\env-java.ps1` |
| Temu 首次登录（Playwright） | `py backend/python/login.py` |
| Temu 爬虫入库 | `py backend/python/crawl.py` |
| Temu 种子数据（无浏览器） | `py backend/python/crawl.py --seed` |
| Java Temu API | `mvn -f backend/java/pom.xml spring-boot:run` |
| Frontend dev | `cd dev/vue-site && npm run dev` |

## External References
| Need | File |
|------|------|
| Frontend entry & UI stack | `dev/vue-site/src/main.js` |
| Routes & role guard | `dev/vue-site/src/router/index.js` |
| Sidebar menus (boss/employee) | `dev/vue-site/src/layouts/PortalLayout.vue` |
| Platform taxonomy | `dev/vue-site/src/constants/platforms.js` |
| Employee menu scoping | `dev/vue-site/src/utils/scope.js` |
| 运营绑定 | `dev/vue-site/src/views/boss/EmployeeBindingView.vue` |
| Demo data & localStorage APIs | `dev/vue-site/src/api/*Local.js`, `dev/vue-site/src/api/platformAccounts.js` |
| Optional HTTP client | `dev/vue-site/src/api/http.js` |
| Vite proxy (`/api/temu`,`/api/auth`,`/api/warehouse`,`/api/tenant` → Java; `/api` → `:3000`) | `dev/vue-site/vite.config.js` |
| Demo 后端开关（默认关，仅 `VITE_USE_TEMU_BACKEND=true` 连 Java） | `dev/vue-site/.env`, `src/api/config.js` |
| 任务分配（Boss） | `views/boss/TaskAssignmentView.vue`, `api/assignedTasks.js` |
| 员工任务中心 | `views/employee/TasksView.vue`, `utils/employeeTasks.js` |
| 仓库任务中心 | `views/warehouse/WarehouseTasksView.vue`, `fetchWarehouseAssignedTasks` |
| 任务反馈 UI | `components/tasks/TaskFeedbackDialog.vue`, `TaskFeedbackTimeline.vue`, `AssignedTaskDetailDrawer.vue`, `EmployeeTaskDetailDrawer.vue` |
| 仓库端口登录（Demo） | `api/auth.js`, `api/warehouseAuthLocal.js` |
| 仓管分仓展示 | `components/warehouse/WarehouseScopePanel.vue`, `utils/warehouseScope.js` |
| Temu Java API + Python 爬虫 | `backend/README.md` |
| Temu 前端 API 客户端 | `dev/vue-site/src/api/temuApi.js` |
| 仓库出库单（本地 + Java `/api/warehouse`） | `dev/vue-site/src/api/warehouseOrders.js`, `warehouseOrdersApi.js` |
| 分仓设置（本地 + Java `/api/warehouse/sites`） | `dev/vue-site/src/api/warehouseSites.js` |
| 仓库人员绑定（本地 + Java `/api/warehouse/members`） | `dev/vue-site/src/api/warehouseStaff.js`, `warehouseStaffLocal.js` |
| Express demo backend | `script/api-server/index.js` |

## Key Conventions
- Monorepo layout: Vue app in `dev/vue-site/`; demo Express in `script/api-server/`.
- Import alias: `@` → `dev/vue-site/src/`.
- Roles: `boss` (`/boss/*`), `employee` (`/employee/*`), `warehouse` (`/warehouse/*`); guard in `router/index.js`.
- Boss sees all platform menus; employee menus come from `employeeModuleMenus()` based on `auth.employee.platforms`.
- Store visibility: `scopeStores()` filters by `assignedStoreIds` or platform list.
- **Demo-first data**: most platform ops use `*Local.js` + `localStorage`; `platformAccounts.js` orchestrates seed/ensure helpers. **默认纯前端 Demo**（`.env` 中 `VITE_USE_TEMU_BACKEND=false`）；仅 Boss 且已后端登录时 `employees.js` / `warehouseStaff.js` 才写 Java API，避免未启动 Java 时 502。
- Platform module pattern: `views/<platform>/*ModuleView.vue` + `components/<platform>/` + `constants/<platform>*.js` + `utils/<platform>.js`.
- Domestic platforms (拼多多/抖音/视频号): shared `useDomesticModule` composable + `api/domesticPlatforms.js`.
- New platform: add boss + employee routes, `PortalLayout` boss menu, `employeeModuleMenus` def, view/components/constants, and `platformAccounts` fetch/seed.
- **Temu 运营**：Python 爬虫 → `backend/data/crosshub.db` → Java `:8080` → 前端 `temuApi.js`（见 `backend/README.md`）。
- **任务分配**：Boss 可向 **运营人员** 或 **仓库管理员** 分配（`assigneeType`）；员工/仓库在各自 **任务中心** 提交反馈 → `syncAssignedTaskFeedback` 同步状态与 `lastFeedback`（无百分比进度）；历史反馈在 **详情抽屉**，提交弹窗 `TaskFeedbackDialog` 仅填新反馈。
- **仓库下单**：Java `WarehouseOrderService` + SQLite `warehouse_order`；前端 `warehouseOrders.js` 在后端登录时走 `warehouseOrdersApi.js`，否则 localStorage Demo。流程：提交 → 审批 → 暂不可发 → 确认可发 → 发货；管理员可 DELETE 删除。仓库侧栏：待审核 / 待发货 / 已发货 / **任务中心**。下单须指定分仓（`warehouse_id`）。仓管登录后侧栏与顶栏展示 **负责分仓**（`WarehouseScopePanel`）。
- **分仓设置**：Java `WarehouseSiteService` + `warehouse_site` 表；Boss **设置 → 仓库设置**；Demo 种子：泰州1号仓 / 泰州邮政仓 / 安徽仓库。
- **仓库人员**：Java `WarehouseStaffService` + `app_user`(role=warehouse)；前端 `warehouseStaff.js`；**仅 Boss「设置 → 仓库人员」** 可新增/编辑/绑定；仓管通过 `user_warehouse_scope` 分配可管理分仓。
- Other demo APIs: Vite proxies `/api` to `localhost:3000` (Express; store-binding for `temu`/`aliexpress` labels only).
- UI: Element Plus; page shell via `PageHeader` + `PageScroll`.
- No ESLint/test runner configured—do not add tooling unless requested.

## Commit Attribution
AI commits MUST include:
```
Co-Authored-By: (the agent's name and attribution byline)
```
