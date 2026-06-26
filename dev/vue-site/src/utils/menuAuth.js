import {
  Briefcase,
  Box,
  CircleCheck,
  DataAnalysis,
  DocumentChecked,
  Goods,
  House,
  Key,
  Link,
  Sell,
  Setting,
  Shop,
  ShoppingBag,
  ShoppingCart,
  Tickets,
  TrendCharts,
  UserFilled,
  Van,
  VideoCamera,
  VideoPlay,
} from '@element-plus/icons-vue'
import { employeeModuleMenus } from '@/utils/scope'

const MENU_ICONS = {
  'boss.settings': Setting,
  'boss.employees': UserFilled,
  'boss.warehouse_sites': House,
  'boss.warehouse_staff': Box,
  'boss.dashboard': TrendCharts,
  'boss.tasks': Tickets,
  'boss.accounts': Key,
  'boss.warehouse': Box,
  'employee.warehouse': Box,
  'warehouse.pending_review': DocumentChecked,
  'warehouse.pending_shipment': Van,
  'warehouse.shipped': CircleCheck,
  'warehouse.tasks': Briefcase,
  'warehouse.dashboard': TrendCharts,
  'employee.dashboard': TrendCharts,
  'employee.tasks': Briefcase,
  'employee.ai': DataAnalysis,
}

const PLATFORM_ICONS = {
  temu: Shop,
  aliexpress: Goods,
  amazon: Sell,
  walmart: ShoppingBag,
  pdd: ShoppingCart,
  douyin: VideoCamera,
  channels: VideoPlay,
  '1688': ShoppingCart,
  dtc: Link,
  shopify: Link,
  wordpress: Link,
}

export function iconForMenu(menu) {
  if (MENU_ICONS[menu.code]) return MENU_ICONS[menu.code]
  if (menu.platform && PLATFORM_ICONS[menu.platform]) return PLATFORM_ICONS[menu.platform]
  return Shop
}

export function decorateMenus(menus = []) {
  return (Array.isArray(menus) ? menus : []).map((menu) => ({
    ...menu,
    index: menu.path && menu.path !== '#' ? menu.path : menu.code,
    icon: iconForMenu(menu),
  }))
}

function sortMenus(a, b) {
  return (a.sort_order ?? 0) - (b.sort_order ?? 0)
}

export function buildSidebarTree(flatMenus = []) {
  const items = decorateMenus(flatMenus).sort(sortMenus)
  const byCode = new Map(items.map((menu) => [menu.code, { ...menu, children: [] }]))
  const roots = []

  for (const menu of items) {
    const node = byCode.get(menu.code)
    const parentCode = menu.parent_code || menu.parentCode
    if (parentCode && byCode.has(parentCode)) {
      byCode.get(parentCode).children.push(node)
    } else {
      roots.push(node)
    }
  }

  for (const node of byCode.values()) {
    node.children.sort(sortMenus)
  }

  return roots.sort(sortMenus)
}

export function flattenMenuPaths(menus = []) {
  const paths = []
  for (const menu of menus) {
    if (menu.path && menu.path !== '#') paths.push(menu.path)
    if (menu.children?.length) paths.push(...flattenMenuPaths(menu.children))
  }
  return paths
}

export function settingsMenuOpenKeys(path = '') {
  if (path.startsWith('/boss/employees') || path.startsWith('/boss/accounts') || path.startsWith('/boss/warehouse-staff') || path.startsWith('/boss/warehouse-sites')) {
    return ['boss.settings']
  }
  return []
}

