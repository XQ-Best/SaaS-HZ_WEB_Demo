/** 根据员工列表构建 storeId → 负责人 映射 */
export function buildStoreAssigneeMap(employees = []) {
  const map = {}
  for (const employee of employees) {
    if (employee.status === false) continue
    for (const storeId of employee.assignedStoreIds || []) {
      map[storeId] = {
        employeeId: employee.id,
        name: employee.name,
        role: employee.role,
      }
    }
  }
  return map
}

export function resolveStoreAssignee(storeId, assigneeMap, fallback = '未分配') {
  return assigneeMap[storeId]?.name || fallback
}

export function attachAssignee(item, storeId, assigneeMap) {
  const assignee = assigneeMap[storeId]
  return {
    ...item,
    storeId,
    assigneeName: assignee?.name || '未分配',
    assigneeRole: assignee?.role || '',
  }
}

export function enrichWithAssignee(items = [], assigneeMap = {}) {
  return items.map((item) => attachAssignee(item, item.storeId, assigneeMap))
}

/** 将问题列表按店铺分组，并汇总待办数 */
export function groupIssuesByStore(items = [], { issueFilter } = {}) {
  const groups = new Map()

  for (const item of items) {
    const storeId = item.storeId || '_unknown'
    if (!groups.has(storeId)) {
      groups.set(storeId, {
        storeId,
        storeName: item.storeName || '—',
        assigneeName: item.assigneeName || '未分配',
        assigneeRole: item.assigneeRole || '',
        items: [],
        issueCount: 0,
      })
    }
    const group = groups.get(storeId)
    group.items.push(item)
    if (!issueFilter || issueFilter(item)) {
      group.issueCount += 1
    }
  }

  return [...groups.values()].sort((a, b) => a.storeName.localeCompare(b.storeName, 'zh-CN'))
}

export function storeAssignmentLabels(storeIds = [], storeNameMap = {}) {
  if (!storeIds.length) return '—'
  return storeIds.map((id) => storeNameMap[id] || id).join('、')
}

export function validateStoreAssignmentConflict(employees, assignedStoreIds, employeeId) {
  for (const storeId of assignedStoreIds || []) {
    const conflict = employees.find(
      (employee) =>
        employee.id !== employeeId &&
        employee.status !== false &&
        (employee.assignedStoreIds || []).includes(storeId),
    )
    if (conflict) {
      return `店铺「${storeId}」已分配给「${conflict.name}」`
    }
  }
  return null
}
