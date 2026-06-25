import { ACOS_THRESHOLDS, ACOS_LEVEL_META } from '@/constants/amazonBoss'
import { formatMoney, formatMoneyDecimal } from '@/utils/format'

export function getAcosLevel(acos) {
  const value = Number(acos) || 0
  if (value >= ACOS_THRESHOLDS.danger) return 'danger'
  if (value >= ACOS_THRESHOLDS.warning) return 'warning'
  if (value >= ACOS_THRESHOLDS.good) return 'normal'
  return 'good'
}

export function acosMeta(acos) {
  const level = getAcosLevel(acos)
  return { level, ...ACOS_LEVEL_META[level] }
}

export function summarizeTopProducts(products = [], limit = 20) {
  const sorted = [...products].sort((a, b) => (b.revenue7d || 0) - (a.revenue7d || 0))
  const top = sorted.slice(0, limit).map((item, index) => ({ ...item, displayRank: index + 1 }))
  const highAcos = top.filter((p) => getAcosLevel(p.acos) === 'danger' || getAcosLevel(p.acos) === 'warning')

  const totalRevenue = top.reduce((sum, p) => sum + (p.revenue7d || 0), 0)
  const totalAdSpend = top.reduce((sum, p) => sum + (p.adSpend7d || 0), 0)
  const avgAcos = totalRevenue ? Number(((totalAdSpend / totalRevenue) * 100).toFixed(1)) : 0

  return {
    top,
    total: products.length,
    highAcosCount: highAcos.length,
    dangerAcosCount: top.filter((p) => getAcosLevel(p.acos) === 'danger').length,
    avgAcos,
    totalRevenue,
    totalRevenueText: formatMoney(totalRevenue),
    totalAdSpend,
    totalAdSpendText: formatMoney(totalAdSpend),
  }
}

export function summarizeOutboundOrders(orders = []) {
  const pending = orders.filter((o) => o.status === 'pending')
  const packed = orders.filter((o) => o.status === 'packed')
  const fbmPending = [...pending, ...packed].filter((o) => o.fulfillmentType === 'fbm')
  const fbaPending = [...pending, ...packed].filter((o) => o.fulfillmentType === 'fba')

  return {
    total: orders.length,
    pending: pending.length,
    packed: packed.length,
    shipped: orders.filter((o) => o.status === 'shipped').length,
    fbmPending: fbmPending.length,
    fbaPending: fbaPending.length,
    actionRequired: pending.length + packed.length,
  }
}

export function formatAmazonMoney(amount, currency = 'USD') {
  return `${formatMoneyDecimal(amount)} ${currency}`
}
