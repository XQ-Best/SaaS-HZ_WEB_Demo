# CrossHub 跨境运营管理平台

CrossHub 是一套面向跨境企业的 **SaaS 运营管理工作台** Demo。支持企业管理员与员工分级登录，覆盖 Temu、AliExpress、Amazon、Walmart、1688、独立站（Shopify / WordPress）等多平台运营场景，提供账户绑定、运营总览、异常预警、**任务分配与协同**、每日运营报告与 AI 办公辅助。

> 当前版本以 **前端 Demo + 浏览器 localStorage** 为主，无需数据库即可完整体验；可选启动本地 Express API 服务用于部分账户绑定接口联调。

---

## 技术栈

| 类别 | 选型 |
|------|------|
| 框架 | Vue 3（Composition API + `<script setup>`） |
| 构建 | Vite 8 |
| 路由 | Vue Router 5 |
| 状态 | Pinia |
| UI | Element Plus + `@element-plus/icons-vue` |
| 语言 | JavaScript（ES Module） |
| Node | `^22.18.0` 或 `>=24.12.0` |

界面采用 **Soybean / Arco 风格** 设计令牌（`assets/theme.css`），浅色侧栏工作台 + 分屏登录布局。

---

## 快速开始

```bash
# 进入前端项目
cd dev/vue-site

# 安装依赖
npm install

# 启动开发服务器（默认 http://localhost:5173）
npm run dev

# 生产构建
npm run build

# 预览构建产物
npm run preview
```

### 可选：本地 API 服务

部分历史接口通过 Vite 代理转发到 `http://localhost:3000`（见 `vite.config.js`）。如需启动：

```bash
npm run dev:api
# 等价于：npm --prefix ../../script/api-server run dev
```

当前 Demo 主流程（登录、员工、店铺、运营数据、任务分配）**不依赖**该服务，数据保存在浏览器 localStorage。

---

## 项目结构

```
dev/vue-site/
├── index.html
├── vite.config.js          # 路径别名 @ → src，/api 代理
├── package.json
└── src/
    ├── main.js             # 应用入口，初始化 Demo 数据
    ├── App.vue
    ├── router/index.js     # 路由与守卫
    ├── stores/
    │   └── auth.js         # 登录态、角色、企业/员工信息
    ├── layouts/
    │   ├── AuthLayout.vue      # 登录/注册壳
    │   └── PortalLayout.vue    # 工作台侧栏 + 内容区（用户信息在侧栏底部）
    ├── views/
    │   ├── auth/               # LoginView, RegisterView
    │   ├── boss/               # 企业管理员：总览、任务分配、员工/账户绑定
    │   ├── employee/           # 员工：工作台、任务中心、AI 办公
    │   ├── temu/ aliexpress/ amazon/ walmart/ alibaba1688/ dtc/
    ├── components/
    │   ├── auth/               # 分屏布局、SaaS 插画
    │   ├── dashboard/          # 运营总览、问题面板、每日报告
    │   ├── accounts/           # BindStoreDialog 等账户绑定组件
    │   ├── ai/                 # AI 办公对话面板
    │   ├── temu/ aliexpress/ amazon/ walmart/ alibaba1688/ dtc/ common/
    ├── api/                    # 数据访问层（Facade）
    │   ├── auth.js / authLocal.js
    │   ├── employees.js / employeesLocal.js
    │   ├── platformAccounts.js / platformAccountsLocal.js
    │   ├── assignedTasks.js / assignedTasksLocal.js   # 管理员任务分配
    │   ├── opsFeedback.js / opsFeedbackLocal.js       # 员工任务反馈
    │   ├── operationsOverview.js   # 运营总览 + 任务中心聚合
    │   ├── temu*.js aliexpress*.js amazon*.js walmart*.js alibaba1688*.js dtc*.js
    │   └── http.js
    ├── utils/
    │   ├── scope.js                # 按角色过滤可见店铺/菜单
    │   ├── storeAssignment.js      # 店铺 → 负责人映射
    │   ├── operationsOverview.js   # 各平台问题项聚合
    │   ├── employeeTasks.js        # 任务中心：预警 + 计划 + 分配任务
    │   ├── dailyOpsReport.js       # 管理员每日运营报告
    │   └── temu.js aliexpress.js amazon.js walmart.js ...
    ├── constants/
    │   ├── platforms.js employees.js assignedTasks.js opsFeedbackDemo.js
    │   ├── aiOffice.js             # AI 办公技能与 Mock 回复
    │   └── temu.js temuOps.js aliexpressDemo.js amazonDaily.js walmartDemo.js ...
    ├── composables/
    │   ├── useStoreAssignees.js
    │   └── useYotoMascot.js        # 登录页密码框 focus 遮眼（可选交互）
    └── assets/
        ├── main.css theme.css auth-panel.css
```

