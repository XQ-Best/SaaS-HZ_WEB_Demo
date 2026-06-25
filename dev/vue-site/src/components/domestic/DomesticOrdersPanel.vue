<script setup>
import { computed } from 'vue'
import { DOMESTIC_ORDER_STATUS_TYPE } from '@/constants/domesticShared'
import { summarizeDomesticOrders } from '@/utils/domesticPlatform'
import { formatMoneyDecimal } from '@/utils/format'
import DomesticPanelHeader from '@/components/domestic/DomesticPanelHeader.vue'
import AssigneeTableColumn from '@/components/common/AssigneeTableColumn.vue'

const props = defineProps({
  orders: { type: Array, default: () => [] },
  syncedAt: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  showStoreColumn: { type: Boolean, default: false },
  storeNameMap: { type: Object, default: () => ({}) },
  showChannelColumn: { type: Boolean, default: false },
  ordersDescription: { type: String, default: '今日待处理与已发货订单' },
})

defineEmits(['refresh'])

const summary = computed(() => summarizeDomesticOrders(props.orders))

function statusType(order) {
  return DOMESTIC_ORDER_STATUS_TYPE[order.status] || 'info'
}
</script>

<template>
  <div class="domestic-panel">
    <DomesticPanelHeader
      title="今日订单"
      :description="ordersDescription"
      :synced-at="syncedAt"
      action-label="抓取今日订单"
      :loading="loading"
      @action="$emit('refresh')"
    />

    <div class="mini-stats">
      <div class="mini-stat">
        <span class="mini-stat__value">{{ summary.total }}</span>
        <span class="mini-stat__label">全部订单</span>
      </div>
      <div class="mini-stat">
        <span class="mini-stat__value">{{ summary.pending }}</span>
        <span class="mini-stat__label">待处理</span>
        <el-tag v-if="summary.pending" type="warning" size="small" effect="plain">
          需跟进
        </el-tag>
      </div>
      <div class="mini-stat">
        <span class="mini-stat__value">{{ summary.totalAmountText }}</span>
        <span class="mini-stat__label">当日金额</span>
      </div>
    </div>

    <el-table :data="orders" size="small" stripe v-loading="loading">
      <el-table-column prop="orderNo" label="订单号" min-width="150" />
      <el-table-column v-if="showStoreColumn" label="店铺" width="130">
        <template #default="{ row }">{{ storeNameMap[row.storeId] || '—' }}</template>
      </el-table-column>
      <AssigneeTableColumn width="90" />
      <el-table-column prop="productName" label="商品" min-width="150" show-overflow-tooltip />
      <el-table-column v-if="showChannelColumn" prop="channel" label="来源" width="80" />
      <el-table-column label="金额" width="100" align="right">
        <template #default="{ row }">{{ formatMoneyDecimal(row.amount) }}</template>
      </el-table-column>
      <el-table-column prop="shipDeadline" label="发货截止" width="150" />
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="statusType(row)" size="small">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.domestic-panel {
  display: grid;
  gap: 16px;
}

.mini-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.mini-stat {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  padding: 12px 16px;
  background: var(--ch-bg-soft, var(--el-fill-color-light));
  border-radius: var(--ch-radius-md, 8px);
}

.mini-stat__value {
  font-size: 20px;
  font-weight: 600;
  color: var(--ch-text, var(--el-text-color-primary));
}

.mini-stat__label {
  font-size: 12px;
  color: var(--ch-text-muted, var(--el-text-color-secondary));
}
</style>
