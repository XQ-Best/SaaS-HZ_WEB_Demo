<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { fetchPlatformStores } from '@/api/platformAccounts'
import { HOT_BROADCASTS, TEMU_PRODUCTS_RAW } from '@/constants/temu'
import { enrichAllProducts } from '@/utils/temu'
import { scopeStores } from '@/utils/scope'
import { useStoreAssignees } from '@/composables/useStoreAssignees'
import PageHeader from '@/components/common/PageHeader.vue'
import PageScroll from '@/components/common/PageScroll.vue'
import TemuOverviewCards from '@/components/temu/TemuOverviewCards.vue'
import TemuBossOverview from '@/components/temu/TemuBossOverview.vue'
import PriceLossTable from '@/components/temu/PriceLossTable.vue'
import SlowMovingPanel from '@/components/temu/SlowMovingPanel.vue'
import HotProductBroadcast from '@/components/temu/HotProductBroadcast.vue'
import RestockPlanner from '@/components/temu/RestockPlanner.vue'
import CompetitorAnalysis from '@/components/temu/CompetitorAnalysis.vue'

const auth = useAuthStore()
const { assigneeMap, loadAssignees, enrichItems } = useStoreAssignees()
const activeTab = ref('profit')
const selectedStoreId = ref('all')
const temuStores = ref([])

const scopedStoreIds = computed(() => new Set(temuStores.value.map((s) => s.id)))

const allProducts = computed(() =>
  enrichAllProducts(
    TEMU_PRODUCTS_RAW.filter((p) => scopedStoreIds.value.has(p.storeId)),
  ),
)

const storeNameMap = computed(() =>
  Object.fromEntries(temuStores.value.map((s) => [s.id, s.storeName])),
)

function withStoreMeta(list) {
  return enrichItems(
    list.map((p) => ({
      ...p,
      storeName: storeNameMap.value[p.storeId] || '未分配店铺',
    })),
  )
}

const products = computed(() => {
  let list = allProducts.value
  if (selectedStoreId.value !== 'all') {
    list = list.filter((p) => p.storeId === selectedStoreId.value)
  }
  return withStoreMeta(list)
})

const overviewProducts = computed(() => {
  if (selectedStoreId.value === 'all') {
    return withStoreMeta(allProducts.value)
  }
  return products.value
})

const overviewStores = computed(() => {
  if (selectedStoreId.value === 'all') {
    return temuStores.value
  }
  return temuStores.value.filter((s) => s.id === selectedStoreId.value)
})

const showStoreList = computed(
  () => selectedStoreId.value === 'all' && temuStores.value.length > 0,
)

const showStoreColumn = computed(() => selectedStoreId.value === 'all')

const alertCount = computed(() => {
  const p = products.value
  return {
    loss: p.filter((i) => i.isLoss).length,
    slow: p.filter((i) => i.slowMoving).length,
    hot: p.filter((i) => i.isHot).length,
    restock: p.filter((i) => i.restock.urgency !== 'normal').length,
  }
})

async function loadTemuStores() {
  try {
    const res = await fetchPlatformStores('temu')
    temuStores.value = scopeStores(res.data || [], auth)
  } catch {
    temuStores.value = []
  }
}

onMounted(async () => {
  await Promise.all([loadTemuStores(), loadAssignees()])
})
</script>

<template>
  <PageScroll>
    <template #header>
      <div v-if="temuStores.length" class="page-toolbar">
        <el-radio-group v-model="selectedStoreId" size="small">
          <el-radio-button value="all">全部店铺</el-radio-button>
          <el-radio-button
            v-for="store in temuStores"
            :key="store.id"
            :value="store.id"
          >
            {{ store.storeName }}
          </el-radio-button>
        </el-radio-group>
      </div>

      <PageHeader
        v-else-if="!temuStores.length && !auth.isBoss"
        title="Temu 运营"
        :description="`${auth.employee.name} · 日常运营与库存管理`"
      />
    </template>

    <el-empty
      v-if="!temuStores.length"
      description="暂无可见的 Temu 店铺"
      :image-size="96"
    >
      <el-text type="info" size="small">
        {{ auth.isBoss ? '请先在「账户绑定」中绑定 Temu 店铺' : '请联系企业管理员在员工绑定中分配负责店铺' }}
      </el-text>
    </el-empty>

    <template v-else>
    <TemuBossOverview
      v-if="auth.isBoss"
      :products="overviewProducts"
      :stores="overviewStores"
      :assignee-map="assigneeMap"
      :show-store-list="showStoreList"
      @navigate="activeTab = $event"
    />

    <TemuOverviewCards v-else :products="products" />

    <el-tabs v-model="activeTab" class="temu-tabs">
      <el-tab-pane name="profit">
        <template #label>
          <span>价格亏损</span>
          <el-badge v-if="alertCount.loss" :value="alertCount.loss" class="tab-badge" />
        </template>
        <PriceLossTable :products="products" :show-store-column="showStoreColumn" />
      </el-tab-pane>

      <el-tab-pane name="slow">
        <template #label>
          <span>滞销预警</span>
          <el-badge v-if="alertCount.slow" :value="alertCount.slow" class="tab-badge" />
        </template>
        <SlowMovingPanel :products="products" :show-store-column="showStoreColumn" />
      </el-tab-pane>

      <el-tab-pane name="hot">
        <template #label>
          <span>爆款通报</span>
          <el-badge v-if="alertCount.hot" :value="alertCount.hot" class="tab-badge" />
        </template>
        <HotProductBroadcast
          :products="products"
          :broadcasts="HOT_BROADCASTS"
        />
      </el-tab-pane>

      <el-tab-pane name="restock">
        <template #label>
          <span>备货分析</span>
          <el-badge v-if="alertCount.restock" :value="alertCount.restock" class="tab-badge" />
        </template>
        <RestockPlanner :products="products" :show-store-column="showStoreColumn" />
      </el-tab-pane>

      <el-tab-pane v-if="auth.isBoss" name="competitor">
        <template #label>
          <span>竞店分析</span>
        </template>
        <CompetitorAnalysis />
      </el-tab-pane>
    </el-tabs>
    </template>
  </PageScroll>
</template>

<style scoped>
.page-toolbar {
  margin-bottom: 16px;
}

.temu-tabs {
  margin-top: 20px;
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
