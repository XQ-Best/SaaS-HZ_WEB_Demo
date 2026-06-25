<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { loadOperationsOverview } from '@/api/operationsOverview'
import { TASK_STATUS_META } from '@/constants/operations'
import PageHeader from '@/components/common/PageHeader.vue'
import PageScroll from '@/components/common/PageScroll.vue'

const auth = useAuthStore()
const loading = ref(false)
const tasks = ref([])

const priorityMap = {
  high: { label: '高', type: 'danger' },
  medium: { label: '中', type: 'warning' },
  low: { label: '低', type: 'info' },
}

const pendingCount = computed(() => tasks.value.filter((t) => t.status !== '已完成').length)

async function loadTasks() {
  loading.value = true
  try {
    const res = await loadOperationsOverview(auth)
    tasks.value = (res.data?.tasks || []).map((t) => ({ ...t }))
  } catch {
    tasks.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadTasks)
</script>

<template>
  <PageScroll>
    <PageHeader title="任务中心" :description="`${auth.employee.name} · 个人运营任务与跟进项`">
      <template #actions>
        <el-tag v-if="pendingCount" type="warning" effect="plain">{{ pendingCount }} 项待完成</el-tag>
      </template>
    </PageHeader>

    <el-card v-loading="loading" shadow="never">
      <el-empty v-if="!loading && !tasks.length" description="暂无与你相关的任务" />
      <el-table v-else :data="tasks">
        <el-table-column prop="title" label="任务" min-width="240" show-overflow-tooltip />
        <el-table-column prop="platform" label="平台" width="110" />
        <el-table-column label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="priorityMap[row.priority]?.type || 'info'" size="small">
              {{ priorityMap[row.priority]?.label || '中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="due" label="截止时间" width="140" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="TASK_STATUS_META[row.status]?.type" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button
              v-if="row.status !== '已完成'"
              link
              type="primary"
              @click="row.status = '已完成'; row.progress = 100"
            >
              标记完成
            </el-button>
            <el-text v-else type="success" size="small">已完成</el-text>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </PageScroll>
</template>
