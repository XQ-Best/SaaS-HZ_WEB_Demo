<script setup>
import { computed, ref } from 'vue'
import { formatMoneyDecimal } from '@/utils/format'
import AssigneeTableColumn from '@/components/common/AssigneeTableColumn.vue'

const props = defineProps({
  products: { type: Array, required: true },
  showStoreColumn: { type: Boolean, default: false },
})

const filter = ref('all')

const filtered = computed(() => {
  if (filter.value === 'lowstock') return props.products.filter((p) => p.stock < 200)
  if (filter.value === 'slow') return props.products.filter((p) => p.daysWithoutSale >= 15)
  if (filter.value === 'hot') return props.products.filter((p) => p.dailyOrders >= 20)
  return props.products
})
</script>

<template>
  <el-card shadow="never">
    <template #header>
      <el-space>
        <span>商品管理</span>
        <el-radio-group v-model="filter" size="small">
          <el-radio-button value="all">全部</el-radio-button>
          <el-radio-button value="lowstock">低库存</el-radio-button>
          <el-radio-button value="slow">滞销</el-radio-button>
          <el-radio-button value="hot">爆款</el-radio-button>
        </el-radio-group>
      </el-space>
    </template>

    <el-table :data="filtered" stripe size="small">
      <el-table-column v-if="showStoreColumn" prop="storeName" label="店铺" width="140" />
      <AssigneeTableColumn />
      <el-table-column prop="sku" label="SKU" width="100" />
      <el-table-column prop="name" label="商品名称" min-width="160" show-overflow-tooltip />
      <el-table-column prop="category" label="品类" width="90" />
      <el-table-column label="售价" width="90" align="right">
        <template #default="{ row }">{{ formatMoneyDecimal(row.price) }}</template>
      </el-table-column>
      <el-table-column label="库存" prop="stock" width="80" align="center" />
      <el-table-column label="日订单" prop="dailyOrders" width="80" align="center" />
      <el-table-column label="日访客" prop="dailyViews" width="90" align="center" />
      <el-table-column label="转化率" width="90" align="center">
        <template #default="{ row }">{{ row.conversionRate }}%</template>
      </el-table-column>
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.stock < 200" type="danger" size="small">低库存</el-tag>
          <el-tag v-else-if="row.daysWithoutSale >= 15" type="warning" size="small">滞销</el-tag>
          <el-tag v-else-if="row.dailyOrders >= 20" type="success" size="small">爆款</el-tag>
          <el-tag v-else type="info" size="small" effect="plain">正常</el-tag>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>