---

## 架构与数据流

### 整体分层

```
Views（页面）
    ↓ 调用
API Facade（src/api/*.js）
    ↓ 当前 Demo 主要走
Local 实现（*Local.js + localStorage）
    ↓ 读取
Constants（静态样本） + Utils（计算/聚合）
```

页面 **不直接** 读写 localStorage，统一通过 `src/api/` 层访问，便于后续替换为真实 HTTP 接口。

### 运营总览数据链路

```mermaid
flowchart TD
  A[账户绑定 platformAccountsLocal] --> B[各平台店铺列表]
  C[员工绑定 employeesLocal] --> D[assignedStoreIds / platforms]
  B --> E[scopeStores 按角色过滤]
  D --> E
  E --> F[Temu / AE / Amazon / Walmart / 1688 / DTC 运营数据]
  F --> G[buildOperationsOverview]
  C --> H[buildStoreAssigneeMap 负责人标注]
  H --> G
  G --> I[BossDashboardView / OperationsIssuesPanel]
```

入口函数：`loadOperationsOverview(auth)`（`src/api/operationsOverview.js`）

### 任务协同数据链路

```mermaid
flowchart LR
  subgraph 自动生成
    P[各平台运营问题] --> T1[employeeTasks 预警任务 source=issue]
    O[OPERATION_TASKS 计划] --> T2[计划任务 source=plan]
  end
  subgraph 管理员分配
    B[TaskAssignmentView] --> AT[assignedTasksLocal]
    AT --> T3[分配任务 source=assigned]
  end
  T1 --> TC[buildEmployeeTaskCenter / buildBossTaskCenter]
  T2 --> TC
  T3 --> TC
  TC --> EV[员工 TasksView]
  EV --> FB[opsFeedbackLocal 提交反馈]
  FB --> DR[dailyOpsReport 每日报告]
  DR --> BD[BossDashboardView DailyOpsReportPanel]
  EV -->|更新状态| AT
```

---

## 身份与权限

### 两种角色

| 角色 | 路由前缀 | UI 文案 | 能力 |
|------|----------|---------|------|
| 企业管理员 | `/boss/*` | 企业管理员 | 全店铺可见；员工/账户绑定；运营总览；**任务分配**；每日运营报告 |
| 员工 | `/employee/*` | 员工端口 | 仅可见被分配店铺或所属平台；任务中心；提交反馈；AI 办公 |

> 代码内部仍使用 `boss` / `isBoss` 命名，界面已统一为「企业管理员」。

### 权限过滤（`src/utils/scope.js`）

- **`scopeStores(stores, auth)`** — 管理员返回全部店铺；员工按 `assignedStoreIds` 或 `platforms` 过滤
- **`employeeModuleMenus(auth)`** — 按员工绑定平台动态生成侧栏菜单
- **`employeeHasPlatform(auth, platform)`** — 模块内 Tab / 功能是否展示

### 路由守卫（`router/index.js`）

1. 未登录 → 重定向 `/login`
2. 已登录访问登录/注册页 → 按角色跳转默认首页
3. 角色与路由 `meta.role` 不匹配 → 跳回各自首页

Pinia 状态 **未持久化**，刷新页面会丢失登录态（Demo 行为）。

---

## 路由一览

### 认证

| 路径 | 页面 | 说明 |
|------|------|------|
| `/login` | LoginView | 企业管理员 / 员工登录 |
| `/register` | RegisterView | 企业注册 |

### 企业管理员 `/boss`

| 路径 | 页面 | 说明 |
|------|------|------|
| `/boss/employees` | EmployeeBindingView | 员工 CRUD、平台权限、店铺分配 |
| `/boss/dashboard` | BossDashboardView | 跨平台运营总览 + 每日运营报告 |
| `/boss/tasks` | TaskAssignmentView | **向员工分配任务** |
| `/boss/temu` | TemuModuleView | Temu 专项 |
| `/boss/aliexpress` | AliExpressModuleView | 速卖通专项 |
| `/boss/amazon` | AmazonModuleView | Amazon 专项 |
| `/boss/walmart` | WalmartModuleView | Walmart 专项 |
| `/boss/1688` | Alibaba1688ModuleView | 1688 专项 |
| `/boss/dtc` | DtcModuleView | 独立站专项 |
| `/boss/accounts` | AccountBindingView | 多平台店铺账户绑定 |

### 员工 `/employee`

