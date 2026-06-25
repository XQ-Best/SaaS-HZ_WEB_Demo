<script setup>
import { computed, ref } from 'vue'
import { TASK_STATUS_META } from '@/constants/operations'
import { calcTaskStats, groupTasksByAssignee } from '@/utils/operations'

const props = defineProps({
  tasks: { type: Array, default: () => [] },
})

const showAll = ref(false)

const stats = computed(() => calcTaskStats(props.tasks))

const assigneeStats = computed(() =>
  groupTasksByAssignee(props.tasks).sort((a, b) => b.inProgress - a.inProgress),
)

const activeTasks = computed(() =>
  props.tasks.filter((t) => t.status !== '已完成'),
)

const displayTasks = computed(() =>
  showAll.value ? props.tasks : activeTasks.value.slice(0, 6),
)

const priorityType = {
  high: 'danger',
  medium: 'warning',
  low: 'info',
}
</script>

<template>
  <el-card shadow="never">
    <template #header>
      <div class="panel-header">
        <span>任务跟进</span>
        <el-space wrap>
          <el-tag type="success" effect="plain">完成率 {{ stats.completionRate }}%</el-tag>
          <el-tag v-if="stats.overdue" type="danger" effect="plain">{{ stats.overdue }} 项逾期</el-tag>
        </el-space>
      </div>
    </template>

    <div class="task-stats">
      <div class="task-stat">
        <span class="task-stat__value">{{ stats.total }}</span>
        <span class="task-stat__label">全部</span>
      </div>
      <div class="task-stat">
        <span class="task-stat__value is-primary">{{ stats.inProgress }}</span>
        <span class="task-stat__label">进行中</span>
      </div>
      <div class="task-stat">
        <span class="task-stat__value is-info">{{ stats.pending }}</span>
        <span class="task-stat__label">待处理</span>
      </div>
      <div class="task-stat">
        <span class="task-stat__value is-success">{{ stats.completed }}</span>
        <span class="task-stat__label">已完成</span>
      </div>
    </div>

    <el-table :data="assigneeStats" size="small" class="assignee-table">
      <el-table-column prop="assignee" label="员工" width="90" />
      <el-table-column label="完成率" min-width="140">
        <template #default="{ row }">
          <el-progress :percentage="row.rate" :stroke-width="8" />
        </template>
      </el-table-column>
      <el-table-column prop="inProgress" label="进行中" width="80" align="center" />
      <el-table-column prop="overdue" label="逾期" width="70" align="center">
        <template #default="{ row }">
          <el-text :type="row.overdue ? 'danger' : 'info'">{{ row.overdue }}</el-text>
        </template>
      </el-table-column>
    </el-table>

    <el-divider content-position="left">
      {{ showAll ? '全部任务' : '待办任务' }}
    </el-divider>

    <el-empty v-if="!displayTasks.length" description="暂无待办任务" :image-size="56" />

    <el-table v-else :data="displayTasks" size="small" stripe>
      <el-table-column prop="title" label="任务" min-width="220" show-overflow-tooltip />
      <el-table-column prop="platform" label="平台" width="100" />
      <el-table-column prop="assignee" label="负责人" width="90" />
      <el-table-column label="优先级" width="80">
        <template #default="{ row }">
          <el-tag :type="priorityType[row.priority]" size="small">
            {{ row.priority === 'high' ? '高' : row.priority === 'medium' ? '中' : '低' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="TASK_STATUS_META[row.status]?.type" size="small">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="due" label="截止" width="110" />
    </el-table>

    <div v-if="activeTasks.length > 6" class="task-footer">
      <el-button link type="primary" @click="showAll = !showAll">
        {{ showAll ? '收起' : `查看全部 ${activeTasks.length} 项待办` }}
      </el-button>
    </div>
  </el-card>
</template>

<style scoped>
.assignee-table {
  margin-bottom: 4px;
}

.task-footer {
  margin-top: 12px;
  text-align: center;
}
</style>
