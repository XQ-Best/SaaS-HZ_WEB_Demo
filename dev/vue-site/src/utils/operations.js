import { OPERATION_TASKS } from '@/constants/operations'

export function calcTaskStats(tasks = OPERATION_TASKS) {
  const total = tasks.length
  const completed = tasks.filter((t) => t.status === '已完成').length
  const inProgress = tasks.filter((t) => t.status === '进行中').length
  const pending = tasks.filter((t) => t.status === '待处理').length
  const overdue = tasks.filter((t) => t.status === '已逾期').length
  const completionRate = total ? Math.round((completed / total) * 100) : 0
  const todayDone = tasks.filter((t) => t.status === '已完成' && t.due.startsWith('今天')).length

  return { total, completed, inProgress, pending, overdue, completionRate, todayDone }
}

export function groupTasksByAssignee(tasks = OPERATION_TASKS) {
  const map = new Map()
  for (const task of tasks) {
    if (!map.has(task.assignee)) {
      map.set(task.assignee, { assignee: task.assignee, total: 0, completed: 0, inProgress: 0, overdue: 0 })
    }
    const row = map.get(task.assignee)
    row.total += 1
    if (task.status === '已完成') row.completed += 1
    if (task.status === '进行中') row.inProgress += 1
    if (task.status === '已逾期') row.overdue += 1
  }
  return [...map.values()].map((row) => ({
    ...row,
    rate: row.total ? Math.round((row.completed / row.total) * 100) : 0,
  }))
}

export function groupTasksByPlatform(tasks = OPERATION_TASKS) {
  const map = new Map()
  for (const task of tasks) {
    if (!map.has(task.platform)) {
      map.set(task.platform, { platform: task.platform, total: 0, completed: 0, active: 0, overdue: 0 })
    }
    const row = map.get(task.platform)
    row.total += 1
    if (task.status === '已完成') row.completed += 1
    if (task.status === '进行中' || task.status === '待处理') row.active += 1
    if (task.status === '已逾期') row.overdue += 1
  }
  return [...map.values()]
}

export function filterTasksForAuth(employees, auth) {
  if (!auth || auth.isBoss) return OPERATION_TASKS

  const employeeId = auth.employee?.id
  const employeeName = auth.employee?.name
  const platforms = new Set(auth.employee?.platforms || [])

  return OPERATION_TASKS.filter((task) => {
    if (employeeId && task.employeeId === employeeId) return true
    if (employeeName && task.assignee === employeeName) return true
    if (task.platformKey && platforms.has(task.platformKey)) return true
    if (task.platformKey === 'dtc' && (platforms.has('shopify') || platforms.has('wordpress'))) {
      return true
    }
    return false
  })
}
