<script setup>
import { computed, ref, watch } from 'vue'
import { summarizeDomesticIssues } from '@/utils/domesticPlatform'
import DomesticPanelHeader from '@/components/domestic/DomesticPanelHeader.vue'
import AssigneeTableColumn from '@/components/common/AssigneeTableColumn.vue'

const props = defineProps({
  issues: { type: Array, default: () => [] },
  syncedAt: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  showStoreColumn: { type: Boolean, default: false },
  storeNameMap: { type: Object, default: () => ({}) },
  initialFilter: { type: String, default: 'all' },
  issuesTitle: { type: String, default: '运营预警' },
  issuesDescription: { type: String, default: '商品、活动与内容相关待跟进事项' },
})

const emit = defineEmits(['refresh', 'resolve'])

const filterStatus = ref(props.initialFilter)
const resolving = ref(false)

const summary = computed(() => summarizeDomesticIssues(props.issues))

const filterOptions = computed(() => [
  { label: '全部', value: 'all' },
  {
    label: summary.value.open ? `待处理 (${summary.value.open})` : '待处理',
    value: 'open',
  },
  {
    label: summary.value.high ? `高优先级 (${summary.value.high})` : '高优先级',
    value: 'high',
  },
  { label: '已解决', value: 'resolved' },
])

const filteredIssues = computed(() => {
  const map = {
    open: (item) => !item.resolved,
    high: (item) => !item.resolved && item.severity === 'high',
    resolved: (item) => item.resolved,
  }
  const fn = map[filterStatus.value]
  return fn ? props.issues.filter(fn) : props.issues
})

function severityType(severity) {
  if (severity === 'high') return 'danger'
  if (severity === 'medium') return 'warning'
  return 'info'
}

function severityLabel(severity) {
  if (severity === 'high') return '高'
  if (severity === 'medium') return '中'
  return '低'
}

function handleResolve(row) {
  resolving.value = true
  emit('resolve', { id: row.id })
}

function finishResolve() {
  resolving.value = false
}

function setFilter(value) {
  filterStatus.value = value
}

watch(
  () => props.initialFilter,
  (value) => {
    if (value) filterStatus.value = value
  },
)

defineExpose({ finishResolve, setFilter })
</script>

<template>
  <div class="domestic-panel">
    <DomesticPanelHeader
      :title="issuesTitle"
      :description="issuesDescription"
      :synced-at="syncedAt"
      action-label="刷新预警"
      :loading="loading"
      @action="$emit('refresh')"
    />

    <el-segmented v-model="filterStatus" :options="filterOptions" size="small" />

    <el-table :data="filteredIssues" size="small" stripe v-loading="loading">
      <el-table-column prop="typeLabel" label="类型" width="110" />
      <el-table-column v-if="showStoreColumn" label="店铺" width="130">
        <template #default="{ row }">{{ storeNameMap[row.storeId] || '—' }}</template>
      </el-table-column>
      <AssigneeTableColumn width="90" />
      <el-table-column prop="sku" label="SKU" width="100" />
      <el-table-column prop="productName" label="商品" min-width="130" show-overflow-tooltip />
      <el-table-column prop="detail" label="说明" min-width="180" show-overflow-tooltip />
      <el-table-column label="优先级" width="72" align="center">
        <template #default="{ row }">
          <el-tag :type="severityType(row.severity)" size="small">
            {{ severityLabel(row.severity) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="90" align="center" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="!row.resolved"
            link
            type="primary"
            size="small"
            :loading="resolving"
            @click="handleResolve(row)"
          >
            标记解决
          </el-button>
          <el-tag v-else type="success" size="small">已解决</el-tag>
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
</style>
