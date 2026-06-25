<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, Right } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { loadOperationsOverview } from '@/api/operationsOverview'
import { submitTaskFeedback } from '@/api/opsFeedback'
import { updateAssignedTaskStatus } from '@/api/assignedTasks'
import { calcTaskStats } from '@/utils/operations'
import { groupEmployeeTasksByPlatform } from '@/utils/employeeTasks'
import { TASK_STATUS_META } from '@/constants/operations'
import { OUTCOME_OPTIONS } from '@/constants/opsFeedbackDemo'
import PageHeader from '@/components/common/PageHeader.vue'
import PageScroll from '@/components/common/PageScroll.vue'

const auth = useAuthStore()
const router = useRouter()
const loading = ref(false)
const tasks = ref([])
const activeFilter = ref('all')
const feedbackVisible = ref(false)
const feedbackSubmitting = ref(false)
const activeTask = ref(null)
const feedbackForm = reactive({
  outcome: 'resolved',
  feedback: '',
})

const priorityMap = {
  high: { label: '高', type: 'danger' },
  medium: { label: '中', type: 'warning' },
  low: { label: '低', type: 'info' },
}

const sourceMap = {
  issue: { label: '运营预警', type: 'danger' },
  plan: { label: '计划任务', type: 'info' },
  assigned: { label: '管理员分配', type: 'primary' },
}

const stats = computed(() => calcTaskStats(tasks.value))
const issueCount = computed(() => tasks.value.filter((t) => t.source === 'issue' && t.status !== '已完成').length)

const platformGroups = computed(() => groupEmployeeTasksByPlatform(tasks.value))

const filterOptions = computed(() => {
  const options = [{ value: 'all', label: '全部', count: tasks.value.filter((t) => t.status !== '已完成').length }]
  for (const group of platformGroups.value) {
    options.push({
      value: group.platformKey,
      label: group.platform,
      count: group.pending,
    })
  }
  return options
})

const visibleGroups = computed(() => {
  if (activeFilter.value === 'all') return platformGroups.value
  return platformGroups.value.filter((g) => g.platformKey === activeFilter.value)
})

const platformLabels = computed(() => {
  const map = {
    temu: 'Temu',
    aliexpress: 'AliExpress',
    amazon: 'Amazon',
    walmart: 'Walmart',
    pdd: '拼多多',
    douyin: '抖音',
    channels: '视频号',
    '1688': '1688',
    shopify: '独立站',
    wordpress: '独立站',
  }
  const labels = (auth.employee.platforms || []).map((p) => map[p] || p)
  return [...new Set(labels)].join(' · ') || '—'
})

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

function openFeedback(task) {
  activeTask.value = task
  feedbackForm.outcome = 'resolved'
  feedbackForm.feedback = ''
  feedbackVisible.value = true
}

async function submitFeedback() {
  if (!activeTask.value) return
  if (!feedbackForm.feedback.trim()) {
    ElMessage.warning('请填写处理说明，便于管理员了解进展')
    return
  }

  feedbackSubmitting.value = true
  try {
    submitTaskFeedback({
      taskId: String(activeTask.value.id),
      employeeId: auth.employee.id,
      employeeName: auth.employee.name,
      employeeRole: auth.employee.role,
      platform: activeTask.value.platform,
      platformKey: activeTask.value.platformKey,
      taskTitle: activeTask.value.title,
      category: activeTask.value.category,
      storeName: activeTask.value.storeName,
      outcome: feedbackForm.outcome,
      feedback: feedbackForm.feedback,
    })

    if (feedbackForm.outcome === 'resolved') {
      activeTask.value.status = '已完成'
      activeTask.value.progress = 100
    } else if (feedbackForm.outcome === 'in_progress') {
      activeTask.value.status = '进行中'
      activeTask.value.progress = Math.max(activeTask.value.progress || 0, 50)
    } else {
      activeTask.value.status = '进行中'
    }

    if (activeTask.value.source === 'assigned') {
      updateAssignedTaskStatus(activeTask.value.id, activeTask.value.status, {
        progress: activeTask.value.progress,
      })
    }

    ElMessage.success('反馈已提交，管理员可在运营总览查看')
    feedbackVisible.value = false
  } catch (err) {
    ElMessage.error(err.message || '提交失败')
  } finally {
    feedbackSubmitting.value = false
  }
}

