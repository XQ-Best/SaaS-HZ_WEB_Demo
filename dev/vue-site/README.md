# CrossHub 跨境运营管理平台

CrossHub 是一套面向跨境企业的 **SaaS 运营管理工作台** Demo。支持企业管理员与员工分级登录，覆盖 Temu、AliExpress、Amazon、1688、独立站（Shopify / WordPress）等多平台运营场景，提供账户绑定、运营总览、异常预警、任务协同与平台专项分析。

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

当前 Demo 主流程（登录、员工、店铺、运营数据）**不依赖**该服务，数据保存在浏览器 localStorage。

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
    │   ├── AuthLayout.vue      # 登录/注册深色背景壳
    │   └── PortalLayout.vue    # 工作台侧栏 + 顶栏
    ├── views/                  # 页面（按业务域划分）
    │   ├── auth/               # LoginView, RegisterView
    │   ├── boss/               # 企业管理员：总览、员工绑定、账户绑定
    │   ├── employee/           # 员工：工作台、任务、AI 办公
    │   ├── temu/               # Temu 运营模块
    │   ├── aliexpress/         # AliExpress 运营模块
    │   ├── amazon/             # Amazon 运营模块
    │   ├── alibaba1688/        # 1688 采购/运营模块
    │   └── dtc/                # 独立站运营模块
    ├── components/             # 可复用 UI（按平台/功能分子目录）
    │   ├── auth/               # 分屏布局、Yoto 互动小助手
    │   ├── dashboard/          # 运营总览、问题面板、任务面板
    │   ├── temu/ aliexpress/ amazon/ alibaba1688/ dtc/ ai/ common/ accounts/
    ├── api/                    # 数据访问层（Facade）
    │   ├── auth.js             # 登录/注册对外 API
    │   ├── authLocal.js        # 企业账号 localStorage 实现
    │   ├── employees.js / employeesLocal.js
    │   ├── platformAccounts.js / platformAccountsLocal.js
    │   ├── operationsOverview.js   # 运营总览聚合入口
    │   ├── operationalContext.js   # 别名导出
    │   ├── temu*.js aliexpress*.js amazon*.js alibaba1688*.js dtc*.js
    │   └── http.js             # fetch 封装（对接远程 API 时使用）
    ├── utils/                  # 纯函数：计算、过滤、格式化
    │   ├── scope.js            # 按角色过滤可见店铺/菜单
    │   ├── storeAssignment.js  # 店铺 → 负责人映射
    │   ├── operationsOverview.js  # 各平台问题项聚合
    │   ├── temu.js aliexpress.js amazon.js alibaba1688.js dtcStore.js ...
    ├── constants/              # 静态 Demo 数据与枚举
    │   ├── platforms.js        # 平台分类定义
    │   ├── employees.js        # Demo 员工样本
    │   ├── temu.js temuOps.js  # Temu 商品/补货状态
    │   ├── aliexpressDemo.js amazonDaily.js alibaba1688.js dtcOrders.js ...
    ├── composables/            # 组合式逻辑
    │   ├── useStoreAssignees.js
    │   └── useYotoMascot.js    # 登录页 Yoto 遮眼交互
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

运营总览是串联全站逻辑的核心：

```mermaid
flowchart TD
  A[账户绑定 platformAccountsLocal] --> B[各平台店铺列表]
  C[员工绑定 employeesLocal] --> D[assignedStoreIds / platforms]
  B --> E[scopeStores 按角色过滤]
  D --> E
  E --> F[Temu 商品 / AE 订单 / Amazon 订单 / 1688 采购 / DTC 订单]
  F --> G[buildOperationsOverview]
  C --> H[buildStoreAssigneeMap 负责人标注]
  H --> G
  G --> I[BossDashboardView / OperationsIssuesPanel]
```

入口函数：`loadOperationsOverview(auth)`（`src/api/operationsOverview.js`）

### 启动时 Demo 种子数据

`main.js` 在应用挂载前调用：

| 函数 | 作用 |
|------|------|
| `ensureDefaultUser()` | 写入默认企业管理员账号 |
| `ensureDemoStores()` | 写入各平台 Demo 店铺 |
| `ensureDemoEmployees()` | 同步 Demo 员工（可覆盖更新） |
| `ensureDemoCompetitors()` | Temu 竞店分析样本 |

---

## 身份与权限

### 两种角色

| 角色 | 路由前缀 | UI 文案 | 能力 |
|------|----------|---------|------|
| 企业管理员 | `/boss/*` | 企业管理员 | 全店铺可见；员工绑定；账户绑定；运营总览 |
| 员工 | `/employee/*` | 员工端口 | 仅可见被分配店铺或所属平台店铺 |

> 代码内部仍使用 `boss` / `isBoss` 命名，界面已统一为「企业管理员」。

### 权限过滤（`src/utils/scope.js`）

- **`scopeStores(stores, auth)`**  
  - 管理员：返回全部店铺  
  - 员工：优先按 `assignedStoreIds` 过滤；若未分配具体店铺，则按 `platforms` 过滤

- **`employeeModuleMenus(auth)`**  
  根据员工绑定的平台动态生成侧栏菜单（如仅有 Temu 权限则只显示 Temu 模块）

