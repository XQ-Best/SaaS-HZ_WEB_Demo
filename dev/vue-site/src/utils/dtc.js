import { formatMoneyDecimal } from '@/utils/format'

export function summarizeDtcProducts(products) {
  const list = products || []
  const dailyOrders = list.reduce((s, p) => s + p.dailyOrders, 0)
  const dailyRevenue = list.reduce((s, p) => s + p.dailyOrders * p.price, 0)
  const dailyViews = list.reduce((s, p) => s + p.dailyViews, 0)
  const stock = list.reduce((s, p) => s + p.stock, 0)
  const lowStock = list.filter((p) => p.stock < 200).length
  const slowMoving = list.filter((p) => p.daysWithoutSale >= 15).length
  const hotProducts = list.filter((p) => p.dailyOrders >= 20).length
  const avgConversion = list.length
    ? list.reduce((s, p) => s + p.conversionRate, 0) / list.length
    : 0

  let healthScore = 100
  healthScore -= lowStock * 8
  healthScore -= slowMoving * 10
  healthScore -= list.filter((p) => p.cost >= p.price).length * 15
  healthScore = Math.max(0, Math.min(100, healthScore))

  const healthType = healthScore >= 85 ? 'success' : healthScore >= 70 ? 'warning' : 'danger'
  const healthLabel = healthScore >= 85 ? '运营良好' : healthScore >= 70 ? '需要关注' : '存在风险'

  return {
    skuCount: list.length,
    dailyOrders,
    dailyRevenue,
    dailyRevenueText: formatMoneyDecimal(dailyRevenue),
    dailyViews,
    stock,
    lowStock,
    slowMoving,
    hotProducts,
    avgConversion: avgConversion.toFixed(2),
    healthScore,
    healthType,
    healthLabel,
  }
}

export function summarizeDtcBySite(products, sites) {
  return (sites || []).map((site) => {
    const siteProducts = (products || []).filter((p) => p.storeId === site.id)
    const summary = summarizeDtcProducts(siteProducts)
    return { site, summary, products: siteProducts }
  })
}
