import {
  ASSIGNED_TASKS_SEED,
  PLATFORM_LABELS,
  TASK_STATUS_OPTIONS,
} from '@/constants/assignedTasks'

const STORAGE_KEY = 'crosshub_assigned_tasks'
const SEED_FLAG_KEY = 'crosshub_assigned_tasks_seeded'

function nowText() {
  return new Date().toISOString().replace('T', ' ').slice(0, 19)
}

function loadAll() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveAll(items) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
}

function ensureSeedTasks() {
  if (localStorage.getItem(SEED_FLAG_KEY)) return
  const existing = loadAll()
  const ids = new Set(existing.map((item) => item.id))
  const merged = [...existing, ...ASSIGNED_TASKS_SEED.filter((item) => !ids.has(item.id))]
  saveAll(merged)
  localStorage.setItem(SEED_FLAG_KEY, '1')
}

function normalizeStatus(status) {
  return TASK_STATUS_OPTIONS.includes(status) ? status : '待处理'
}

export function fetchLocalAssignedTasks(filters = {}) {
  ensureSeedTasks()
  let items = loadAll()

  if (filters.employeeId) {
    items = items.filter((item) => item.employeeId === filters.employeeId)
  }
  if (filters.status) {
    items = items.filter((item) => item.status === filters.status)
  }
  if (filters.platformKey) {
    items = items.filter((item) => item.platformKey === filters.platformKey)
  }
  if (filters.activeOnly) {
    items = items.filter((item) => item.status !== '已完成' && item.status !== '已取消')
  }

  return items.sort((a, b) => String(b.assignedAt).localeCompare(String(a.assignedAt)))
}

export function createLocalAssignedTask(payload, employees = []) {
  ensureSeedTasks()
  const items = loadAll()
  const employee = employees.find((emp) => emp.id === payload.employeeId)
  if (!employee) {
    throw new Error('请选择有效员工')
  }
  if (!payload.title?.trim()) {
    throw new Error('请填写任务标题')
  }

  const row = {
    id: `assign_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
    employeeId: employee.id,
    assignee: employee.name,
    title: payload.title.trim(),
    description: (payload.description || '').trim(),
    platformKey: payload.platformKey || employee.platforms?.[0] || 'temu',
    category: payload.category || '运营',
    priority: payload.priority || 'medium',
    status: '待处理',
    progress: 0,
    due: payload.due || '今天 18:00',
    assignedBy: payload.assignedBy || '企业管理员',
    assignedAt: nowText(),
    updatedAt: nowText(),
  }

  items.unshift(row)
  saveAll(items)
  return row
}

export function updateLocalAssignedTask(id, payload) {
  ensureSeedTasks()
  const items = loadAll()
  const index = items.findIndex((item) => item.id === id)
  if (index === -1) throw new Error('任务不存在')

  items[index] = {
    ...items[index],
    ...payload,
    updatedAt: nowText(),
  }
  saveAll(items)
  return items[index]
}

export function updateLocalAssignedTaskStatus(id, status, extra = {}) {
  const normalized = normalizeStatus(status)
  const progress =
    extra.progress ??
    (normalized === '已完成' ? 100 : normalized === '进行中' ? Math.max(extra.progress || 0, 50) : 0)
  return updateLocalAssignedTask(id, { status: normalized, progress, ...extra })
}

export function deleteLocalAssignedTask(id) {
  ensureSeedTasks()
  const items = loadAll()
  const index = items.findIndex((item) => item.id === id)
  if (index === -1) throw new Error('任务不存在')
  const [removed] = items.splice(index, 1)
  saveAll(items)
  return removed
}

export function mapAssignedTaskToCenterTask(task) {
  const platformKey = task.platformKey || 'temu'
  const routes = {
    temu: '/employee/temu',
    aliexpress: '/employee/aliexpress',
    amazon: '/employee/amazon',
    walmart: '/employee/walmart',
    pdd: '/employee/pdd',
    douyin: '/employee/douyin',
    channels: '/employee/channels',
    '1688': '/employee/1688',
    dtc: '/employee/dtc',
  }
  return {
    id: task.id,
    source: 'assigned',
    employeeId: task.employeeId,
    assignee: task.assignee,
    title: task.title,
    detail: task.description || '',
    platform: PLATFORM_LABELS[platformKey] || platformKey,
    platformKey,
    category: task.category || '运营',
    priority: task.priority || 'medium',
    status: task.status || '待处理',
    progress: task.progress ?? 0,
    due: task.due || '今天 18:00',
    storeName: task.storeName || '—',
    route: routes[platformKey] || '',
    assignedBy: task.assignedBy,
    assignedAt: task.assignedAt,
    updatedAt: task.updatedAt,
  }
}