function goPlatform(route) {
  if (route) router.push(route)
}

onMounted(loadTasks)
</script>

<template>
  <PageScroll>
    <template #header>
      <PageHeader
        title="任务中心"
        :description="`${auth.employee.name} · ${auth.employee.role} · 负责 ${platformLabels}`"
      >
        <template #actions>
          <el-button :icon="Refresh" :loading="loading" @click="loadTasks">刷新</el-button>
        </template>
      </PageHeader>
    </template>

    <div v-loading="loading" class="task-center">
      <div class="metrics-bar metrics-bar--4">
        <div class="metric-item">
          <div class="metric-value" :class="issueCount ? 'is-danger' : ''">{{ issueCount }}</div>
          <div class="metric-label">运营预警</div>
          <div class="metric-hint">来自各平台实时问题</div>
        </div>
        <div class="metric-item">
          <div class="metric-value" :class="stats.pending + stats.inProgress ? 'is-warning' : ''">
            {{ stats.pending + stats.inProgress }}
          </div>
          <div class="metric-label">待完成</div>
          <div class="metric-hint">含计划与预警任务</div>
        </div>
        <div class="metric-item">
          <div class="metric-value" :class="stats.overdue ? 'is-danger' : ''">{{ stats.overdue }}</div>
          <div class="metric-label">已逾期</div>
          <div class="metric-hint">需立即处理</div>
        </div>
        <div class="metric-item">
          <div class="metric-value is-success">{{ stats.completionRate }}<small>%</small></div>
          <div class="metric-label">完成率</div>
          <div class="metric-hint">{{ stats.completed }}/{{ stats.total }} 已完成</div>
        </div>
      </div>

      <div class="filter-bar">
        <button
          v-for="item in filterOptions"
          :key="item.value"
          type="button"
          class="filter-chip"
          :class="{ 'is-active': activeFilter === item.value }"
          @click="activeFilter = item.value"
        >
          {{ item.label }}
          <span v-if="item.count" class="filter-chip__count">{{ item.count }}</span>
        </button>
      </div>

      <el-empty
        v-if="!loading && !visibleGroups.length"
        description="暂无与你相关的任务"
        :image-size="88"
      />

      <div v-else class="platform-groups">
        <section v-for="group in visibleGroups" :key="group.platformKey" class="platform-group">
          <header class="platform-group__head">
            <div class="platform-group__title">
              <strong>{{ group.platform }}</strong>
              <el-tag v-if="group.high" type="danger" size="small" effect="plain">
                {{ group.high }} 项高优
              </el-tag>
              <el-tag v-if="group.pending" type="warning" size="small" effect="plain">
                {{ group.pending }} 待完成
              </el-tag>
            </div>
            <el-button
              v-if="group.route"
              link
              type="primary"
              :icon="Right"
              @click="goPlatform(group.route)"
            >
              进入运营
            </el-button>
          </header>

          <el-table :data="group.tasks" size="small" stripe class="task-table">
            <el-table-column label="任务" min-width="240">
              <template #default="{ row }">
                <div class="task-title">{{ row.title }}</div>
                <div v-if="row.detail" class="task-detail">{{ row.detail }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="storeName" label="店铺" width="130" show-overflow-tooltip />
            <el-table-column prop="category" label="类型" width="80" />
            <el-table-column label="来源" width="90">
              <template #default="{ row }">
                <el-tag :type="sourceMap[row.source]?.type || 'info'" size="small" effect="plain">
                  {{ sourceMap[row.source]?.label || '任务' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="优先级" width="72" align="center">
              <template #default="{ row }">
                <el-tag :type="priorityMap[row.priority]?.type || 'info'" size="small">
                  {{ priorityMap[row.priority]?.label || '中' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="due" label="截止" width="110" />
            <el-table-column label="状态" width="88" align="center">
              <template #default="{ row }">
                <el-tag :type="TASK_STATUS_META[row.status]?.type" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="center" fixed="right">
              <template #default="{ row }">
                <el-button
                  v-if="row.status !== '已完成'"
                  link
                  type="primary"
                  size="small"
                  @click="openFeedback(row)"
                >
                  提交反馈
                </el-button>
                <el-text v-else type="success" size="small">已完成</el-text>
              </template>
            </el-table-column>
          </el-table>
        </section>
      </div>
    </div>

    <el-dialog
      v-model="feedbackVisible"
      title="提交处理反馈"
      width="480px"
      destroy-on-close
      @closed="activeTask = null"
    >
      <template v-if="activeTask">
        <div class="feedback-task-summary">
          <el-tag size="small" effect="plain">{{ activeTask.platform }}</el-tag>
          <strong>{{ activeTask.title }}</strong>
          <p v-if="activeTask.detail">{{ activeTask.detail }}</p>
        </div>

        <el-form label-width="80px" class="feedback-form">
          <el-form-item label="处理结果" required>
            <el-radio-group v-model="feedbackForm.outcome">
              <el-radio v-for="item in OUTCOME_OPTIONS" :key="item.value" :value="item.value">
                {{ item.label }}
              </el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="处理说明" required>
            <el-input
              v-model="feedbackForm.feedback"
              type="textarea"
              :rows="4"
              placeholder="说明处理措施、进展或需要协助的原因，管理员将在运营总览查看"
            />
          </el-form-item>
        </el-form>
      </template>

      <template #footer>
        <el-button @click="feedbackVisible = false">取消</el-button>
        <el-button type="primary" :loading="feedbackSubmitting" @click="submitFeedback">
          提交反馈
        </el-button>
      </template>
    </el-dialog>
  </PageScroll>
</template>

<style scoped>
.task-center {
  display: grid;
  gap: 16px;
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid var(--ch-border);
  border-radius: var(--ch-radius-sm);
  background: var(--ch-surface);
  color: var(--ch-text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
}

.filter-chip:hover {
  border-color: var(--ch-primary-muted);
  color: var(--ch-primary);
}

.filter-chip.is-active {
  border-color: var(--ch-primary);
  background: var(--ch-primary-soft);
  color: var(--ch-primary);
  font-weight: 600;
}

.filter-chip__count {
  min-width: 18px;
  padding: 0 5px;
  border-radius: 10px;
  background: var(--ch-surface-muted);
  font-size: 12px;
  line-height: 18px;
  text-align: center;
}

.filter-chip.is-active .filter-chip__count {
  background: var(--ch-primary-muted);
  color: #fff;
}

.platform-groups {
  display: grid;
  gap: 16px;
}

.platform-group {
  border: 1px solid var(--ch-border);
  border-radius: var(--ch-radius-lg);
  background: var(--ch-surface);
  overflow: hidden;
}

.platform-group__head {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--ch-border);
  background: var(--ch-surface-muted);
}

.platform-group__title {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.platform-group__title strong {
  font-size: 15px;
  color: var(--ch-text);
}

.task-table {
  border-radius: 0;
}

.task-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--ch-text);
  line-height: 1.45;
}

.task-detail {
  margin-top: 4px;
  font-size: 12px;
  color: var(--ch-text-muted);
  line-height: 1.4;
}

.feedback-task-summary {
  display: grid;
  gap: 8px;
  margin-bottom: 16px;
  padding: 12px 14px;
  border-radius: var(--ch-radius-md);
  background: var(--ch-surface-muted);
}

.feedback-task-summary p {
  margin: 0;
  font-size: 12px;
  color: var(--ch-text-muted);
  line-height: 1.5;
}

.feedback-form {
  margin-top: 4px;
}
</style>