| 路径 | 页面 | 说明 |
|------|------|------|
| `/employee/dashboard` | DashboardView | 个人工作台 |
| `/employee/tasks` | TasksView | **任务中心**（预警 + 计划 + 管理员分配） |
| `/employee/temu` 等 | 与各平台 ModuleView 共用 | 按权限显示 |
| `/employee/ai` | AiOfficeView | AI 办公（Mock 对话 + 技能快捷入口） |

---

## 数据层设计

### API Facade 与 Local 实现

典型模式：

```
src/api/employees.js          → 对外导出 fetchEmployees / saveEmployee ...
src/api/employeesLocal.js     → localStorage 读写实现
```

| 模块 | Facade | Local 存储 Key（localStorage） |
|------|--------|-------------------------------|
| 企业账号 | `auth.js` | `crosshub_auth_users` |
| 员工 | `employees.js` | `crosshub_employees` |
| 店铺绑定 | `platformAccounts.js` | `crosshub_platform_stores` |
| **任务分配** | `assignedTasks.js` | `crosshub_assigned_tasks` |
| **任务反馈** | `opsFeedback.js` | `crosshub_ops_feedback` |
| Temu 补货状态 | `temuRestockLocal.js` | `crosshub_temu_restock_status` |
| Temu 竞店 | `temuCompetitorsLocal.js` | 多个 key，见对应文件 |
| AliExpress 订单/违规 | `aliexpress*Local.js` | 按店铺 lazy 写入 |
| Amazon 一日运营 | `amazonDailyLocal.js` | 买家消息、账户、差评、优惠券等 |
| Walmart 订单/Listing | `walmart*Local.js` | 按店铺 lazy 写入 |
| 1688 采购 | `alibaba1688DemoLocal.js` | 按店铺 lazy 写入 |
| DTC 订单 | `dtcOrdersLocal.js` | 按店铺 lazy 写入 |

### 任务分配 API（`assignedTasks.js`）

| 方法 | 说明 |
|------|------|
| `fetchAssignedTasks(filters?)` | 查询已分配任务 |
| `assignTaskToEmployee(payload, employees)` | 向指定员工分配任务 |
| `updateAssignedTask(id, payload)` | 编辑任务 |
| `cancelAssignedTask(id)` | 取消任务 |
| `removeAssignedTask(id)` | 删除任务 |
| `updateAssignedTaskStatus(id, status, extra?)` | 更新状态（员工反馈时调用） |
| `fetchAssignedTasksForCenter(auth, employees)` | 转为任务中心统一结构 |

### 平台常量（`src/constants/platforms.js`）

```text
跨境平台：temu | aliexpress | amazon | walmart | 1688
独立站：  shopify | wordpress
```

DTC 相关 API 会合并 Shopify 与 WordPress 店铺为统一「独立站」视图。

### 远程 HTTP（预留）

- `src/api/http.js`：`fetch` 封装，基址 `VITE_API_BASE_URL`
- `vite.config.js`：`/api` → `localhost:3000`
- `script/api-server/`：Express 示例服务（内存存储，仅 Temu / AliExpress 绑定）

接入真实后端时，只需在 Facade 层将 `*Local.js` 调用替换为 `http.request(...)`，**View 层无需大改**。

---

## 核心业务模块

### 1. 账户绑定（`AccountBindingView`）

- 统一列表 + 平台筛选芯片，替代原先多卡片布局
- 通过 `BindStoreDialog` 弹窗绑定/编辑店铺
- 数据写入 `platformAccountsLocal`，后续所有运营模块通过 `fetchPlatformStores(platform)` 读取

### 2. 员工绑定（`EmployeeBindingView`）

- 维护员工账号、岗位、平台权限、`assignedStoreIds`
- `validateStoreAssignmentConflict` 防止同一店铺分配给多人
- 员工登录后 `auth.employee` 携带权限信息

### 3. 运营总览（`BossDashboardView`）

| 组件 | 说明 |
|------|------|
| `OperationsSummaryHeader` | 各平台指标摘要 |
| `OperationsIssuesPanel` | 跨平台待办/异常（补货、亏损、订单、违规等） |
| `OperationsTasksPanel` | 任务列表（含分配任务） |
| `DailyOpsReportPanel` | **每日运营报告**：汇总问题处理进度与员工反馈 |

数据来源：`loadOperationsOverview(auth)` 一次性聚合各平台 payload、任务中心与日报。

### 4. 任务分配（`TaskAssignmentView`）— 管理员

