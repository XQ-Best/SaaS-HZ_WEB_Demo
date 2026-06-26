import { OUTCOME_MAP } from '@/constants/opsFeedbackDemo'
import { TASK_PRIORITY_OPTIONS } from '@/constants/assignedTasks'
import { TASK_STATUS_META } from '@/constants/operations'

export const TASK_FLOW_STEPS = [
  { key: 'assigned', title: '任务分配', description: '管理员下发任务至负责人' },
  { key: 'processing', title: '员工处理', description: '负责人跟进执行' },
  { key: 'feedback', title: '提交反馈', description: '同步进展与处理说明' },
  { key: 'closed', title: '结案', description: '任务完成或确认关闭' },
]

export function priorityMeta(priority) {
  return TASK_PRIORITY_OPTIONS.find((item) => item.value === priority) || TASK_PRIORITY_OPTIONS[1]
}

export function statusMeta(status) {
  return TASK_STATUS_META[status] || { type: 'info', label: status }
}

export function sortFeedbacks(feedbacks = []) {
  return [...feedbacks].sort((a, b) => String(b.submittedAt).localeCompare(String(a.submittedAt)))
}

/** 运营反馈 → 分配任务状态 */
export function mapOutcomeToTaskStatus(outcome) {
  if (outcome === 'resolved') return '已完成'
  if (outcome === 'in_progress') return '进行中'
  return '进行中'
}

export function taskNeedsAttention(task, feedbacks = []) {
  if (!task || task.status === '已完成' || task.status === '已取消') return false
  const latest = sortFeedbacks(feedbacks)[0]
  return latest?.outcome === 'need_help' || latest?.outcome === 'blocked'
}

export function resolveFlowActive(task, feedbacks = []) {
  if (!task) return 0
  if (task.status === '已取消') return 0
  if (task.status === '已完成') return 3

  const sorted = sortFeedbacks(feedbacks)
  if (sorted.length) {
    const latest = sorted[0]
    if (latest.outcome === 'resolved') return 3
    return 2
  }
  if (task.status === '进行中') return 1
  return 0
}

export function buildTaskTimeline(task, feedbacks = []) {
  if (!task) return []

  const items = [
    {
      id: `${task.id}_assigned`,
      type: 'assigned',
      time: task.assignedAt,
      title: '任务已分配',
      content: `${task.assignedBy || '企业管理员'} 分配给 ${task.assignee}`,
      actor: task.assignedBy || '企业管理员',
      tag: { label: '分配', type: 'primary' },
    },
  ]

  if (task.status === '已取消') {
    items.push({
      id: `${task.id}_cancelled`,
      type: 'cancelled',
      time: task.updatedAt || task.assignedAt,
      title: '任务已取消',
      content: '管理员取消了该任务',
      actor: task.assignedBy || '企业管理员',
      tag: { label: '已取消', type: 'info' },
    })
  }

  for (const fb of sortFeedbacks(feedbacks).reverse()) {
    const meta = OUTCOME_MAP[fb.outcome] || OUTCOME_MAP.in_progress
    items.push({
      id: fb.id,
      type: 'feedback',
      time: fb.submittedAt,
      title: `员工反馈 · ${meta.label}`,
      content: fb.feedback,
      actor: fb.employeeName,
      tag: { label: meta.label, type: meta.type },
      outcome: fb.outcome,
    })
  }

  if (task.status === '已完成' && !feedbacks.some((fb) => fb.outcome === 'resolved')) {
    items.push({
      id: `${task.id}_done`,
      type: 'closed',
      time: task.updatedAt || task.assignedAt,
      title: '任务已完成',
      content: task.lastFeedback || '任务已标记为完成',
      actor: task.assignee,
      tag: { label: '已完成', type: 'success' },
    })
  }

  return items.sort((a, b) => String(a.time).localeCompare(String(b.time)))
}

export function buildAssignedTaskDetail(task, feedbacks = []) {
  const sorted = sortFeedbacks(feedbacks)
  const latest = sorted[0] || null
  const flowActive = resolveFlowActive(task, sorted)

  return {
    task,
    feedbacks: sorted,
    latestFeedback: latest,
    flowSteps: TASK_FLOW_STEPS,
    flowActive,
    needsAttention: taskNeedsAttention(task, sorted),
    timeline: buildTaskTimeline(task, sorted),
    summary: {
      feedbackCount: sorted.length,
      lastOutcome: latest?.outcome || task.lastOutcome || '',
      lastOutcomeLabel: latest?.outcomeLabel || '',
      lastFeedbackAt: latest?.submittedAt || task.lastFeedbackAt || '',
    },
  }
}
