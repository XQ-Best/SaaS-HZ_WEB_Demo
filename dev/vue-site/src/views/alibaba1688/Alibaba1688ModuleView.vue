<script setup>
import { computed, onActivated, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { loadAlibaba1688OperationalData } from '@/api/alibaba1688'
import { fetchAlibaba1688Stores } from '@/api/platformAccounts'
import { scopeStores } from '@/utils/scope'
import { useStoreAssignees } from '@/composables/useStoreAssignees'
import PageHeader from '@/components/common/PageHeader.vue'
import PageScroll from '@/components/common/PageScroll.vue'
import Alibaba1688BossOverview from '@/components/alibaba1688/Alibaba1688BossOverview.vue'
import Alibaba1688PurchasePanel from '@/components/alibaba1688/Alibaba1688PurchasePanel.vue'
import Alibaba1688SupplierPanel from '@/components/alibaba1688/Alibaba1688SupplierPanel.vue'

const auth = useAuthStore()
const router = useRouter()
const { assigneeMap, loadAssignees, enrichItems } = useStoreAssignees()
const activeTab = ref('purchase')
const selectedStoreId = ref('all')
const stores1688 = ref([])
const purchaseOrders = ref([])
const supplierAlerts = ref([])
const syncedAt = ref('')
const loadingStores = ref(false)

const storeNameMap = computed(() =>
  Object.fromEntries(stores1688.value.map((store) => [store.id, store.storeName])),
)

const enrichedOrders = computed(() => enrichItems(purchaseOrders.value))
const enrichedAlerts = computed(() => enrichItems(supplierAlerts.value))

const filteredOrders = computed(() => {
  if (selectedStoreId.value === 'all') return enrichedOrders.value
  return enrichedOrders.value.filter((order) => order.storeId === selectedStoreId.value)
})

const filteredAlerts = computed(() => {
  if (selectedStoreId.value === 'all') return enrichedAlerts.value
  return enrichedAlerts.value.filter((alert) => alert.storeId === selectedStoreId.value)
})

const overviewStores = computed(() => {
  if (selectedStoreId.value === 'all') return stores1688.value
  return stores1688.value.filter((store) => store.id === selectedStoreId.value)
})

const showStoreList = computed(
  () => selectedStoreId.value === 'all' && stores1688.value.length > 0,
)

const showStoreColumn = computed(() => selectedStoreId.value === 'all')

const pendingPurchaseCount = computed(() =>
  filteredOrders.value.filter((order) => order.isActionNeeded).length,
)

const openAlertCount = computed(() =>
  filteredAlerts.value.filter((alert) => alert.isOpen).length,
)

async function loadModuleData() {
  loadingStores.value = true
  try {
    const res = await fetchAlibaba1688Stores()
    stores1688.value = scopeStores(res.data || [], auth)
    if (stores1688.value.length) {
      const demoRes = loadAlibaba1688OperationalData(stores1688.value)
      purchaseOrders.value = demoRes.data.purchaseOrders
      supplierAlerts.value = demoRes.data.supplierAlerts
      syncedAt.value = demoRes.data.syncedAt
    } else {
      purchaseOrders.value = []
      supplierAlerts.value = []
      syncedAt.value = ''
    }
  } catch {
    stores1688.value = []
    purchaseOrders.value = []
    supplierAlerts.value = []
    syncedAt.value = ''
  } finally {
    loadingStores.value = false
  }
}

function refreshData() {
  if (!stores1688.value.length) return
  const demoRes = loadAlibaba1688OperationalData(stores1688.value)
  purchaseOrders.value = demoRes.data.purchaseOrders
  supplierAlerts.value = demoRes.data.supplierAlerts
  syncedAt.value = demoRes.data.syncedAt
  ElMessage.success('已刷新 1688 运营数据')
}

function goToAccountBinding() {
  router.push(auth.isBoss ? '/boss/accounts' : '/employee/dashboard')
}

watch(stores1688, (stores) => {
  if (selectedStoreId.value === 'all') return
  if (!stores.some((store) => store.id === selectedStoreId.value)) {
    selectedStoreId.value = 'all'
  }
})

onMounted(async () => {
  await loadAssignees()
  await loadModuleData()
})
onActivated(loadModuleData)
</script>

<template>
  <PageScroll>
    <template #header>
      <div v-if="stores1688.length" class="page-toolbar">
        <el-radio-group v-model="selectedStoreId" size="small">
          <el-radio-button value="all">全部账号</el-radio-button>
          <el-radio-button
            v-for="store in stores1688"
            :key="store.id"
            :value="store.id"
          >
            {{ store.storeName }}
          </el-radio-button>
        </el-radio-group>
      </div>

      <PageHeader
        v-else-if="!stores1688.length && !auth.isBoss"
        title="1688 运营"
        :description="`${auth.employee.name} · 采购订单与供应商跟进`"
      />
    </template>

    <el-empty
      v-if="!loadingStores && !stores1688.length"
      description="暂无可见的 1688 采购账号"
      :image-size="96"
    >
      <el-text type="info" size="small">
        {{ auth.isBoss ? '请先在「账户绑定」中绑定 1688 采购账号' : '请联系企业管理员在运营绑定中分配负责账号' }}
      </el-text>
      <el-button v-if="auth.isBoss" type="primary" style="margin-top: 16px" @click="goToAccountBinding">
        前往账户绑定
      </el-button>
    </el-empty>

    <template v-else-if="stores1688.length">
      <Alibaba1688BossOverview
        v-if="auth.isBoss"
        :purchase-orders="filteredOrders"
        :supplier-alerts="filteredAlerts"
        :stores="overviewStores"
        :assignee-map="assigneeMap"
        :show-store-list="showStoreList"
        @navigate="activeTab = $event"
      />

      <el-tabs v-model="activeTab" class="module-tabs">
        <el-tab-pane name="purchase">
          <template #label>
            <span>采购订单</span>
            <el-badge v-if="pendingPurchaseCount" :value="pendingPurchaseCount" class="tab-badge" />
          </template>
          <div class="tab-panel">
            <Alibaba1688PurchasePanel
              :orders="filteredOrders"
              :synced-at="syncedAt"
              :loading="loadingStores"
              :show-store-column="showStoreColumn"
              :store-name-map="storeNameMap"
              @refresh="refreshData"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane name="supplier">
          <template #label>
            <span>供应商跟进</span>
            <el-badge v-if="openAlertCount" :value="openAlertCount" class="tab-badge" />
          </template>
          <div class="tab-panel">
            <Alibaba1688SupplierPanel
              :alerts="filteredAlerts"
              :synced-at="syncedAt"
              :loading="loadingStores"
              :show-store-column="showStoreColumn"
              :store-name-map="storeNameMap"
              @refresh="refreshData"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </template>
  </PageScroll>
</template>

<style scoped>
.page-toolbar {
  margin-bottom: 16px;
}

.module-tabs {
  margin-top: 20px;
}

.tab-panel {
  padding: 16px 0 4px;
}

.tab-badge {
  margin-left: 6px;
  vertical-align: middle;
}

.tab-badge :deep(.el-badge__content) {
  position: relative;
  transform: none;
  vertical-align: middle;
}
</style>
