import { WAREHOUSE_SITES_SEED } from '@/constants/warehouseSites'

export function resolveWarehouseNames(ids, sites = WAREHOUSE_SITES_SEED) {
  const list = Array.isArray(ids) ? ids : []
  if (!list.length) return []
  const nameMap = Object.fromEntries((sites || []).map((site) => [site.id, site.name]))
  return list.map((id) => nameMap[id] || id)
}

export function formatWarehouseScopeText(names) {
  const list = (names || []).filter(Boolean)
  if (!list.length) return ''
  if (list.length <= 2) return list.join('、')
  return `${list.slice(0, 2).join('、')} 等 ${list.length} 仓`
}