- **`employeeHasPlatform(auth, platform)`**  
  模块内 Tab / 功能是否展示

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
| `/boss/dashboard` | BossDashboardView | 跨平台运营总览 |
| `/boss/temu` | TemuModuleView | Temu 专项 |
| `/boss/aliexpress` | AliExpressModuleView | 速卖通专项 |
| `/boss/amazon` | AmazonModuleView | Amazon 专项 |
| `/boss/1688` | Alibaba1688ModuleView | 1688 专项 |
| `/boss/dtc` | DtcModuleView | 独立站专项 |
| `/boss/accounts` | AccountBindingView | 多平台店铺账户绑定 |

### 员工 `/employee`

| 路径 | 页面 | 说明 |
|------|------|------|
| `/employee/dashboard` | DashboardView | 个人工作台 |
| `/employee/tasks` | TasksView | 任务中心 |
| `/employee/temu` 等 | 与各平台 ModuleView 共用 | 按权限显示 |
| `/employee/ai` | AiOfficeView | AI 办公（Mock 对话） |

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
| Temu 补货状态 | `temuRestockLocal.js` | `crosshub_temu_restock_status` |
| Temu 竞店 | `temuCompetitorsLocal.js` | 多个 key，见对应文件 |
| AliExpress 订单/违规 | `aliexpress*Local.js` | 按店铺 lazy 写入 |
| Amazon 一日运营 | `amazonDailyLocal.js` | 买家消息、账户、差评、优惠券等 |
| 1688 采购 | `alibaba1688DemoLocal.js` | 按店铺 lazy 写入 |
| DTC 订单 | `dtcOrdersLocal.js` | 按店铺 lazy 写入 |

### 平台常量（`src/constants/platforms.js`）

```text
跨境平台：temu | aliexpress | amazon | 1688
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

- 企业管理员绑定各平台店铺账号
- 数据写入 `platformAccountsLocal`
- 后续所有运营模块通过 `fetchPlatformStores(platform)` 读取

### 2. 员工绑定（`EmployeeBindingView`）

- 维护员工账号、岗位、平台权限、`assignedStoreIds`
- `validateStoreAssignmentConflict` 防止同一店铺分配给多人
- 员工登录后 `auth.employee` 携带权限信息

### 3. 运营总览（`BossDashboardView`）

组件：

- `OperationsSummaryHeader` — 各平台指标摘要
- `OperationsIssuesPanel` — 跨平台待办/异常（补货、亏损、订单、违规等）
- `OperationsTasksPanel` — 任务列表

数据来源：`loadOperationsOverview(auth)` 一次性聚合五平台 payload。

### 4. Temu 运营（`TemuModuleView`）

- 商品样本：`constants/temu.js` → `utils/temu.js`  enrich（利润、滞销、补货 urgency）
- 子面板：概览、亏损 SKU、滞销、爆款播报、补货计划、竞店分析
- 补货处理状态：`temuRestockLocal.js`

### 5. AliExpress 运营（`AliExpressModuleView`）

- 订单、违规记录：首次加载时 `ensureAliexpressDemoData` 生成
- 管理员/员工视图共用，通过 `scopeStores` 过滤

### 6. Amazon 运营（`AmazonModuleView`）

围绕卖家 **一日运营工作流** 设计，共 7 项巡检 + 今日工作台：

| 步骤 | 模块 | 说明 |
|------|------|------|
| 1 | 买家消息 | 24h 内回复，支持统一回复模板，避免迟复扣绩效 |
| 2 | 账户状况 | 每日反映 ODR、迟发率、健康评级；爆红指标优先处理 |
| 3 | 差评预警 | 1-3 星评价预警与跟进 |
| 4 | 优惠券 | 过期、即将过期、配置异常预警 |
| 5 | 卖家新闻 | 平台通知自动归纳，白话报送 |
| 6 | 货件到货 | 送达、缺件、完成无货等异常预警 |
| 7 | Case 回复 | 平台 Case 新回复单独提醒 |

数据：`constants/amazonDaily.js` + `api/amazonDailyLocal.js`

### 7. 1688 运营（`Alibaba1688ModuleView`）

- 采购单、供应商预警 Demo
- 负责人列通过 `useStoreAssignees` 注入

### 8. 独立站 DTC（`DtcModuleView`）

- Shopify / WordPress 店铺合并展示
- 今日订单、流量、活动等面板（Demo 数据）

### 9. 登录页 Yoto 小助手

- `AuthSplitLayout` — 左品牌 + 文案，右表单
- `AuthInteractiveScene` — SVG 角色，眼球跟随鼠标
- `useYotoMascot` — 密码框 focus 时遮眼（LoginView / RegisterView 联动）

---

## 关键工具与 Composables

| 文件 | 用途 |
|------|------|
| `utils/scope.js` | 店铺/菜单级权限过滤 |
| `utils/storeAssignment.js` | 店铺负责人映射、问题分组、分配冲突校验 |
| `utils/operationsOverview.js` | 将各平台原始数据转为统一「问题项」结构 |
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
| 张强 | `zhangqiang@yituo-outdoor.com` | `Emp@Demo789` | AliExpress |
| 陈敏 | `chenmin@yituo-outdoor.com` | `Emp@Demo321` | 独立站 |

登录页提供 Demo 芯片一键填充。

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
6. 新建 `views/<platform>/` 与 `components/<platform>/`  
7. 在 `router/index.js` 与 `PortalLayout.vue` 注册路由/菜单  

### 样式

- 全局主题：`assets/theme.css`
- 登录表单共享：`assets/auth-panel.css`（非 scoped，避免 `:deep` 穿透 Element Plus）
- Portal 侧栏：`PortalLayout.vue` scoped 样式

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

---

## License

Private / Demo — 仅供内部开发与演示使用。
