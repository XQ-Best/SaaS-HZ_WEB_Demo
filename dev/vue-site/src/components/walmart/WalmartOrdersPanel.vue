<script setup>
import { computed, ref } from 'vue'
import {
  WFS_STATUS_TYPE,
  SELLER_STATUS_TYPE,
} from '@/constants/walmartDemo'
import { summarizeWalmartOrders } from '@/utils/walmart'
import { formatMoneyDecimal } from '@/utils/format'
import WalmartPanelHeader from '@/components/walmart/WalmartPanelHeader.vue'
import AssigneeTableColumn from '@/components/common/AssigneeTableColumn.vue'

const props = defineProps({
  orders: { type: Array, default: () => [] },
  syncedAt: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  showStoreColumn: { type: Boolean, default: false },
  storeNameMap: { type: Object, default: () => ({}) },
})

defineEmits(['refresh'])

const orderType = ref('wfs')

const summary = computed(() => summarizeWalmartOrders(props.orders))

const wfsOrders = computed(() => props.orders.filter((order) => order.fulfillmentType === 'wfs'))
const sellerOrders = computed(() =>
  props.orders.filter((order) => order.fulfillmentType === 'seller'),
)

const currentOrders = computed(() =>
  orderType.value === 'wfs' ? wfsOrders.value : sellerOrders.value,
)

function statusType(order) {
  if (order.fulfillmentType === 'wfs') {
    return WFS_STATUS_TYPE[order.status] || 'info'
  }
  return SELLER_STATUS_TYPE[order.status] || 'info'
}
</script>

<template>
  <div class="wm-panel">
    <WalmartPanelHeader
      title="今日订单"
      description="WFS 仓发与 Seller Fulfilled 自发货订单"
      :synced-at="syncedAt"
      action-label="抓取今日订单"
      :loading="loading"
      @action="$emit('refresh')"
    />

    <div class="mini-stats">
      <div class="mini-stat">
        <span class="mini-stat__value">{{ summary.wfsTotal }}</span>
        <span class="mini-stat__label">WFS 订单</span>
        <el-tag v-if="summary.wfsPending" type="warning" size="small" effect="plain">
          {{ summary.wfsPending }} 待处理
        </el-tag>
      </div>
      <div class="mini-stat">
        <span class="mini-stat__value">{{ summary.sellerTotal }}</span>
        <span class="mini-stat__label">自发货订单</span>
        <el-tag v-if="summary.sellerPending" type="warning" size="small" effect="plain">
          {{ summary.sellerPending }} 待处理
        </el-tag>
      </div>
      <div class="mini-stat">
        <span class="mini-stat__value">{{ summary.totalAmountText }}</span>
        <span class="mini-stat__label">当日金额</span>
      </div>
    </div>

    <el-segmented
      v-model="orderType"
      :options="[
        { label: `WFS (${summary.wfsTotal})`, value: 'wfs' },
        { label: `自发货 (${summary.sellerTotal})`, value: 'seller' },
      ]"
    />

    <el-table :data="currentOrders" stripe size="small" v-loading="loading" class="wm-table">
      <el-table-column prop="orderNo" label="订单号" min-width="150" fixed />
      <el-table-column
        v-if="showStoreColumn"
        label="店铺"
        min-width="130"
        show-overflow-tooltip
      >
        <template #default="{ row }">{{ storeNameMap[row.storeId] || '—' }}</template>
      </el-table-column>
      <el-table-column prop="productName" label="商品" min-width="160" show-overflow-tooltip />
      <AssigneeTableColumn />
      <el-table-column prop="sku" label="SKU" width="100" />
      <el-table-column prop="quantity" label="数量" width="70" align="center" />
      <el-table-column label="金额" width="100" align="right">
        <template #default="{ row }">
          {{ formatMoneyDecimal(row.amount) }} {{ row.currency }}
        </template>
      </el-table-column>
      <el-table-column prop="orderedAt" label="下单时间" width="160" />
      <el-table-column prop="shipDeadline" label="发货截止" width="160" />
      <el-table-column label="状态" width="90" align="center" fixed="right">
        <template #default="{ row }">
          <el-tag :type="statusType(row)" size="small">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
    </el-table>

    <el-empty
      v-if="!loading && !currentOrders.length"
      :description="orderType === 'wfs' ? '今日暂无 WFS 订单' : '今日暂无自发货订单'"
      :image-size="72"
    />
  </div>
</template>

<style scoped>
.wm-panel {
  display: grid;
  gap: 16px;
}

.mini-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.mini-stat {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 10px;
  align-items: center;
  padding: 12px 14px;
  border-radius: 8px;
  background: var(--el-fill-color-lighter);
}

.mini-stat__value {
  font-size: 18px;
  font-weight: 700;
}

.mini-stat__label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.wm-table {
  border-radius: 8px;
}

@media (max-width: 768px) {
  .mini-stats {
    grid-template-columns: 1fr;
  }
}
</style>
