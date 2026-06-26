<script setup>
import { computed, ref, watch } from 'vue'
import { loadTaskFeedbacks } from '@/api/opsFeedback'
import { TASK_STATUS_META } from '@/constants/operations'
import TaskFeedbackTimeline from './TaskFeedbackTimeline.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  task: { type: Object, default: null },
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const feedbacks = ref([])
const loading = ref(false)

const sourceMap = {
  issue: { label: '运营预警', type: 'danger' },
  plan: { label: '计划任务', type: 'info' },
}

async function loadFeedbacks(taskId) {
  if (!taskId) {
    feedbacks.value = []
    return
  }
  loading.value = true
  try {
    const res = loadTaskFeedbacks(String(taskId))
    feedbacks.value = res.data || []
  } catch {
    feedbacks.value = []
  } finally {
    loading.value = false
  }
}

watch(
  () => [visible.value, props.task?.id],
  ([open, taskId]) => {
    if (open && taskId) loadFeedbacks(taskId)
    else if (!open) feedbacks.value = []
  },
)
</script>

<template>
  <el-drawer
    v-model="visible"
    :title="task ? `任务详情 · ${task.title}` : '任务详情'"
    size="520px"
  >
    <template v-if="task">
      <div class="detail-head">
        <el-tag :type="TASK_STATUS_META[task.status]?.type || 'info'" effect="light">
          {{ task.status }}
        </el-tag>
        <el-tag size="small" effect="plain">{{ task.platform }}</el-tag>
        <el-tag
          :type="sourceMap[task.source]?.type || 'info'"
          size="small"
          effect="plain"
        >
          {{ sourceMap[task.source]?.label || '任务' }}
        </el-tag>
      </div>

      <el-descriptions :column="1" border class="detail-block">
        <el-descriptions-item label="任务类型">{{ task.category || '—' }}</el-descriptions-item>
        <el-descriptions-item label="店铺">{{ task.storeName || '—' }}</el-descriptions-item>
        <el-descriptions-item label="截止时间">{{ task.due || '—' }}</el-descriptions-item>
      </el-descriptions>

      <div v-if="task.detail" class="desc-block">
        <h4 class="section-title">任务说明</h4>
        <p>{{ task.detail }}</p>
      </div>

      <div v-loading="loading" class="feedback-section">
        <TaskFeedbackTimeline :feedbacks="feedbacks" empty-text="暂无反馈记录" />
      </div>
    </template>
  </el-drawer>
</template>

<style scoped>
.detail-head {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.detail-block {
  margin-bottom: 16px;
}

.section-title {
  margin: 0 0 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--ch-text);
}

.desc-block {
  margin-bottom: 16px;
}

.desc-block p {
  margin: 0;
  padding: 12px 14px;
  border-radius: var(--ch-radius-md);
  background: var(--ch-surface-muted);
  font-size: 13px;
  line-height: 1.6;
  color: var(--ch-text-secondary);
}

.feedback-section {
  min-height: 80px;
}
</style>
