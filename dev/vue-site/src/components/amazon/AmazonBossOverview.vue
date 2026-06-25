<script setup>
import { computed } from 'vue'
import { summarizeTopProducts, summarizeOutboundOrders, acosMeta } from '@/utils/amazonBoss'
import { resolveStoreAssignee } from '@/utils/storeAssignment'
import AssigneeTag from '@/components/common/AssigneeTag.vue'

const props = defineProps({
  products: { type: Array, default: () => [] },
  outboundOrders: { type: Array, default: () => [] },
  stores: { type: Array, default: () => [] },
  assigneeMap: { type: Object, default: () => ({}) },
  showStoreList: { type: Boolean, default: true },
})

const emit = defineEmits(['navigate'])

const productSummary = computed(() => summarizeTopProducts(props.products, 20))
const outboundSummary = computed(() => summarizeOutboundOrders(props.outboundOrders))

const avgAcosMeta = computed(() => acosMeta(productSummary.value.avgAcos))

const keyMetrics = computed(() => [
  {
    label: 'TOP20 销售额',
    value: productSummary.value.totalRevenueText,
    hint: `7 日 · ${productSummary.value.top.length} SKU`,
  },
  {
    label: '平均 ACOS',
    value: `${productSummary.value.avgAcos}%`,
    hint: `广告花费 ${productSummary.value.totalAdSpendText}`,
    type: avgAcosMeta.value.type,
  },
  {
    label: 'ACOS 偏高',
    value: productSummary.value.highAcosCount,
    hint: productSummary.value.dangerAcosCount
      ? `${productSummary.value.dangerAcosCount} 个过高需优化`
      : '关注广告效率',
    type: productSummary.value.highAcosCount ? 'danger' : 'success',
  },
  {
    label: '待发货订单',
    value: outboundSummary.value.actionRequired,
    hint: `FBM ${outboundSummary.value.fbmPending} · FBA ${outboundSummary.value.fbaPending}`,
    type: outboundSummary.value.actionRequired ? 'warning' : 'success',
  },
])

const alertItems = computed(() => [
  {
    label: 'ACOS 过高',
    count: productSummary.value.dangerAcosCount,
    tab: 'products:high-acos',
    type: 'danger',
  },
  {
    label: 'ACOS 偏高',
    count: productSummary.value.highAcosCount - productSummary.value.dangerAcosCount,
    tab: 'products',
    type: 'warning',
  },
  {
    label: '待发货',
    count: outboundSummary.value.pending,
    tab: 'outbound',
    type: 'warning',
  },
  {
    label: '待揽收',
    count: outboundSummary.value.packed,
    tab: 'outbound:packed',
    type: 'primary',
  },
])

const highAcosProducts = computed(() =>
  productSummary.value.top
    .filter((p) => ['warning', 'danger'].includes(acosMeta(p.acos).level))
    .slice(0, 5),
)
</script>

<template>
  <div class="boss-overview">
    <div class="metrics-bar metrics-bar--4">
      <div v-for="item in keyMetrics" :key="item.label" class="metric-item">
        <div class="metric-value" :class="item.type ? `is-${item.type}` : ''">
          {{ item.value }}
        </div>
        <div class="metric-label">{{ item.label }}</div>
        <div class="metric-hint">{{ item.hint }}</div>
      </div>
    </div>

    <div class="alert-bar">
      <button
        v-for="item in alertItems.filter((i) => i.count > 0)"
        :key="item.tab"
        type="button"
        class="alert-chip"
        :class="`is-${item.type}`"
        @click="emit('navigate', item.tab)"
      >
        <span class="alert-count">{{ item.count }}</span>
        <span>{{ item.label }}</span>
      </button>
    </div>

    <div v-if="highAcosProducts.length" class="acos-alert-card">
      <div class="acos-alert-head">
        <strong>ACOS 需关注</strong>
        <el-button link type="primary" size="small" @click="emit('navigate', 'products:high-acos')">
          查看全部
        </el-button>
      </div>
      <div class="acos-list">
        <div v-for="item in highAcosProducts" :key="item.id" class="acos-row">
          <div class="acos-row__main">
            <span class="acos-rank">#{{ item.displayRank }}</span>
            <span class="acos-name">{{ item.productName }}</span>
          </div>
          <el-tag :type="acosMeta(item.acos).type" size="small">ACOS {{ item.acos }}%</el-tag>
        </div>
      </div>
    </div>

    <el-table
      v-if="showStoreList && stores.length > 1"
      :data="stores"
      size="small"
      class="store-table"
    >
      <el-table-column label="店铺" min-width="140">
        <template #default="{ row }">
          <strong>{{ row.storeName }}</strong>
        </template>
      </el-table-column>
      <el-table-column label="负责人" width="96">
        <template #default="{ row }">
          <AssigneeTag :name="resolveStoreAssignee(row.id, assigneeMap)" />
        </template>
      </el-table-column>
      <el-table-column label="TOP SKU" width="90" align="center">
        <template #default="{ row }">
          {{ products.filter((p) => p.storeId === row.id).length }}
        </template>
      </el-table-column>
      <el-table-column label="待发货" width="80" align="center">
        <template #default="{ row }">
          <el-text
            :type="outboundOrders.filter((o) => o.storeId === row.id && ['pending', 'packed'].includes(o.status)).length ? 'warning' : 'info'"
            size="small"
          >
            {{
              outboundOrders.filter((o) => o.storeId === row.id && ['pending', 'packed'].includes(o.status)).length
            }}
          </el-text>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.boss-overview {
  display: grid;
  gap: 16px;
}

.acos-alert-card {
  padding: 14px 16px;
  border-radius: var(--ch-radius-lg, 12px);
  border: 1px solid var(--el-color-danger-light-7);
  background: linear-gradient(135deg, #fef2f2 0%, #fff 70%);
}

.acos-alert-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.acos-list {
  display: grid;
  gap: 8px;
}

.acos-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 13px;
}

.acos-row__main {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.acos-rank {
  font-weight: 600;
  color: var(--ch-text-muted, var(--el-text-color-secondary));
}

.acos-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
