import {
  createLocalAssignedTask,
  deleteLocalAssignedTask,
  fetchLocalAssignedTaskById,
  fetchLocalAssignedTasks,
  mapAssignedTaskToCenterTask,
  updateLocalAssignedTask,
  updateLocalAssignedTaskStatus,
} from './assignedTasksLocal'
import { fetchFeedbacksByTaskId } from './opsFeedbackLocal'
import { buildAssignedTaskDetail, mapOutcomeToTaskStatus } from '@/utils/assignedTaskFlow'

function mapAssignedRows(rows) {
  return rows
    .filter((task) => task.status !== '已取消')
    .map((task) => mapAssignedTaskToCenterTask(task))
}

export function fetchAssignedTasks(filters = {}) {
  return {
    success: true,
    data: fetchLocalAssignedTasks(filters),
  }
}

export function fetchAssignedTaskDetail(taskId) {
  const task = fetchLocalAssignedTaskById(taskId)
  if (!task) {
    throw new Error('任务不存在')
  }
  const feedbacks = fetchFeedbacksByTaskId(taskId)
  return {
    success: true,
    data: buildAssignedTaskDetail(task, feedbacks),
  }
}

export function fetchAssignedTasksForCenter(auth) {
  if (auth?.isBoss) {
    return mapAssignedRows(fetchLocalAssignedTasks())
  }
  if (auth?.isEmployee && auth.employee?.id) {
    return mapAssignedRows(
      fetchLocalAssignedTasks({ assigneeId: auth.employee.id }).filter(
        (task) => (task.assigneeType || 'employee') === 'employee',
      ),
    )
  }
  return []
}

export function fetchWarehouseAssignedTasks(auth) {
  if (!auth?.isWarehouse || !auth.warehouse?.id) return []
  return mapAssignedRows(
    fetchLocalAssignedTasks({ assigneeId: auth.warehouse.id }).filter(
      (task) => task.assigneeType === 'warehouse',
    ),
  )
}

export function assignTask(payload, context = {}) {
  const data = createLocalAssignedTask(payload, context)
  return {
    success: true,
    message: `已分配给 ${data.assignee}`,
    data,
  }
}

export function assignTaskToEmployee(payload, employees = []) {
  return assignTask(payload, { employees, warehouseStaff: [] })
}

export function updateAssignedTask(id, payload) {
  const data = updateLocalAssignedTask(id, payload)
  return { success: true, data }
}

export function updateAssignedTaskStatus(id, status, extra = {}) {
  const data = updateLocalAssignedTaskStatus(id, status, extra)
  return { success: true, data }
}

/** 负责人提交反馈后同步分配任务进展 */
export function syncAssignedTaskFeedback(taskId, { outcome, feedback, employeeName, assigneeName }) {
  const task = fetchLocalAssignedTaskById(taskId)
  if (!task) return null

  const status = mapOutcomeToTaskStatus(outcome)
  const name = assigneeName || employeeName || task.assignee

  return updateLocalAssignedTaskStatus(taskId, status, {
    lastOutcome: outcome,
    lastFeedback: (feedback || '').trim(),
    lastFeedbackAt: new Date().toISOString().replace('T', ' ').slice(0, 19),
    lastFeedbackBy: name,
  })
}

export function removeAssignedTask(id) {
  deleteLocalAssignedTask(id)
  return { success: true, message: '任务已删除' }
}

export function cancelAssignedTask(id) {
  const data = updateLocalAssignedTaskStatus(id, '已取消')
  return { success: true, message: '任务已取消', data }
}