- 路径：`/boss/tasks`
- 向员工指派运营任务：标题、说明、平台、类型、优先级、截止时间
- 支持编辑、取消、删除；按员工/状态筛选
- 分配后任务出现在对应员工的 **任务中心**，来源标记为「管理员分配」

### 5. 任务中心（`TasksView`）— 员工

任务来源三类，由 `utils/employeeTasks.js` 聚合：

| 来源 | `source` | 说明 |
|------|----------|------|
| 运营预警 | `issue` | 从各平台运营问题自动生成，按员工平台/店铺权限过滤 |
| 计划任务 | `plan` | 来自 `constants/operations.js` 的 `OPERATION_TASKS` |
| 管理员分配 | `assigned` | 来自 `assignedTasksLocal` |

功能：

- 按平台分组展示，支持状态/优先级筛选
- **提交反馈**：处理结果 + 说明 → 写入 `opsFeedbackLocal`，管理员可在日报查看
- 对 `assigned` 类型任务，反馈后同步更新 `assignedTasksLocal` 中的状态

### 6. Temu 运营（`TemuModuleView`）

- 商品样本：`constants/temu.js` → `utils/temu.js` enrich（利润、滞销、补货 urgency）
- 子面板：概览、亏损 SKU、滞销、爆款播报、补货计划、竞店分析
- 补货处理状态：`temuRestockLocal.js`

### 7. AliExpress 运营（`AliExpressModuleView`）

- 订单、违规记录：首次加载时 `ensureAliexpressDemoData` 生成
- 管理员/员工视图共用，通过 `scopeStores` 过滤

### 8. Amazon 运营（`AmazonModuleView`）

围绕卖家 **一日运营工作流** 设计，共 7 项巡检 + 今日工作台：

| 步骤 | 模块 | 说明 |
|------|------|------|
| 1 | 买家消息 | 24h 内回复，支持统一回复模板 |
| 2 | 账户状况 | ODR、迟发率、健康评级 |
| 3 | 差评预警 | 1-3 星评价预警与跟进 |
| 4 | 优惠券 | 过期、即将过期、配置异常预警 |
| 5 | 卖家新闻 | 平台通知自动归纳 |
| 6 | 货件到货 | 送达、缺件等异常预警 |
| 7 | Case 回复 | 平台 Case 新回复提醒 |

数据：`constants/amazonDaily.js` + `api/amazonDailyLocal.js`

### 9. Walmart 运营（`WalmartModuleView`）

- **今日订单**：WFS 仓发与 Seller Fulfilled 自发货分开展示
- **Listing 问题**：未发布、内容错误、价格异常、库存不一致等
- 管理员概览：指标条 + 店铺维度汇总 + 快捷跳转 Tab
- 数据：`constants/walmartDemo.js` + `api/walmartOrdersLocal.js` / `walmartListingsLocal.js`

### 10. 1688 运营（`Alibaba1688ModuleView`）

- 采购单、供应商预警 Demo
- 负责人列通过 `useStoreAssignees` 注入

### 11. 独立站 DTC（`DtcModuleView`）

- Shopify / WordPress 店铺合并展示
- 今日订单、流量、活动等面板（Demo 数据）

### 12. AI 办公（`AiOfficeView`）

- Copilot 式布局：左侧技能快捷入口，中间对话区，右侧上下文面板
- `AiChatPanel` + `constants/aiOffice.js` Mock 回复
- 支持按平台/场景切换预设技能（补货分析、Listing 优化等 Demo）

### 13. 登录页

- `AuthSplitLayout` — 左品牌文案 + SaaS 插画（`AuthHeroIllustration`），右表单
- Demo 账号芯片一键填充
- 密码框 focus 时可选 Yoto 遮眼交互（`useYotoMascot`）

---

## 关键工具与 Composables

| 文件 | 用途 |
|------|------|
| `utils/scope.js` | 店铺/菜单级权限过滤 |
| `utils/storeAssignment.js` | 店铺负责人映射、问题分组、分配冲突校验 |
| `utils/operationsOverview.js` | 将各平台原始数据转为统一「问题项」结构 |
| `utils/employeeTasks.js` | 任务中心聚合：预警 + 计划 + 分配任务 |
| `utils/dailyOpsReport.js` | 管理员每日运营报告生成 |
| `utils/platformMetrics.js` | 平台销售行汇总 |
| `utils/operations.js` | 任务过滤等 |
| `composables/useStoreAssignees.js` | 页面内加载员工并 enrich 列表行 |
| `composables/useYotoMascot.js` | 登录页遮眼状态共享 |

### 负责人标注模式

多数表格使用 `AssigneeTableColumn` / `AssigneeTag`，数据流：

