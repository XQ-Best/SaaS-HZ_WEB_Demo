import {
  createLocalAssignedTask,
  deleteLocalAssignedTask,
  fetchLocalAssignedTasks,
  mapAssignedTaskToCenterTask,
  updateLocalAssignedTask,
  updateLocalAssignedTaskStatus,
} from './assignedTasksLocal'

export function fetchAssignedTasks(filters = {}) {
  return {
    success: true,
    data: fetchLocalAssignedTasks(filters),
  }
}

export function fetchAssignedTasksForCenter(auth, employees = []) {
  const filters = {}
  if (auth && !auth.isBoss && auth.employee?.id) {
    filters.employeeId = auth.employee.id
    filters.activeOnly = false
  }
  const rows = fetchLocalAssignedTasks(filters).filter((task) => {
    if (auth?.isBoss) return true
    if (task.status === '已取消') return false
    return task.employeeId === auth?.employee?.id
  })
  return rows
    .filter((task) => task.status !== '已取消')
    .map((task) => mapAssignedTaskToCenterTask(task))
}

export function assignTaskToEmployee(payload, employees = []) {
  const data = createLocalAssignedTask(payload, employees)
  return {
    success: true,
    message: `已分配给 ${data.assignee}`,
    data,
  }
}

export function updateAssignedTask(id, payload) {
  const data = updateLocalAssignedTask(id, payload)
  return { success: true, data }
}

export function updateAssignedTaskStatus(id, status, extra = {}) {
  const data = updateLocalAssignedTaskStatus(id, status, extra)
  return { success: true, data }
}

export function removeAssignedTask(id) {
  deleteLocalAssignedTask(id)
  return { success: true, message: '任务已删除' }
}

export function cancelAssignedTask(id) {
  const data = updateLocalAssignedTaskStatus(id, '已取消')
  return { success: true, message: '任务已取消', data }
}
