<script setup>
import { computed } from 'vue'
import { ChatDotRound } from '@element-plus/icons-vue'
import { OUTCOME_MAP } from '@/constants/opsFeedbackDemo'
import { sortFeedbacks } from '@/utils/assignedTaskFlow'

const props = defineProps({
  feedbacks: { type: Array, default: () => [] },
  emptyText: { type: String, default: '暂无历史反馈' },
  compact: { type: Boolean, default: false },
})

const items = computed(() =>
  sortFeedbacks(props.feedbacks).map((fb) => ({
    id: fb.id,
    time: fb.submittedAt,
    label: fb.outcomeLabel || OUTCOME_MAP[fb.outcome]?.label || '反馈',
    type: OUTCOME_MAP[fb.outcome]?.type || 'info',
    content: fb.feedback,
    actor: fb.employeeName,
  })),
)

function timelineType(type) {
  if (type === 'danger') return 'danger'
  if (type === 'warning') return 'warning'
  if (type === 'success') return 'success'
  return 'primary'
}
</script>

<template>
  <div class="feedback-history" :class="{ 'feedback-history--compact': compact }">
    <div v-if="items.length" class="feedback-history__head">
      <strong>历史反馈</strong>
      <el-tag size="small" type="info" effect="plain">{{ items.length }} 条</el-tag>
    </div>

    <el-empty v-if="!items.length" :description="emptyText" :image-size="compact ? 56 : 72" />

    <el-timeline v-else class="feedback-timeline">
      <el-timeline-item
        v-for="item in items"
        :key="item.id"
        :timestamp="item.time"
        :type="timelineType(item.type)"
        placement="top"
      >
        <div class="timeline-card">
          <div class="timeline-card__head">
            <el-tag size="small" :type="item.type" effect="plain">{{ item.label }}</el-tag>
          </div>
          <p class="timeline-card__content">{{ item.content }}</p>
          <span v-if="item.actor" class="timeline-card__actor">
            <el-icon><ChatDotRound /></el-icon>
            {{ item.actor }}
          </span>
        </div>
      </el-timeline-item>
    </el-timeline>
  </div>
</template>

<style scoped>
.feedback-history__head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 13px;
  color: var(--ch-text);
}

.feedback-history--compact .feedback-history__head {
  margin-bottom: 8px;
}

.feedback-timeline {
  padding-left: 4px;
}

.timeline-card__head {
  margin-bottom: 6px;
}

.timeline-card__content {
  margin: 0 0 6px;
  font-size: 13px;
  line-height: 1.55;
  color: var(--ch-text-secondary);
}

.feedback-history--compact .timeline-card__content {
  font-size: 12px;
}

.timeline-card__actor {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--ch-text-muted);
}
</style>