```text
fetchEmployees → buildStoreAssigneeMap → attachAssignee / enrichWithAssignee
```

---

## Demo 账号

### 企业管理员

| 账号 | 密码 |
|------|------|
| `admin@crosshub.cn` | `12345678` |

### 员工（节选，完整列表见 `constants/employees.js`）

| 姓名 | 账号 | 密码 | 平台 |
|------|------|------|------|
| 王一鸣 | `wangyiming@yituo-outdoor.com` | `Emp@Demo123` | Temu |
| 赵磊 | `zhaolei@yituo-outdoor.com` | `Emp@Demo654` | 1688 |
| 刘洋 | `liuyang@yituo-outdoor.com` | `Emp@Demo987` | Amazon |
| 周婷 | `zhouting@yituo-outdoor.com` | `Emp@Demo852` | Walmart |
| 张强 | `zhangqiang@yituo-outdoor.com` | `Emp@Demo789` | AliExpress |
| 陈敏 | `chenmin@yituo-outdoor.com` | `Emp@Demo321` | 独立站 |

登录页提供 Demo 芯片一键填充。

### 推荐体验路径

1. **管理员**登录 → `任务分配` 向「王一鸣」分配 Temu 相关任务
2. 切换 **员工「王一鸣」** → `任务中心` 查看预警 + 分配任务 → 提交反馈
3. 切回 **管理员** → `运营总览` 查看 `DailyOpsReportPanel` 中的反馈汇总

---

## 开发约定

### 路径别名

`@/` → `src/`（Vite + VS Code 均已配置）

### 新增平台模块建议步骤

1. 在 `constants/platforms.js` 注册平台 key  
2. 扩展 `platformAccountsLocal` Demo 店铺（如需要）  
3. 添加 `constants/<platform>.js` 静态样本 + `utils/<platform>.js` 计算  
4. 添加 `api/<platform>.js` 与 `*DemoLocal.js`  
5. 在 `operationsOverview.js` 的 `loadOperationsOverview` 中接入聚合  
6. 在 `employeeTasks.js` 中补充该平台的问题 → 任务映射  
7. 新建 `views/<platform>/` 与 `components/<platform>/`  
8. 在 `router/index.js` 与 `PortalLayout.vue` 注册路由/菜单  

### 样式

- 全局主题与设计令牌：`assets/theme.css`（Soybean/Arco 风格 CSS 变量）
- 登录表单共享：`assets/auth-panel.css`（非 scoped，避免 `:deep` 穿透 Element Plus）
- Portal 侧栏：`PortalLayout.vue` scoped 样式；用户信息固定在侧栏底部

### 组件命名

- 页面：`views/<域>/<Name>View.vue`
- 平台面板：`<Platform><Feature>Panel.vue` / `<Platform>BossOverview.vue`
- 通用：`components/common/PageHeader.vue`、`PageScroll.vue`

---

## 构建与部署

```bash
npm run build   # 输出到 dist/
npm run preview # 本地预览 dist
```

静态资源可部署至任意静态托管（Nginx、OSS、Vercel 等）。若需对接后端 API，构建时设置环境变量：

```bash
VITE_API_BASE_URL=https://api.example.com npm run build
```

---

## 仓库关联

| 路径 | 说明 |
|------|------|
| `dev/vue-site/` | 本前端项目（CrossHub 主应用） |
| `script/api-server/` | 可选 Express Demo API（账户绑定原型） |

---

## 常见问题

**Q: 刷新后为什么要重新登录？**  
A: 当前 Pinia 未做 persist，属 Demo 行为。生产环境可在 `auth` store 增加 sessionStorage / Cookie 持久化。

**Q: 如何清空本地 Demo 数据？**  
A: 浏览器开发者工具 → Application → Local Storage → 删除 `crosshub_*` 前缀项，刷新后 `main.js` 会重新种子化。

**Q: 员工看不到某个平台菜单？**  
A: 检查 `EmployeeBindingView` 中该员工的 `platforms` 与 `assignedStoreIds` 配置。

**Q: 运营总览数据为空？**  
A: 确认 `账户绑定` 中已有对应平台店铺，且当前登录角色有权限看到它们。

**Q: 管理员分配的任务员工看不到？**  
A: 确认任务 `employeeId` 与当前登录员工一致，且任务状态不是「已取消」。分配任务写入 `crosshub_assigned_tasks`。

**Q: 员工提交的反馈管理员在哪里看？**  
A: 管理员登录 → `运营总览` → `DailyOpsReportPanel`（每日运营报告区域）。

---

## License

Private / Demo — 仅供内部开发与演示使用。
