<script setup>
import { computed } from 'vue'
import {
  ChatLineSquare,
  CircleCheck,
  Clock,
  WarningFilled,
  CircleCloseFilled,
} from '@element-plus/icons-vue'
import { OUTCOME_OPTIONS } from '@/constants/opsFeedbackDemo'
import { TASK_STATUS_META } from '@/constants/operations'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  task: { type: Object, default: null },
  outcome: { type: String, default: 'in_progress' },
  feedback: { type: String, default: '' },
  submitting: { type: Boolean, default: false },
  isAssigned: { type: Boolean, default: false },
  sourceLabel: { type: String, default: '任务' },
  sourceType: { type: String, default: 'info' },
})

const emit = defineEmits(['update:modelValue', 'update:outcome', 'update:feedback', 'submit', 'closed'])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const outcomeValue = computed({
  get: () => props.outcome,
  set: (value) => emit('update:outcome', value),
})

const feedbackValue = computed({
  get: () => props.feedback,
  set: (value) => emit('update:feedback', value),
})

const outcomeIcons = {
  resolved: CircleCheck,
  in_progress: Clock,
  need_help: WarningFilled,
  blocked: CircleCloseFilled,
}

const syncHint = computed(() =>
  props.isAssigned
    ? '提交后将同步至管理员「任务分配」'
    : '提交后将同步至运营总览',
)

const dialogTitle = computed(() =>
  props.isAssigned ? '提交分配任务反馈' : '提交处理反馈',
)

function handleClosed() {
  emit('closed')
}
</script>

<template>
  <el-dialog
    v-model="visible"
    width="520px"
    class="task-feedback-dialog"
    align-center
    destroy-on-close
    :show-close="!submitting"
    @closed="handleClosed"
  >
    <template #header>
      <div class="dialog-head">
        <div class="dialog-head__icon">
          <el-icon><ChatLineSquare /></el-icon>
        </div>
        <div>
          <h3 class="dialog-head__title">{{ dialogTitle }}</h3>
          <p class="dialog-head__sub">{{ syncHint }}</p>
        </div>
      </div>
    </template>

    <template v-if="task">
      <article class="task-card" :class="{ 'task-card--assigned': isAssigned }">
        <div class="task-card__tags">
          <el-tag size="small" effect="plain">{{ task.platform }}</el-tag>
          <el-tag
            :type="isAssigned ? 'primary' : sourceType"
            size="small"
            effect="plain"
          >
            {{ isAssigned ? '管理员分配' : sourceLabel }}
          </el-tag>
          <el-tag
            v-if="task.status"
            :type="TASK_STATUS_META[task.status]?.type || 'info'"
            size="small"
          >
            {{ task.status }}
          </el-tag>
        </div>
        <h4 class="task-card__title">{{ task.title }}</h4>
        <p v-if="task.detail" class="task-card__detail">{{ task.detail }}</p>
        <div v-if="task.due" class="task-card__meta">
          <span>截止 {{ task.due }}</span>
        </div>
      </article>

      <section class="form-section">
        <label class="form-section__label">处理结果</label>
        <div class="outcome-grid">
          <button
            v-for="item in OUTCOME_OPTIONS"
            :key="item.value"
            type="button"
            class="outcome-chip"
            :class="[
              `outcome-chip--${item.type}`,
              { 'is-active': outcomeValue === item.value },
            ]"
            @click="outcomeValue = item.value"
          >
            <el-icon class="outcome-chip__icon">
              <component :is="outcomeIcons[item.value]" />
            </el-icon>
            <span>{{ item.label }}</span>
          </button>
        </div>
      </section>

      <section class="form-section">
        <label class="form-section__label" for="task-feedback-input">处理说明</label>
        <el-input
          id="task-feedback-input"
          v-model="feedbackValue"
          type="textarea"
          :rows="4"
          resize="none"
          maxlength="500"
          show-word-limit
          :placeholder="isAssigned
            ? '说明当前处理进展、已完成事项或下一步计划…'
            : '说明处理措施、进展或需要协助的原因…'"
        />
      </section>
    </template>

    <template #footer>
      <div class="dialog-footer">
        <p class="dialog-footer__hint">
          <el-icon><ChatLineSquare /></el-icon>
          {{ syncHint }}
        </p>
        <div class="dialog-footer__actions">
          <el-button :disabled="submitting" @click="visible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="emit('submit')">
            提交反馈
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.dialog-head {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.dialog-head__icon {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: var(--ch-radius-md);
  background: var(--ch-primary-soft);
  color: var(--ch-primary);
  flex-shrink: 0;
}

.dialog-head__icon .el-icon {
  font-size: 20px;
}

.dialog-head__title {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: var(--ch-text);
  line-height: 1.35;
}

.dialog-head__sub {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--ch-text-muted);
}

