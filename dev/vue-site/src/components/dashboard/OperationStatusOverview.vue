<script setup>
import { computed } from 'vue'
import { PLATFORM_OPS_STATUS } from '@/constants/operations'

const alertType = {
  normal: 'success',
  warning: 'warning',
  danger: 'danger',
}

const overallHealth = computed(() =>
  Math.round(PLATFORM_OPS_STATUS.reduce((s, p) => s + p.health, 0) / PLATFORM_OPS_STATUS.length),
)

const riskPlatforms = computed(() => PLATFORM_OPS_STATUS.filter((p) => p.alertLevel !== 'normal'))
const activeTasksTotal = computed(() => PLATFORM_OPS_STATUS.reduce((s, p) => s + p.activeTasks, 0))
const overdueTotal = computed(() => PLATFORM_OPS_STATUS.reduce((s, p) => s + p.overdueTasks, 0))
const todayDoneTotal = computed(() => PLATFORM_OPS_STATUS.reduce((s, p) => s + p.todayDone, 0))
</script>

<template>
  <el-card shadow="never">
    <template #header>
      <el-space>
        <span>运营整体状态</span>
        <el-tag :type="overallHealth >= 85 ? 'success' : overallHealth >= 75 ? 'warning' : 'danger'" effect="plain">
          综合健康 {{ overallHealth }}
        </el-tag>
      </el-space>
    </template>

    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :xs="12" :sm="6">
        <el-statistic title="进行中任务" :value="activeTasksTotal" />
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-statistic title="今日已完成" :value="todayDoneTotal" />
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-statistic title="逾期任务" :value="overdueTotal">
          <template v-if="overdueTotal" #suffix>
            <el-tag type="danger" size="small">需关注</el-tag>
          </template>
        </el-statistic>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-statistic title="风险平台" :value="riskPlatforms.length" />
      </el-col>
    </el-row>

    <el-table :data="PLATFORM_OPS_STATUS" size="small" stripe>
      <el-table-column prop="platform" label="平台" width="110" />
      <el-table-column prop="owner" label="负责人" width="90" />
      <el-table-column label="健康度" width="150">
        <template #default="{ row }">
          <el-progress
            :percentage="row.health"
            :stroke-width="8"
            :status="row.health < 75 ? 'exception' : row.health < 85 ? 'warning' : 'success'"
          />
        </template>
      </el-table-column>
      <el-table-column prop="activeTasks" label="进行中" width="80" align="center" />
      <el-table-column prop="todayDone" label="今日完成" width="90" align="center" />
      <el-table-column prop="overdueTasks" label="逾期" width="70" align="center">
        <template #default="{ row }">
          <el-text :type="row.overdueTasks ? 'danger' : 'info'">{{ row.overdueTasks }}</el-text>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="alertType[row.alertLevel]" size="small">
            {{ row.alertLevel === 'normal' ? '正常' : row.alertLevel === 'warning' ? '关注' : '风险' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="summary" label="运营摘要" min-width="180" show-overflow-tooltip />
    </el-table>
  </el-card>
</template>
