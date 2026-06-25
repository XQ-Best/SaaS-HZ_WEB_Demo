<script setup>
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { loadOperationsOverview } from '@/api/operationsOverview'
import OperationsIssuesPanel from '@/components/dashboard/OperationsIssuesPanel.vue'

const auth = useAuthStore()
const loading = ref(false)
const overview = ref(null)

async function refresh() {
  loading.value = true
  try {
    const res = await loadOperationsOverview(auth)
    overview.value = {
      platforms: res.data.platforms,
      totalIssues: res.data.totalIssues,
      syncedAt: res.data.syncedAt,
    }
  } catch {
    overview.value = null
  } finally {
    loading.value = false
  }
}

onMounted(refresh)
</script>

<template>
  <OperationsIssuesPanel v-loading="loading" :overview="overview" />
</template>
