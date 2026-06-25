<script setup>
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { summarizeWalmartListings } from '@/utils/walmart'
import WalmartPanelHeader from '@/components/walmart/WalmartPanelHeader.vue'
import AssigneeTableColumn from '@/components/common/AssigneeTableColumn.vue'

const props = defineProps({
  issues: { type: Array, default: () => [] },
  syncedAt: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  showStoreColumn: { type: Boolean, default: false },
  storeNameMap: { type: Object, default: () => ({}) },
  initialFilter: { type: String, default: 'all' },
})

const emit = defineEmits(['refresh', 'resolve'])

const filterStatus = ref(props.initialFilter)
const resolving = ref(false)

const summary = computed(() => summarizeWalmartListings(props.issues))

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
  <div class="wm-panel">
    <WalmartPanelHeader
      title="Listing 问题"
      description="未发布、内容错误、价格异常与库存不一致等问题"
      :synced-at="syncedAt"
      action-label="抓取 Listing 问题"
      :loading="loading"
      @action="$emit('refresh')"
    />

    <div class="mini-stats">
      <div class="mini-stat">
        <span class="mini-stat__value">{{ summary.total }}</span>
        <span class="mini-stat__label">问题记录</span>
      </div>
      <div class="mini-stat is-danger">
        <span class="mini-stat__value">{{ summary.open }}</span>
        <span class="mini-stat__label">待处理</span>
      </div>
      <div class="mini-stat">
        <span class="mini-stat__value">{{ summary.high }}</span>
        <span class="mini-stat__label">高优先级</span>
      </div>
      <div class="mini-stat">
        <span class="mini-stat__value">{{ summary.resolved }}</span>
        <span class="mini-stat__label">已解决</span>
      </div>
    </div>

    <el-segmented v-model="filterStatus" :options="filterOptions" />

    <el-table :data="filteredIssues" stripe size="small" v-loading="loading" class="wm-table">
      <el-table-column prop="typeLabel" label="问题类型" width="110" fixed />
      <el-table-column
        v-if="showStoreColumn"
        label="店铺"
        min-width="130"
        show-overflow-tooltip
      >
        <template #default="{ row }">{{ storeNameMap[row.storeId] || '—' }}</template>
      </el-table-column>
      <el-table-column prop="sku" label="SKU" width="100" />
      <el-table-column prop="productName" label="商品" min-width="150" show-overflow-tooltip />
      <AssigneeTableColumn />
      <el-table-column prop="detail" label="问题说明" min-width="220" show-overflow-tooltip />
      <el-table-column label="优先级" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="severityType(row.severity)" size="small">
            {{ severityLabel(row.severity) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="reportedAt" label="发现时间" width="160" />
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="row.resolved ? 'success' : 'warning'" size="small">
            {{ row.resolved ? '已解决' : '待处理' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="90" align="center" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="!row.resolved"
            type="primary"
            link
            size="small"
            :loading="resolving"
            @click="handleResolve(row)"
          >
            标记解决
          </el-button>
          <el-text v-else size="small" type="info">已处理</el-text>
        </template>
      </el-table-column>
    </el-table>

    <el-empty
      v-if="!loading && !filteredIssues.length"
      description="暂无 Listing 问题"
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
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.mini-stat {
  display: grid;
  gap: 4px;
  padding: 12px 14px;
  border-radius: 8px;
  background: var(--el-fill-color-lighter);
}

.mini-stat.is-danger .mini-stat__value {
  color: var(--el-color-danger);
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
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
