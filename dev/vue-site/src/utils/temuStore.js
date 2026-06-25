import { formatMoney, formatMoneyDecimal } from '@/utils/format'

export function summarizeTemuProducts(products) {
  const list = products || []
  const onlineItems = list.filter((p) => (p.listingStatus || 'online') === 'online')
  const offlineItems = list.filter((p) => p.listingStatus === 'offline')
  const lossItems = list.filter((p) => p.isLoss)
  const slowItems = list.filter((p) => p.slowMoving)
  const hotItems = list.filter((p) => p.isHot)
  const restockItems = list.filter(
    (p) => p.restock.urgency === 'critical' || p.restock.urgency === 'warning',
  )

  const dailySales = onlineItems.reduce((sum, p) => sum + p.dailySales, 0)
  const dailyRevenue = onlineItems.reduce((sum, p) => sum + p.dailySales * p.sellingPrice, 0)
  const officialStock = onlineItems.reduce((sum, p) => sum + p.officialStock, 0)
  const totalLoss = lossItems.reduce(
    (sum, p) => sum + Math.abs(p.unitProfit) * Math.max(p.officialStock, 1),
    0,
  )

  const offlineHint = offlineItems.length ? `已下架 ${offlineItems.length}` : `共 ${list.length} 个 SKU`

  return {
    skuCount: list.length,
    onlineCount: onlineItems.length,
    offlineCount: offlineItems.length,
    onlineHint: offlineHint,
    lossCount: lossItems.length,
    slowCount: slowItems.length,
    hotCount: hotItems.length,
    restockCount: restockItems.length,
    dailySales,
    dailyRevenue,
    officialStock,
    totalLoss,
    totalLossText: formatMoneyDecimal(totalLoss),
    dailyRevenueText: formatMoney(dailyRevenue),
  }
}

export function summarizeTemuByStore(products, stores) {
  return (stores || []).map((store) => {
    const storeProducts = (products || []).filter((p) => p.storeId === store.id)
    return {
      store,
      summary: summarizeTemuProducts(storeProducts),
      products: storeProducts,
    }
  })
}