.task-card {
  margin-bottom: 20px;
  padding: 14px 16px 14px 18px;
  border: 1px solid var(--ch-border);
  border-left: 3px solid var(--el-color-info);
  border-radius: var(--ch-radius-md);
  background: linear-gradient(135deg, var(--ch-surface-muted) 0%, var(--ch-surface) 100%);
}

.task-card--assigned {
  border-left-color: var(--ch-primary);
}

.task-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.task-card__title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--ch-text);
  line-height: 1.45;
}

.task-card__detail {
  margin: 8px 0 0;
  font-size: 13px;
  color: var(--ch-text-secondary);
  line-height: 1.55;
}

.task-card__meta {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed var(--ch-border);
  font-size: 12px;
  color: var(--ch-text-muted);
}

.form-section {
  margin-bottom: 18px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.form-section__label {
  display: block;
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: 600;
  color: var(--ch-text);
}

.outcome-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.outcome-chip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 44px;
  padding: 10px 12px;
  border: 1px solid var(--ch-border);
  border-radius: var(--ch-radius-md);
  background: var(--ch-surface);
  color: var(--ch-text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s, color 0.15s, box-shadow 0.15s;
}

.outcome-chip:hover {
  border-color: var(--ch-primary-muted);
  color: var(--ch-text);
}

.outcome-chip__icon {
  font-size: 16px;
}

.outcome-chip.is-active {
  font-weight: 600;
  box-shadow: 0 0 0 1px inset;
}

.outcome-chip--success.is-active {
  border-color: var(--el-color-success);
  background: var(--el-color-success-light-9);
  color: var(--el-color-success);
  box-shadow: 0 0 0 1px var(--el-color-success-light-5);
}

.outcome-chip--primary.is-active {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
  box-shadow: 0 0 0 1px var(--el-color-primary-light-5);
}

.outcome-chip--warning.is-active {
  border-color: var(--el-color-warning);
  background: var(--el-color-warning-light-9);
  color: var(--el-color-warning);
  box-shadow: 0 0 0 1px var(--el-color-warning-light-5);
}

.outcome-chip--danger.is-active {
  border-color: var(--el-color-danger);
  background: var(--el-color-danger-light-9);
  color: var(--el-color-danger);
  box-shadow: 0 0 0 1px var(--el-color-danger-light-5);
}

.dialog-footer {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.dialog-footer__hint {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin: 0;
  font-size: 12px;
  color: var(--ch-text-muted);
}

.dialog-footer__actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}
</style>

<style>
.task-feedback-dialog.el-dialog {
  border-radius: var(--ch-radius-lg);
  overflow: hidden;
}

.task-feedback-dialog .el-dialog__header {
  margin-right: 0;
  padding: 20px 24px 12px;
  border-bottom: 1px solid var(--ch-border);
}

.task-feedback-dialog .el-dialog__body {
  padding: 20px 24px 8px;
}

.task-feedback-dialog .el-dialog__footer {
  padding: 12px 24px 20px;
  border-top: 1px solid var(--ch-border);
  background: var(--ch-surface-muted);
}
</style>
