import { getDtcStoreMeta } from '@/api/dtcDemoLocal'
import { dtcPlatformLabel } from '@/constants/platforms'

/** 将账户绑定店铺转为独立站运营页使用的站点信息 */
export function normalizeDtcStore(store) {
  const meta = getDtcStoreMeta(store.id) || {}
  return {
    id: store.id,
    name: store.storeName,
    domain: meta.domain || store.account || '—',
    platform: dtcPlatformLabel(store.platform),
    currency: meta.currency,
  }
}

/** 合并多店铺流量来源数据 */
export function aggregateDtcTraffic(trafficByStore, storeIds = []) {
  const merged = new Map()

  for (const storeId of storeIds) {
    const rows = trafficByStore[storeId] || []
    for (const row of rows) {
      const existing = merged.get(row.source)
      if (!existing) {
        merged.set(row.source, { ...row })
        continue
      }
      existing.visits += row.visits
      existing.orders += row.orders
      existing.spend += row.spend
    }
  }

  return Array.from(merged.values()).map((row) => ({
    ...row,
    conversion: row.visits ? Number(((row.orders / row.visits) * 100).toFixed(2)) : 0,
  }))
}