export function fallbackSidebarMenus(auth) {
  if (auth.isWarehouse) {
    return buildSidebarTree([
      { code: 'warehouse.pending_review', path: '/warehouse/pending-review', label: '待审核', menu_type: 'base', sort_order: 10 },
      { code: 'warehouse.pending_shipment', path: '/warehouse/pending-shipment', label: '待发货', menu_type: 'base', sort_order: 20 },
      { code: 'warehouse.shipped', path: '/warehouse/shipped', label: '已发货', menu_type: 'base', sort_order: 30 },
      { code: 'warehouse.tasks', path: '/warehouse/tasks', label: '任务中心', menu_type: 'base', sort_order: 40 },
    ])
  }

  if (auth.isBoss) {
    return buildSidebarTree([
      { code: 'boss.dashboard', path: '/boss/dashboard', label: '运营总览', menu_type: 'admin', sort_order: 10 },
      { code: 'boss.tasks', path: '/boss/tasks', label: '任务分配', menu_type: 'admin', sort_order: 20 },
      { code: 'boss.warehouse', path: '/boss/warehouse-orders', label: '仓库下单', menu_type: 'admin', sort_order: 25 },
      { code: 'boss.platform.temu', path: '/boss/temu', label: 'Temu 运营', platform: 'temu', menu_type: 'module', sort_order: 30 },
      { code: 'boss.platform.aliexpress', path: '/boss/aliexpress', label: 'AliExpress 运营', platform: 'aliexpress', menu_type: 'module', sort_order: 40 },
      { code: 'boss.platform.amazon', path: '/boss/amazon', label: 'Amazon 运营', platform: 'amazon', menu_type: 'module', sort_order: 50 },
      { code: 'boss.platform.walmart', path: '/boss/walmart', label: 'Walmart 运营', platform: 'walmart', menu_type: 'module', sort_order: 60 },
      { code: 'boss.platform.pdd', path: '/boss/pdd', label: '拼多多运营', platform: 'pdd', menu_type: 'module', sort_order: 70 },
      { code: 'boss.platform.douyin', path: '/boss/douyin', label: '抖音运营', platform: 'douyin', menu_type: 'module', sort_order: 80 },
      { code: 'boss.platform.channels', path: '/boss/channels', label: '视频号运营', platform: 'channels', menu_type: 'module', sort_order: 90 },
      { code: 'boss.platform.1688', path: '/boss/1688', label: '1688 运营', platform: '1688', menu_type: 'module', sort_order: 100 },
      { code: 'boss.platform.dtc', path: '/boss/dtc', label: '独立站运营', platform: 'dtc', menu_type: 'module', sort_order: 110 },
      { code: 'boss.settings', path: '#', label: '设置', menu_type: 'group', sort_order: 120 },
      { code: 'boss.employees', parent_code: 'boss.settings', path: '/boss/employees', label: '运营绑定', menu_type: 'admin', sort_order: 121 },
      { code: 'boss.warehouse_sites', parent_code: 'boss.settings', path: '/boss/warehouse-sites', label: '仓库设置', menu_type: 'admin', sort_order: 122 },
      { code: 'boss.warehouse_staff', parent_code: 'boss.settings', path: '/boss/warehouse-staff', label: '仓库人员', menu_type: 'admin', sort_order: 123 },
      { code: 'boss.accounts', parent_code: 'boss.settings', path: '/boss/accounts', label: '账户绑定', menu_type: 'admin', sort_order: 124 },
    ])
  }

  const platformMenus = employeeModuleMenus(auth).map((item, index) => ({
    code: `employee.platform.${item.platform}`,
    path: item.index,
    label: item.label,
    platform: item.platform,
    menu_type: 'module',
    sort_order: 20 + index * 10,
  }))

  const menuCodes = auth.employee?.menuCodes || []
  const hasWarehouseGrant = menuCodes.includes('employee.warehouse')

  const warehouseMenu = {
    code: 'employee.warehouse',
    path: '/employee/warehouse-orders',
    label: '仓库下单',
    menu_type: 'module',
    sort_order: 85,
  }

  return buildSidebarTree([
    { code: 'employee.dashboard', path: '/employee/dashboard', label: '我的工作台', menu_type: 'base', sort_order: 10 },
    ...platformMenus,
    ...(hasWarehouseGrant ? [warehouseMenu] : []),
    { code: 'employee.tasks', path: '/employee/tasks', label: '任务中心', menu_type: 'base', sort_order: 90 },
    { code: 'employee.ai', path: '/employee/ai', label: 'AI 办公', menu_type: 'base', sort_order: 100 },
  ])
}

export function resolveSidebarMenus(auth) {
  const decorated = buildSidebarTree(auth.menus || [])
  if (decorated.length) return decorated
  return fallbackSidebarMenus(auth)
}

export function canAccessRoute(auth, to) {
  const record = [...to.matched].reverse().find((item) => item.meta?.menuCode)
  if (!record?.meta?.menuCode) return true

  if (auth.backendLinked) {
    if (auth.isWarehouse) {
      return auth.hasMenuCode(record.meta.menuCode) || record.meta.menuCode?.startsWith('warehouse.')
    }
    return auth.hasMenuCode(record.meta.menuCode)
  }

  const requiredRole = to.matched.find((item) => item.meta.role)?.meta.role
  if (requiredRole && requiredRole !== auth.role) return false

  if (auth.isBoss || auth.isWarehouse) return true

  const allowedPaths = new Set(flattenMenuPaths(resolveSidebarMenus(auth)))
  return allowedPaths.has(to.path)
}

export function defaultLandingPath(auth) {
  const first = auth.menuPaths[0]
  if (first) return first
  return auth.isBoss ? '/boss/dashboard' : auth.isWarehouse ? '/warehouse/pending-review' : '/employee/dashboard'
}
