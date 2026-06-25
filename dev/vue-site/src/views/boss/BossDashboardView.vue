<script setup>
import { computed, onMounted, ref } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { loadOperationsOverview } from '@/api/operationsOverview'
import OperationsSummaryHeader from '@/components/dashboard/OperationsSummaryHeader.vue'
import OperationsIssuesPanel from '@/components/dashboard/OperationsIssuesPanel.vue'
import OperationsTasksPanel from '@/components/dashboard/OperationsTasksPanel.vue'
import DailyOpsReportPanel from '@/components/dashboard/DailyOpsReportPanel.vue'
import PageScroll from '@/components/common/PageScroll.vue'

const auth = useAuthStore()
const loading = ref(false)
const context = ref(null)

const overview = computed(() => {
  if (!context.value) return null
  return {
    platforms: context.value.platforms,
    totalIssues: context.value.totalIssues,
    syncedAt: context.value.syncedAt,
  }
})

const platformSales = computed(() => context.value?.platformSales || [])
const tasks = computed(() => context.value?.tasks || [])
const dailyReport = computed(() => context.value?.dailyReport || null)

async function refresh() {
  loading.value = true
  try {
    const res = await loadOperationsOverview(auth)
    context.value = res.data
  } catch {
    context.value = null
  } finally {
    loading.value = false
  }
}

onMounted(refresh)
</script>

<template>
  <PageScroll>
    <div v-loading="loading" class="ops-dashboard">
      <div class="ops-toolbar">
        <el-text size="small" type="info">
          数据来自账户绑定店铺与员工分配，按负责人汇总
        </el-text>
        <el-button :icon="Refresh" size="small" :loading="loading" @click="refresh">
          刷新
        </el-button>
      </div>

      <OperationsSummaryHeader
        :overview="overview"
        :platform-sales="platformSales"
        :tasks="tasks"
      />

      <DailyOpsReportPanel :report="dailyReport" :loading="loading" />

      <OperationsIssuesPanel :overview="overview" />

      <OperationsTasksPanel :tasks="tasks" />
    </div>
  </PageScroll>
</template>

<style scoped>
.ops-dashboard {
  display: grid;
  gap: 16px;
}

.ops-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
}
</style>
