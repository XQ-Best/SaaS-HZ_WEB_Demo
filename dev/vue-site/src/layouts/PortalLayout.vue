<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Bell,
  Briefcase,
  DataAnalysis,
  Goods,
  Key,
  Link,
  Sell,
  Shop,
  ShoppingCart,
  TrendCharts,
  User,
  UserFilled,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { employeeModuleMenus } from '@/utils/scope'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const bossMenus = [
  { index: '/boss/employees', label: '员工绑定', icon: UserFilled },
  { index: '/boss/dashboard', label: '运营总览', icon: TrendCharts },
  { index: '/boss/temu', label: 'Temu 运营', icon: Shop },
  { index: '/boss/aliexpress', label: 'AliExpress 运营', icon: Goods },
  { index: '/boss/amazon', label: 'Amazon 运营', icon: Sell },
  { index: '/boss/1688', label: '1688 运营', icon: ShoppingCart },
  { index: '/boss/dtc', label: '独立站运营', icon: Link },
  { index: '/boss/accounts', label: '账户绑定', icon: Key },
]

const employeeBaseMenus = [
  { index: '/employee/dashboard', label: '我的工作台', icon: TrendCharts },
  { index: '/employee/tasks', label: '任务中心', icon: Briefcase },
  { index: '/employee/ai', label: 'AI 办公', icon: DataAnalysis },
]

const platformMenuIcons = {
  temu: Shop,
  aliexpress: Goods,
  amazon: Sell,
  '1688': ShoppingCart,
  shopify: Link,
  wordpress: Link,
}

const menus = computed(() => {
  if (auth.isBoss) return bossMenus

  const platformMenus = employeeModuleMenus(auth).map((item) => ({
    ...item,
    icon: platformMenuIcons[item.platform] || Shop,
  }))

  return [
    employeeBaseMenus[0],
    ...platformMenus,
    ...employeeBaseMenus.slice(1),
  ]
})

const activeMenu = computed(() => route.path)
const pageTitle = computed(() => route.meta.title || 'CrossHub')

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <el-container class="portal">
    <el-aside width="280px" class="portal-aside">
      <div class="brand">
        <div class="brand-mark">CH</div>
        <div class="brand-text">
          <strong>CrossHub</strong>
          <span>{{ auth.portalLabel }}</span>
        </div>
      </div>

      <el-menu :default-active="activeMenu" router class="portal-menu">
        <el-menu-item v-for="item in menus" :key="item.index" :index="item.index">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>

      <div class="aside-footer">
        <div class="user-chip">
          <div class="user-chip-head">
            <el-avatar :size="32" class="user-avatar">{{ auth.displayName.slice(0, 1) }}</el-avatar>
            <span class="user-role">{{ auth.isBoss ? '企业管理员' : auth.employee.role || '运营专员' }}</span>
          </div>
          <p class="user-name" :title="auth.displayName">{{ auth.displayName }}</p>
        </div>
        <el-button class="logout-btn" size="small" @click="handleLogout">退出登录</el-button>
      </div>
    </el-aside>

    <el-container class="portal-body">
      <el-header class="portal-header">
        <div class="header-title">
          <p class="header-eyebrow">{{ auth.portalLabel }}</p>
          <h2>{{ pageTitle }}</h2>
        </div>
        <div class="header-actions">
          <el-button :icon="Bell" circle class="icon-btn" />
          <el-dropdown>
            <el-button class="profile-btn">
              <el-icon><User /></el-icon>
              <span>{{ auth.displayName }}</span>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>{{ auth.company.name }}</el-dropdown-item>
                <el-dropdown-item disabled>{{ auth.company.account }}</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="portal-main">
        <div class="portal-main-inner">
          <router-view v-slot="{ Component }">
            <component :is="Component" class="portal-page" />
          </router-view>
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.portal {
  height: 100vh;
  overflow: hidden;
  background: var(--ch-page-gradient);
}

.portal-aside {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  flex-shrink: 0;
  background: linear-gradient(180deg, var(--ch-sidebar-bg) 0%, var(--ch-sidebar-bg-end) 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 4px 0 24px rgba(15, 23, 42, 0.12);
}

.portal > .el-container {
  flex: 1;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
}

.portal-body {
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.brand {
  display: flex;
  gap: 14px;
  align-items: center;
  padding: 24px 20px 20px;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 50%, #0ea5e9 100%);
  color: #fff;
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 0.04em;
  box-shadow: 0 4px 14px rgba(79, 70, 229, 0.45);
}

.brand-text strong {
  display: block;
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #f8fafc;
}

.brand-text span {
  display: block;
  margin-top: 2px;
  color: var(--ch-sidebar-text);
  font-size: 12px;
}

.portal-menu {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 8px 12px;
  border-right: none;
  background: transparent;
}

.portal-menu :deep(.el-menu-item) {
  height: 44px;
  margin-bottom: 4px;
  border-radius: 10px;
  color: var(--ch-sidebar-text);
  font-weight: 500;
  transition: background 0.15s ease, color 0.15s ease;
}

.portal-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.06);
  color: #f1f5f9;
}

.portal-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(79, 70, 229, 0.35) 0%, rgba(14, 165, 233, 0.15) 100%);
  color: var(--ch-sidebar-text-active);
  font-weight: 600;
  box-shadow: inset 0 0 0 1px rgba(129, 140, 248, 0.25);
}

.portal-menu :deep(.el-menu) {
  background: transparent;
  border: none;
}

.portal-menu :deep(.el-menu-item .el-icon) {
  font-size: 18px;
}

.aside-footer {
  display: grid;
  gap: 12px;
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.user-chip {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
}

.user-chip-head {
  display: flex;
  gap: 10px;
  align-items: center;
}

.user-avatar {
  background: linear-gradient(135deg, #6366f1, #0ea5e9);
  color: #fff;
  font-weight: 600;
  flex-shrink: 0;
}

.user-role {
  font-size: 11px;
  color: var(--ch-sidebar-text);
}

.user-name {
  margin: 0;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.4;
  color: #f8fafc;
  white-space: nowrap;
}

.logout-btn {
  width: 100%;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
  color: #e2e8f0;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.portal-header {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: space-between;
  height: auto;
  padding: 18px 28px;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--ch-border);
}

.header-eyebrow {
  margin: 0 0 2px;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--el-text-color-secondary);
}

.portal-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 650;
  letter-spacing: -0.03em;
  color: var(--el-text-color-primary);
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.icon-btn {
  border: 1px solid var(--ch-border);
  background: var(--ch-surface);
}

.profile-btn {
  display: inline-flex;
  gap: 6px;
  align-items: center;
  border: 1px solid var(--ch-border);
  background: var(--ch-surface);
  font-weight: 500;
}

.profile-btn span {
  white-space: nowrap;
}

.portal-main {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  padding: 0 !important;
  background: transparent;
  display: flex;
  flex-direction: column;
}

.portal-main-inner {
  flex: 1;
  min-height: 0;
  padding: 24px 28px 28px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.portal-main-inner :deep(.portal-page) {
  flex: 1;
  min-height: 0;
  min-width: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
</style>
