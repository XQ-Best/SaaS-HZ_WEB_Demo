<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { loadOperationsOverview } from '@/api/operationsOverview'
import { calcTaskStats } from '@/utils/operations'
import MetricCards from '@/components/dashboard/MetricCards.vue'
import PlatformIssuesOverview from '@/components/dashboard/PlatformIssuesOverview.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import PageScroll from '@/components/common/PageScroll.vue'

const auth = useAuthStore()
const loading = ref(false)
const context = ref(null)

const platformSales = computed(() => context.value?.platformSales || [])
const tasks = computed(() => context.value?.tasks || [])
const assignedStores = computed(() => {
  const stores = context.value?.stores
  if (!stores) return []
  return [
    ...(stores.temu || []),
    ...(stores.aliexpress || []),
    ...(stores.walmart || []),
    ...(stores.pdd || []),
    ...(stores.douyin || []),
    ...(stores.channels || []),
    ...(stores['1688'] || []),
    ...(stores.dtc || []),
  ]
})

const platformLabels = computed(() => {
  const labels = (auth.employee.platforms || []).map((p) => {
    if (p === 'temu') return 'Temu'
    if (p === 'aliexpress') return 'AliExpress'
    if (p === 'walmart') return 'Walmart'
    if (p === 'pdd') return '拼多多'
    if (p === 'douyin') return '抖音'
    if (p === 'channels') return '视频号'
    if (p === '1688') return '1688'
    if (p === 'shopify' || p === 'wordpress') return '独立站'
    return p
  })
  return [...new Set(labels)].join('、') || '未分配平台'
})

const metrics = computed(() => {
  const list = platformSales.value
  const revenue = list.reduce((s, p) => s + (p.revenue || 0), 0)
  const orders = list.reduce((s, p) => s + (p.orders || 0), 0)
  const alerts = list.reduce((s, p) => s + (p.alerts || 0), 0)
  const stats = calcTaskStats(tasks.value)

  return [
    { label: '我的销售额', value: revenue, isMoney: true, hint: platformLabels.value },
    { label: '我的订单', value: orders, hint: '负责店铺汇总' },
    { label: '待处理预警', value: alerts, hint: '需今日跟进' },
    { label: '任务完成率', value: stats.completionRate, hint: `${stats.completed}/${stats.total} 已完成` },
  ]
})

async function loadContext() {
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

onMounted(loadContext)
</script>

<template>
  <PageScroll>
    <PageHeader
      :title="`${auth.employee.name} 的工作台`"
      :description="`仅展示你负责的 ${platformLabels} 数据（${assignedStores.length} 家店铺）`"
    />

    <MetricCards v-loading="loading" :metrics="metrics" />

    <div style="margin-top: 16px">
      <PlatformIssuesOverview />
    </div>

    <el-row v-loading="loading" :gutter="16" style="margin-top: 16px">
      <el-col :span="24">
        <el-card shadow="never">
          <template #header>我的平台指标</template>
          <el-empty
            v-if="!loading && !platformSales.length"
            description="暂无负责店铺数据，请联系企业管理员在运营绑定中分配店铺"
          />
          <el-table v-else :data="platformSales" size="small">
            <el-table-column prop="name" label="平台" />
            <el-table-column label="销售额">
              <template #default="{ row }">{{ row.revenueText }}</template>
            </el-table-column>
            <el-table-column prop="orders" label="订单/销量" />
            <el-table-column prop="storeCount" label="店铺" width="80" align="center" />
            <el-table-column label="待跟进" width="90" align="center">
              <template #default="{ row }">
                <el-text :type="row.alerts ? 'danger' : 'success'">{{ row.alerts }}</el-text>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </PageScroll>
</template>
