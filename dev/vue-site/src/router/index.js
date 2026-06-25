import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      component: () => import('@/layouts/AuthLayout.vue'),
      children: [
        { path: '', name: 'login', component: () => import('@/views/auth/LoginView.vue') },
      ],
    },
    {
      path: '/register',
      component: () => import('@/layouts/AuthLayout.vue'),
      children: [
        { path: '', name: 'register', component: () => import('@/views/auth/RegisterView.vue') },
      ],
    },
    {
      path: '/boss',
      component: () => import('@/layouts/PortalLayout.vue'),
      meta: { role: 'boss' },
      children: [
        { path: '', redirect: '/boss/employees' },
        { path: 'employees', name: 'boss-employees', component: () => import('@/views/boss/EmployeeBindingView.vue'), meta: { title: '员工绑定' } },
        { path: 'dashboard', name: 'boss-dashboard', component: () => import('@/views/boss/BossDashboardView.vue'), meta: { title: '运营总览' } },
        { path: 'tasks', name: 'boss-tasks', component: () => import('@/views/boss/TaskAssignmentView.vue'), meta: { title: '任务分配' } },
        { path: 'temu', name: 'boss-temu', component: () => import('@/views/temu/TemuModuleView.vue'), meta: { title: 'Temu 运营' } },
        { path: 'aliexpress', name: 'boss-aliexpress', component: () => import('@/views/aliexpress/AliExpressModuleView.vue'), meta: { title: 'AliExpress 运营' } },
        { path: 'amazon', name: 'boss-amazon', component: () => import('@/views/amazon/AmazonModuleView.vue'), meta: { title: 'Amazon 运营' } },
        { path: 'walmart', name: 'boss-walmart', component: () => import('@/views/walmart/WalmartModuleView.vue'), meta: { title: 'Walmart 运营' } },
        { path: 'pdd', name: 'boss-pdd', component: () => import('@/views/pdd/PddModuleView.vue'), meta: { title: '拼多多运营' } },
        { path: 'douyin', name: 'boss-douyin', component: () => import('@/views/douyin/DouyinModuleView.vue'), meta: { title: '抖音运营' } },
        { path: 'channels', name: 'boss-channels', component: () => import('@/views/channels/ChannelsModuleView.vue'), meta: { title: '视频号运营' } },
        { path: '1688', name: 'boss-1688', component: () => import('@/views/alibaba1688/Alibaba1688ModuleView.vue'), meta: { title: '1688 运营' } },
        { path: 'dtc', name: 'boss-dtc', component: () => import('@/views/dtc/DtcModuleView.vue'), meta: { title: '独立站运营' } },
        { path: 'accounts', name: 'boss-accounts', component: () => import('@/views/boss/AccountBindingView.vue'), meta: { title: '账户绑定' } },
      ],
    },
    {
      path: '/employee',
      component: () => import('@/layouts/PortalLayout.vue'),
      meta: { role: 'employee' },
      children: [
        { path: '', redirect: '/employee/dashboard' },
        { path: 'dashboard', name: 'employee-dashboard', component: () => import('@/views/employee/DashboardView.vue'), meta: { title: '我的工作台' } },
        { path: 'tasks', name: 'employee-tasks', component: () => import('@/views/employee/TasksView.vue'), meta: { title: '任务中心' } },
        { path: 'temu', name: 'employee-temu', component: () => import('@/views/temu/TemuModuleView.vue'), meta: { title: 'Temu 运营' } },
        { path: 'aliexpress', name: 'employee-aliexpress', component: () => import('@/views/aliexpress/AliExpressModuleView.vue'), meta: { title: 'AliExpress 运营' } },
        { path: 'amazon', name: 'employee-amazon', component: () => import('@/views/amazon/AmazonModuleView.vue'), meta: { title: 'Amazon 运营' } },
        { path: 'walmart', name: 'employee-walmart', component: () => import('@/views/walmart/WalmartModuleView.vue'), meta: { title: 'Walmart 运营' } },
        { path: 'pdd', name: 'employee-pdd', component: () => import('@/views/pdd/PddModuleView.vue'), meta: { title: '拼多多运营' } },
        { path: 'douyin', name: 'employee-douyin', component: () => import('@/views/douyin/DouyinModuleView.vue'), meta: { title: '抖音运营' } },
        { path: 'channels', name: 'employee-channels', component: () => import('@/views/channels/ChannelsModuleView.vue'), meta: { title: '视频号运营' } },
        { path: '1688', name: 'employee-1688', component: () => import('@/views/alibaba1688/Alibaba1688ModuleView.vue'), meta: { title: '1688 运营' } },
        { path: 'dtc', name: 'employee-dtc', component: () => import('@/views/dtc/DtcModuleView.vue'), meta: { title: '独立站运营' } },
        { path: 'ai', name: 'employee-ai', component: () => import('@/views/employee/AiOfficeView.vue'), meta: { title: 'AI 办公' } },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/login' },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.path === '/login' || to.path === '/register') {
    if (auth.isLoggedIn) {
      return auth.isBoss ? '/boss/employees' : '/employee/dashboard'
    }
    return true
  }

  if (!auth.isLoggedIn) return '/login'

  const requiredRole = to.matched.find((r) => r.meta.role)?.meta.role
  if (requiredRole && requiredRole !== auth.role) {
    return auth.isBoss ? '/boss/employees' : '/employee/dashboard'
  }

  return true
})

export default router
