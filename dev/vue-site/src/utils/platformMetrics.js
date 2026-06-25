import { buildStoreAssigneeMap } from '@/utils/storeAssignment'
import { summarizeTemuProducts } from '@/utils/temuStore'
import { summarizeAliExpressOrders } from '@/utils/aliexpress'
import { countAmazonPendingAlerts } from '@/utils/amazon'
import { summarize1688PurchaseOrders } from '@/utils/alibaba1688'
import { formatMoney } from '@/utils/format'

function primaryOwner(employees, platformKey, assigneeMap, storeIds) {
  const counts = {}
  for (const storeId of storeIds) {
    const name = assigneeMap[storeId]?.name
    if (name) counts[name] = (counts[name] || 0) + 1
  }
  const top = Object.entries(counts).sort((a, b) => b[1] - a[1])[0]
  if (top) return top[0]

  const fallback = employees.find(
    (employee) =>
      employee.status !== false && (employee.platforms || []).includes(platformKey),
  )
  return fallback?.name || '—'
}

export function buildPlatformSalesRows(payload) {
  const { temu, aliexpress, amazon, alibaba1688, dtc, employees = [] } = payload
  const assigneeMap = buildStoreAssigneeMap(employees)
  const rows = []

  if (temu?.products?.length) {
    const summary = summarizeTemuProducts(temu.products)
    const storeIds = (temu.stores || []).map((store) => store.id)
    rows.push({
      id: 'temu',
      name: 'Temu',
      owner: primaryOwner(employees, 'temu', assigneeMap, storeIds),
      revenue: summary.dailyRevenue,
      orders: summary.dailySales,
      alerts: summary.lossCount + summary.restockCount,
      storeCount: storeIds.length,
      revenueText: summary.dailyRevenueText || formatMoney(summary.dailyRevenue),
    })
  }

  if (aliexpress?.orders?.length) {
    const summary = summarizeAliExpressOrders(aliexpress.orders)
    const storeIds = (aliexpress.stores || []).map((store) => store.id)
    const pending = summary.pending
    rows.push({
      id: 'aliexpress',
      name: 'AliExpress',
      owner: primaryOwner(employees, 'aliexpress', assigneeMap, storeIds),
      revenue: summary.totalAmount,
      orders: summary.total,
      alerts: pending,
      storeCount: storeIds.length,
      revenueText: summary.totalAmountText,
    })
  }

  if (amazon?.stores?.length) {
    const alerts = countAmazonPendingAlerts(amazon)
    const storeIds = (amazon.stores || []).map((store) => store.id)
    const critical = (amazon.accountMetrics || []).filter((m) => m.status === 'critical').length
    rows.push({
      id: 'amazon',
      name: 'Amazon',
      owner: primaryOwner(employees, 'amazon', assigneeMap, storeIds),
      revenue: 0,
      orders: (amazon.buyerMessages || []).filter((m) => m.status === 'replied').length,
      alerts,
      storeCount: storeIds.length,
      revenueText: critical ? `${critical} 项爆红` : '今日巡检',
    })
  }

  if (alibaba1688?.purchaseOrders?.length || alibaba1688?.stores?.length) {
    const summary = summarize1688PurchaseOrders(alibaba1688.purchaseOrders || [])
    const alertCount = (alibaba1688.supplierAlerts || []).filter((a) => !a.resolved).length
    const storeIds = (alibaba1688.stores || []).map((store) => store.id)
    rows.push({
      id: '1688',
      name: '1688',
      owner: primaryOwner(employees, '1688', assigneeMap, storeIds),
      revenue: summary.totalAmount,
      orders: summary.total,
      alerts: summary.pending + alertCount,
      storeCount: storeIds.length,
      revenueText: summary.totalAmountText,
    })
  }

  if (dtc?.orders?.length || dtc?.stores?.length) {
    const orders = dtc.orders || []
    const revenue = orders.reduce((sum, order) => sum + (order.amount || 0), 0)
    const pending = orders.filter((order) => order.status === 'pending').length
    const storeIds = (dtc.stores || []).map((store) => store.id)
    rows.push({
      id: 'dtc',
      name: '独立站',
      owner: primaryOwner(employees, 'shopify', assigneeMap, storeIds),
      revenue,
      orders: orders.length,
      alerts: pending,
      storeCount: storeIds.length,
      revenueText: formatMoney(revenue),
    })
  }

  return rows
}
