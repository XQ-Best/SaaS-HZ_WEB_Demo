import { computed, onActivated, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { scopeStores } from '@/utils/scope'
import { useStoreAssignees } from '@/composables/useStoreAssignees'
import { enrichDomesticIssue } from '@/utils/domesticPlatform'
import PageHeader from '@/components/common/PageHeader.vue'
import PageScroll from '@/components/common/PageScroll.vue'
import DomesticBossOverview from '@/components/domestic/DomesticBossOverview.vue'
import DomesticOrdersPanel from '@/components/domestic/DomesticOrdersPanel.vue'
import DomesticIssuesPanel from '@/components/domestic/DomesticIssuesPanel.vue'

export function useDomesticModule(config) {
  const auth = useAuthStore()
  const { assigneeMap, loadAssignees, enrichItems } = useStoreAssignees()
  const router = useRouter()

  const activeTab = ref('orders')
  const selectedStoreId = ref('all')
  const stores = ref([])
  const todayOrders = ref([])
  const issues = ref([])
  const ordersSyncedAt = ref('')
  const issuesSyncedAt = ref('')
  const loadingStores = ref(false)
  const loadingOrders = ref(false)
  const loadingIssues = ref(false)
  const issuesPanel = ref(null)
  const issuesFilter = ref('all')

  const storeNameMap = computed(() =>
    Object.fromEntries(stores.value.map((store) => [store.id, store.storeName])),
  )

  const enrichedOrders = computed(() => enrichItems(todayOrders.value))
  const enrichedIssues = computed(() =>
    enrichItems(issues.value.map((issue) => enrichDomesticIssue(issue, config.issueTypeMap))),
  )

  const showStoreColumn = computed(() => selectedStoreId.value === 'all')
  const showStoreList = computed(() => selectedStoreId.value === 'all' && stores.value.length > 0)

  const overviewStores = computed(() => {
    if (selectedStoreId.value === 'all') return stores.value
    return stores.value.filter((store) => store.id === selectedStoreId.value)
  })

  const filteredOrders = computed(() => {
    if (selectedStoreId.value === 'all') return enrichedOrders.value
    return enrichedOrders.value.filter((order) => order.storeId === selectedStoreId.value)
  })

  const filteredIssues = computed(() => {
    if (selectedStoreId.value === 'all') return enrichedIssues.value
    return enrichedIssues.value.filter((item) => item.storeId === selectedStoreId.value)
  })

  const pendingOrderCount = computed(() =>
    filteredOrders.value.filter((order) => ['待处理', '待发货'].includes(order.status)).length,
  )

  const pendingIssueCount = computed(() =>
    filteredIssues.value.filter((item) => !item.resolved).length,
  )

  async function syncTodayOrders(refresh = false) {
    if (!stores.value.length) {
      todayOrders.value = []
      ordersSyncedAt.value = ''
      return
    }

    loadingOrders.value = true
    try {
      const res = await config.fetchOrders(stores.value, { refresh })
      todayOrders.value = res.data.orders
      ordersSyncedAt.value = res.data.syncedAt
      if (refresh) ElMessage.success(res.message || '已刷新今日订单')
    } catch (err) {
      ElMessage.error(err.message || '订单抓取失败')
    } finally {
      loadingOrders.value = false
    }
  }

  async function syncIssues(refresh = false) {
    if (!stores.value.length) {
      issues.value = []
      issuesSyncedAt.value = ''
      return
    }

    loadingIssues.value = true
    try {
      const res = refresh
        ? await config.crawlIssues(stores.value, { refresh: true })
        : config.loadIssues(stores.value)
      issues.value = res.data.issues
      issuesSyncedAt.value = res.data.syncedAt
      if (refresh) ElMessage.success(res.message || '已刷新运营预警')
    } catch (err) {
      ElMessage.error(err.message || '预警抓取失败')
    } finally {
      loadingIssues.value = false
    }
  }

  async function handleResolveIssue(payload) {
    try {
      const res = config.resolveIssue(payload.id)
      const index = issues.value.findIndex((item) => item.id === payload.id)
      if (index !== -1) issues.value[index] = res.data
      ElMessage.success('已标记为已解决')
    } catch (err) {
      ElMessage.error(err.message || '操作失败')
    } finally {
      issuesPanel.value?.finishResolve?.()
    }
  }

  async function loadModule() {
    loadingStores.value = true
    try {
      const res = await config.fetchStores()
      stores.value = scopeStores(res.data || [], auth)
      if (stores.value.length) {
        await Promise.all([syncTodayOrders(false), syncIssues(false)])
      } else {
        todayOrders.value = []
        issues.value = []
        ordersSyncedAt.value = ''
        issuesSyncedAt.value = ''
      }
    } catch {
      stores.value = []
      todayOrders.value = []
      issues.value = []
      ordersSyncedAt.value = ''
      issuesSyncedAt.value = ''
    } finally {
      loadingStores.value = false
    }
  }

  function goToAccountBinding() {
    router.push(auth.isBoss ? '/boss/accounts' : '/employee/dashboard')
  }

  function handleOverviewNavigate(target) {
    if (target.startsWith('issues')) {
      activeTab.value = 'issues'
      const filter = target === 'issues:high' ? 'high' : 'open'
      issuesFilter.value = filter
      issuesPanel.value?.setFilter?.(filter)
      return
    }
    activeTab.value = target
  }

  watch(stores, (list) => {
    if (selectedStoreId.value === 'all') return
    if (!list.some((store) => store.id === selectedStoreId.value)) {
      selectedStoreId.value = 'all'
    }
  })

  onMounted(async () => {
    await loadAssignees()
    await loadModule()
  })
  onActivated(loadModule)

  return {
    auth,
    assigneeMap,
    activeTab,
    selectedStoreId,
    stores,
    ordersSyncedAt,
    issuesSyncedAt,
    loadingStores,
    loadingOrders,
    loadingIssues,
    issuesPanel,
    issuesFilter,
    storeNameMap,
    showStoreColumn,
    showStoreList,
    overviewStores,
    filteredOrders,
    filteredIssues,
    pendingOrderCount,
    pendingIssueCount,
    syncTodayOrders,
    syncIssues,
    handleResolveIssue,
    goToAccountBinding,
    handleOverviewNavigate,
    config,
  }
}
