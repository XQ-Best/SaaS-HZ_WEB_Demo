<script setup>
import { formatMoney } from '@/utils/format'

defineProps({
  metrics: { type: Array, required: true },
})
</script>

<template>
  <el-row :gutter="16">
    <el-col v-for="item in metrics" :key="item.label" :xs="24" :sm="12" :lg="6">
      <el-card shadow="never" class="metric-card">
        <el-statistic :title="item.label" :value="item.isMoney ? 0 : item.value">
          <template #default>
            <span class="metric-value">
              {{ item.isMoney ? formatMoney(item.value) : item.value.toLocaleString() }}
            </span>
          </template>
        </el-statistic>
        <el-text class="metric-hint" size="small" type="info">{{ item.hint }}</el-text>
      </el-card>
    </el-col>
  </el-row>
</template>

<style scoped>
.metric-card :deep(.el-statistic__head) {
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-secondary);
}

.metric-card :deep(.el-statistic__content) {
  font-size: 28px;
  font-weight: 700;
}

.metric-hint {
  display: block;
  margin-top: 10px;
}
</style>
