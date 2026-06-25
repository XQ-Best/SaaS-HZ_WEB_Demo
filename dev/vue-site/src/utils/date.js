/** 统一使用本地日期，避免 UTC 时区导致「今日」快照匹配失败 */
export function localDateKey(date = new Date()) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

export function dateOffset(days) {
  const d = new Date()
  d.setDate(d.getDate() - days)
  return localDateKey(d)
}

export function daysBetween(fromDate, toDate) {
  const from = new Date(`${fromDate}T00:00:00`)
  const to = new Date(`${toDate}T00:00:00`)
  return Math.round((to - from) / (1000 * 60 * 60 * 24))
}
