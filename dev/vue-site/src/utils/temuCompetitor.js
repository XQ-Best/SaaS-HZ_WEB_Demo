import {
  getCompetitorSnapshots,
  todayKey,
} from '@/api/temuCompetitorSnapshotsLocal'
import { dateOffset, daysBetween } from '@/utils/date'

export function parseCompetitorHost(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return url
  }
}

function detectNewProducts(prevSnapshot, currentSnapshot) {
  if (!prevSnapshot) return []
  const prevIds = new Set(prevSnapshot.products.map((p) => p.productId))
  return currentSnapshot.products
    .filter((p) => !prevIds.has(p.productId))
    .map((p) => ({
      ...p,
      daysSinceListed: 0,
      listedLabel: '今日上新',
    }))
}

function detectRecentListings(currentSnapshot, withinDays = 7) {
  const cutoff = dateOffset(withinDays)
  const today = todayKey()
  return currentSnapshot.products
    .filter((p) => p.listedAt >= cutoff)
    .map((p) => {
      const days = daysBetween(p.listedAt, today)
      return {
        ...p,
        daysSinceListed: days,
        listedLabel: days === 0 ? '今日上新' : `${days} 日前上架`,
      }
    })
    .sort((a, b) => b.listedAt.localeCompare(a.listedAt))
}

function detectSalesSpikes(currentSnapshot, prevSnapshot) {
  const spikes = []
  const prevMap = prevSnapshot
    ? Object.fromEntries(prevSnapshot.products.map((p) => [p.productId, p]))
    : {}

  for (const product of currentSnapshot.products) {
    const prev = prevMap[product.productId]
    const avg7 = product.salesHistory.reduce((s, v) => s + v, 0) / product.salesHistory.length
    const prevDaily = prev?.dailySales ?? avg7
    const growthVsPrev = prevDaily ? ((product.dailySales - prevDaily) / prevDaily) * 100 : 0
    const growthVsAvg = avg7 ? ((product.dailySales - avg7) / avg7) * 100 : 0

    const isSpike = growthVsAvg >= 50 || growthVsPrev >= 80
    if (!isSpike) continue

    spikes.push({
      ...product,
      prevDailySales: prevDaily,
      avg7DailySales: Math.round(avg7),
      growthVsPrev: Math.round(growthVsPrev),
      growthVsAvg: Math.round(growthVsAvg),
      growthVsPrevText: `${growthVsPrev >= 0 ? '+' : ''}${growthVsPrev.toFixed(0)}%`,
      growthVsAvgText: `${growthVsAvg >= 0 ? '+' : ''}${growthVsAvg.toFixed(0)}%`,
      anomalyType: growthVsPrev >= 80 ? '日销激增' : '偏离均值',
      severity: growthVsPrev >= 120 || growthVsAvg >= 100 ? 'high' : 'medium',
    })
  }

  return spikes.sort((a, b) => b.growthVsAvg - a.growthVsAvg)
}

export function buildCompetitorMonitorReport(competitor) {
  const snapshots = getCompetitorSnapshots(competitor.id)
  const current = snapshots[0]
  if (!current) return null

  const previous = snapshots[1] || null
  const newProducts = detectNewProducts(previous, current)
  const recentListings = detectRecentListings(current, 7)
  const salesSpikes = detectSalesSpikes(current, previous)

  return {
    id: competitor.id,
    label: competitor.label,
    url: competitor.url,
    host: parseCompetitorHost(competitor.url),
    analyzedAt: current.crawledAt,
    crawlDate: current.date,
    previousCrawlDate: previous?.date || null,
    snapshotCount: snapshots.length,
    summary: {
      totalProducts: current.productCount,
      newToday: newProducts.length,
      recentListings: recentListings.length,
      salesSpikes: salesSpikes.length,
      highSeveritySpikes: salesSpikes.filter((s) => s.severity === 'high').length,
    },
    newProducts,
    recentListings,
    salesSpikes,
  }
}
