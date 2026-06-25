<script setup>
import { computed, onActivated, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import {
  loadAmazonDailyWorkflow,
  replyBuyerMessage,
  handleReview,
  acknowledgeCase,
} from '@/api/amazon'
import { fetchAmazonStores } from '@/api/platformAccounts'
import { scopeStores } from '@/utils/scope'
import { useStoreAssignees } from '@/composables/useStoreAssignees'
import { buildAmazonDailyChecklist } from '@/utils/amazon'
import PageHeader from '@/components/common/PageHeader.vue'
import PageScroll from '@/components/common/PageScroll.vue'
import AmazonDailyOverview from '@/components/amazon/AmazonDailyOverview.vue'
import AmazonBuyerMessagesPanel from '@/components/amazon/AmazonBuyerMessagesPanel.vue'
import AmazonAccountHealthPanel from '@/components/amazon/AmazonAccountHealthPanel.vue'
import AmazonReviewsPanel from '@/components/amazon/AmazonReviewsPanel.vue'
import AmazonCouponsPanel from '@/components/amazon/AmazonCouponsPanel.vue'
import AmazonSellerNewsPanel from '@/components/amazon/AmazonSellerNewsPanel.vue'
import AmazonShipmentsPanel from '@/components/amazon/AmazonShipmentsPanel.vue'
import AmazonCasesPanel from '@/components/amazon/AmazonCasesPanel.vue'

const auth = useAuthStore()
const { assigneeMap, loadAssignees, enrichItems } = useStoreAssignees()
const router = useRouter()

const activeTab = ref('dashboard')
const selectedStoreId = ref('all')
const amazonStores = ref([])
const workflow = ref(emptyWorkflow())
const syncedAt = ref('')
const loadingStores = ref(false)
const loading = ref(false)

const messagesPanel = ref(null)
const reviewsPanel = ref(null)

const storeNameMap = computed(() =>
  Object.fromEntries(amazonStores.value.map((s) => [s.id, s.storeName])),
)

const showStoreColumn = computed(() => selectedStoreId.value === 'all')
const showStoreList = computed(
  () => selectedStoreId.value === 'all' && amazonStores.value.length > 0,
)

const overviewStores = computed(() => {
  if (selectedStoreId.value === 'all') return amazonStores.value
  return amazonStores.value.filter((s) => s.id === selectedStoreId.value)
})

function emptyWorkflow() {
  return {
    buyerMessages: [],
    accountMetrics: [],
    reviews: [],
    coupons: [],
    sellerNews: [],
    shipments: [],
    cases: [],
  }
}

function filterByStore(items) {
  if (selectedStoreId.value === 'all') return enrichItems(items)
  return enrichItems(items.filter((i) => i.storeId === selectedStoreId.value))
}

const filtered = computed(() => ({
  buyerMessages: filterByStore(workflow.value.buyerMessages),
  accountMetrics: filterByStore(workflow.value.accountMetrics),
  reviews: filterByStore(workflow.value.reviews),
  coupons: filterByStore(workflow.value.coupons),
  sellerNews: filterByStore(workflow.value.sellerNews),
  shipments: filterByStore(workflow.value.shipments),
  cases: filterByStore(workflow.value.cases),
}))

const checklist = computed(() => buildAmazonDailyChecklist(filtered.value))

const tabBadges = computed(() => {
  const map = Object.fromEntries(checklist.value.map((s) => [s.tab, s.count]))
  return {
    dashboard: 0,
    messages: map.messages || 0,
    account: map.account || 0,
    reviews: map.reviews || 0,
    coupons: map.coupons || 0,
    news: map.news || 0,
    shipments: map.shipments || 0,
    cases: map.cases || 0,
  }
})

function applyWorkflowData(data) {
  workflow.value = {
    buyerMessages: data.buyerMessages || [],
    accountMetrics: data.accountMetrics || [],
    reviews: data.reviews || [],
    coupons: data.coupons || [],
    sellerNews: data.sellerNews || [],
    shipments: data.shipments || [],
    cases: data.cases || [],
  }
  syncedAt.value = data.syncedAt || ''
}

async function syncWorkflow() {
  if (!amazonStores.value.length) {
    applyWorkflowData(emptyWorkflow())
    return
  }
  loading.value = true
  try {
    const res = loadAmazonDailyWorkflow(amazonStores.value)
    applyWorkflowData(res.data)
  } catch (err) {
    ElMessage.error(err.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function loadModule() {
  loadingStores.value = true
  try {
    const res = await fetchAmazonStores()
    amazonStores.value = scopeStores(res.data || [], auth)
    if (amazonStores.value.length) {
      await syncWorkflow()
    } else {
      applyWorkflowData(emptyWorkflow())
    }
  } catch {
    amazonStores.value = []
    applyWorkflowData(emptyWorkflow())
  } finally {
    loadingStores.value = false
  }
}

function goToAccountBinding() {
  router.push(auth.isBoss ? '/boss/accounts' : '/employee/dashboard')
}

function handleNavigate(tab) {
  activeTab.value = tab
}

async function onReplyMessage(payload) {
  try {
    const res = replyBuyerMessage(payload.id, payload)
    const idx = workflow.value.buyerMessages.findIndex((m) => m.id === payload.id)
    if (idx !== -1) workflow.value.buyerMessages[idx] = res.data
    ElMessage.success('已回复买家消息')
  } catch (err) {
    ElMessage.error(err.message || '回复失败')
  } finally {
    messagesPanel.value?.finishReply?.()
  }
}

async function onHandleReview(payload) {
  try {
    const res = handleReview(payload.id, payload)
    const idx = workflow.value.reviews.findIndex((r) => r.id === payload.id)
    if (idx !== -1) workflow.value.reviews[idx] = res.data
    ElMessage.success('已标记差评处理')
  } catch (err) {
    ElMessage.error(err.message || '操作失败')
  } finally {
    reviewsPanel.value?.finishHandle?.()
  }
}

async function onAcknowledgeCase(id) {
  try {
    const res = acknowledgeCase(id)
    const idx = workflow.value.cases.findIndex((c) => c.id === id)
    if (idx !== -1) workflow.value.cases[idx] = res.data
    ElMessage.success('已标记 Case 已读')
  } catch (err) {
    ElMessage.error(err.message || '操作失败')
  }
}

watch(amazonStores, (stores) => {
  if (selectedStoreId.value === 'all') return
  if (!stores.some((s) => s.id === selectedStoreId.value)) {
    selectedStoreId.value = 'all'
  }
})

onMounted(async () => {
  await loadAssignees()
  await loadModule()
})
onActivated(loadModule)
</script>

<template>
  <PageScroll>
    <template #header>
      <div v-if="amazonStores.length" class="page-toolbar">
        <el-radio-group v-model="selectedStoreId" size="small">
          <el-radio-button value="all">全部店铺</el-radio-button>
          <el-radio-button v-for="store in amazonStores" :key="store.id" :value="store.id">
            {{ store.storeName }}
          </el-radio-button>
        </el-radio-group>
      </div>

      <PageHeader
        v-else-if="!amazonStores.length && !auth.isBoss"
        title="Amazon 运营"
        :description="`${auth.employee.name} · 一日运营工作流`"
      />
    </template>

    <el-empty
      v-if="!loadingStores && !amazonStores.length"
      description="暂无可见的 Amazon 店铺"
      :image-size="96"
    >
      <el-text type="info" size="small">
        {{ auth.isBoss ? '请先在「账户绑定」中绑定 Amazon 店铺' : '请联系企业管理员分配负责店铺' }}
      </el-text>
      <el-button v-if="auth.isBoss" type="primary" style="margin-top: 16px" @click="goToAccountBinding">
        前往账户绑定
      </el-button>
    </el-empty>

    <template v-else-if="amazonStores.length">
      <el-tabs v-model="activeTab" class="module-tabs">
        <el-tab-pane name="dashboard">
          <template #label>
            <span>今日工作台</span>
          </template>
          <div class="tab-panel">
            <AmazonDailyOverview
              :workflow="filtered"
              :stores="overviewStores"
              :assignee-map="assigneeMap"
              :show-store-list="showStoreList"
              @navigate="handleNavigate"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane name="messages">
          <template #label>
            <span>买家消息</span>
            <el-badge v-if="tabBadges.messages" :value="tabBadges.messages" class="tab-badge" />
          </template>
          <div class="tab-panel">
            <AmazonBuyerMessagesPanel
              ref="messagesPanel"
              :messages="filtered.buyerMessages"
              :synced-at="syncedAt"
              :loading="loading"
              :show-store-column="showStoreColumn"
              :store-name-map="storeNameMap"
              @reply="onReplyMessage"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane name="account">
          <template #label>
            <span>账户状况</span>
            <el-badge v-if="tabBadges.account" :value="tabBadges.account" class="tab-badge" />
          </template>
          <div class="tab-panel">
            <AmazonAccountHealthPanel
              :metrics="filtered.accountMetrics"
              :synced-at="syncedAt"
              :loading="loading"
              :show-store-column="showStoreColumn"
              :store-name-map="storeNameMap"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane name="reviews">
          <template #label>
            <span>差评预警</span>
            <el-badge v-if="tabBadges.reviews" :value="tabBadges.reviews" class="tab-badge" />
          </template>
          <div class="tab-panel">
            <AmazonReviewsPanel
              ref="reviewsPanel"
              :reviews="filtered.reviews"
              :synced-at="syncedAt"
              :loading="loading"
              :show-store-column="showStoreColumn"
              :store-name-map="storeNameMap"
              @handle="onHandleReview"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane name="coupons">
          <template #label>
            <span>优惠券</span>
            <el-badge v-if="tabBadges.coupons" :value="tabBadges.coupons" class="tab-badge" />
          </template>
          <div class="tab-panel">
            <AmazonCouponsPanel
              :coupons="filtered.coupons"
              :synced-at="syncedAt"
              :loading="loading"
              :show-store-column="showStoreColumn"
              :store-name-map="storeNameMap"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane name="news">
          <template #label>
            <span>卖家新闻</span>
            <el-badge v-if="tabBadges.news" :value="tabBadges.news" class="tab-badge" />
          </template>
          <div class="tab-panel">
            <AmazonSellerNewsPanel
              :news="filtered.sellerNews"
              :synced-at="syncedAt"
              :loading="loading"
              :show-store-column="showStoreColumn"
              :store-name-map="storeNameMap"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane name="shipments">
          <template #label>
            <span>货件到货</span>
            <el-badge v-if="tabBadges.shipments" :value="tabBadges.shipments" class="tab-badge" />
          </template>
          <div class="tab-panel">
            <AmazonShipmentsPanel
              :shipments="filtered.shipments"
              :synced-at="syncedAt"
              :loading="loading"
              :show-store-column="showStoreColumn"
              :store-name-map="storeNameMap"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane name="cases">
          <template #label>
            <span>Case 回复</span>
            <el-badge v-if="tabBadges.cases" :value="tabBadges.cases" class="tab-badge" />
          </template>
          <div class="tab-panel">
            <AmazonCasesPanel
              :cases="filtered.cases"
              :synced-at="syncedAt"
              :loading="loading"
              :show-store-column="showStoreColumn"
              :store-name-map="storeNameMap"
              @acknowledge="onAcknowledgeCase"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </template>
  </PageScroll>
</template>

<style scoped>
.page-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.module-tabs :deep(.el-tabs__header) {
  margin-bottom: 4px;
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
