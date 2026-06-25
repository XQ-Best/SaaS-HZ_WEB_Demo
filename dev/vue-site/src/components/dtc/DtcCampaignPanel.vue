<script setup>
import { computed } from 'vue'
import { formatMoneyDecimal } from '@/utils/format'

const props = defineProps({
  campaigns: { type: Array, default: () => [] },
  storeNameMap: { type: Object, default: () => ({}) },
})

const statusType = {
  进行中: 'primary',
  已结束: 'info',
  已暂停: 'warning',
}

const tableData = computed(() => props.campaigns)
</script>

<template>
  <el-table :data="tableData" stripe size="small">
    <el-table-column prop="name" label="活动名称" min-width="160" />
    <el-table-column label="店铺" width="140">
      <template #default="{ row }">{{ storeNameMap[row.storeId] || '—' }}</template>
    </el-table-column>
    <el-table-column label="状态" width="90" align="center">
      <template #default="{ row }">
        <el-tag :type="statusType[row.status] || 'info'" size="small">{{ row.status }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column label="预算" width="100" align="right">
      <template #default="{ row }">{{ formatMoneyDecimal(row.budget) }}</template>
    </el-table-column>
    <el-table-column label="已花费" width="100" align="right">
      <template #default="{ row }">{{ formatMoneyDecimal(row.spent) }}</template>
    </el-table-column>
    <el-table-column prop="orders" label="订单" width="80" align="center" />
    <el-table-column label="ROAS" width="80" align="center">
      <template #default="{ row }">
        <el-text :type="row.roas >= 3 ? 'success' : row.roas >= 2 ? 'warning' : 'danger'">
          {{ row.roas }}x
        </el-text>
      </template>
    </el-table-column>
  </el-table>
</template>
