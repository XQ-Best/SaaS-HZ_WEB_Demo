<script setup>
import { computed } from 'vue'
import { formatMoneyDecimal } from '@/utils/format'

const props = defineProps({
  trafficSources: { type: Array, default: () => [] },
})

const totalVisits = computed(() =>
  props.trafficSources.reduce((sum, row) => sum + row.visits, 0),
)
const totalOrders = computed(() =>
  props.trafficSources.reduce((sum, row) => sum + row.orders, 0),
)
const totalSpend = computed(() =>
  props.trafficSources.reduce((sum, row) => sum + row.spend, 0),
)

const tableData = computed(() =>
  props.trafficSources.map((row) => ({
    ...row,
    visitShare: totalVisits.value ? ((row.visits / totalVisits.value) * 100).toFixed(1) : '0',
    cpa: row.orders ? formatMoneyDecimal(row.spend / row.orders) : '—',
  })),
)
</script>

<template>
  <div>
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :xs="12" :sm="8">
        <el-statistic title="总访客" :value="totalVisits" />
      </el-col>
      <el-col :xs="12" :sm="8">
        <el-statistic title="总订单" :value="totalOrders" />
      </el-col>
      <el-col :xs="12" :sm="8">
        <el-statistic title="广告花费" :value="totalSpend" prefix="$" />
      </el-col>
    </el-row>

    <el-table :data="tableData" stripe size="small">
      <el-table-column prop="source" label="流量来源" min-width="140" />
      <el-table-column prop="visits" label="访客" width="90" align="center" />
      <el-table-column label="占比" width="80" align="center">
        <template #default="{ row }">{{ row.visitShare }}%</template>
      </el-table-column>
      <el-table-column prop="orders" label="订单" width="80" align="center" />
      <el-table-column label="转化率" width="90" align="center">
        <template #default="{ row }">{{ row.conversion }}%</template>
      </el-table-column>
      <el-table-column label="花费" width="100" align="right">
        <template #default="{ row }">
          {{ row.spend ? formatMoneyDecimal(row.spend) : '—' }}
        </template>
      </el-table-column>
      <el-table-column label="获客成本" width="100" align="right" prop="cpa" />
    </el-table>
  </div>
</template>
