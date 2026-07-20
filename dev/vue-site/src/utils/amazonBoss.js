import { ACOS_THRESHOLDS, ACOS_LEVEL_META } from '@/constants/amazonBoss'

const STATUS_ONLY_NAME = /^(在售|停售|缺货|active|inactive|out of stock|–|-)$/i
const PRICE_ONLY_NAME = /^(?:US\$|USD\$?|\$|EUR€?|£|¥|CN¥|R\$)?\s*[\d,]+(?:\.\d+)?(?:\s*(?:USD|EUR|GBP|CNY|JPY))?\s*$/i
const UI_ACTION_NAME = /^(了解更多|创建\s*A\/?B\s*试验|查看建议|编辑未来|报告缺失|learn more|create a\/?b test|view suggestion|edit future|report missing)/i
const DATE_ONLY_NAME = /^\d{4}[/-]\d{1,2}[/-]\d{1,2}$/
const GCID_LIKE_ASIN = /^G\d{9}$/i

function isJunkProductName(name) {
  const text = String(name || '').trim()
  if (!text || STATUS_ONLY_NAME.test(text) || PRICE_ONLY_NAME.test(text)) return true
  if (UI_ACTION_NAME.test(text)) return true
  if (DATE_ONLY_NAME.test(text)) return true
  if (text.length <= 10 && !/[A-Za-z]{4,}/.test(text) && /^[\u4e00-\u9fff/A-B\s]+$/i.test(text)) return true
  return false
}

function looksLikeProductTitle(name) {
  const text = String(name || '').trim()
  if (isJunkProductName(text)) return false
  if (text.length >= 24) return true
  const words = text.match(/[A-Za-z\u4e00-\u9fff]{2,}/g) || []
  return words.length >= 4
}

/** 判断是否为有效的 Amazon 产品行（必须有 ASIN 和真实商品名） */
export function isValidAmazonProduct(product) {
  if (!product) return false
  const asin = String(product.asin || '').trim()
  if (!/^[A-Z0-9]{10}$/i.test(asin) || GCID_LIKE_ASIN.test(asin)) return false
  const name = String(product.productName || product.product_name || '').trim()
  if (isJunkProductName(name)) return false
  if (!/[A-Za-z\u4e00-\u9fff]/.test(name)) return false
  const revenue = parseAmazonAmount(product.revenue7d ?? product.revenue_30d ?? product.revenue30d)
  const orders = Number(product.orders7d ?? product.orders_30d ?? product.orders30d) || 0
  const inventory = Number(product.inventory ?? product.unitsOnHand ?? 0) || 0
  const hasActivity = revenue > 0 || orders > 0 || inventory > 0
  return hasActivity || looksLikeProductTitle(name)
}

/** 解析 US$1,518.28 / 10,411 等 Amazon 金额文本为数字 */
export function parseAmazonAmount(value) {
  if (value == null || value === '') return 0
  if (typeof value === 'number' && Number.isFinite(value)) return value
  const cleaned = String(value).replace(/US\$/gi, '').replace(/[^\d.-]/g, '')
  const num = Number(cleaned)
  return Number.isFinite(num) ? num : 0
}

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
  const normalized = products
    .filter(isValidAmazonProduct)
    .map((p) => ({
    ...p,
    revenue7d: parseAmazonAmount(p.revenue7d),
    adSpend7d: parseAmazonAmount(p.adSpend7d),
    acos: Number(p.acos) || 0,
    tacos: Number(p.tacos) || 0,
    orders7d: Number(p.orders7d) || 0,
    sessions7d: Number(p.sessions7d) || 0,
    conversionRate: Number(p.conversionRate) || 0,
    profitMargin: p.profitMargin == null ? null : Number(p.profitMargin) || 0,
  }))
  const hasActivity = (item) => item.revenue7d > 0 || item.orders7d > 0 || item.sessions7d > 0 || item.adSpend7d > 0
  const active = normalized.filter(hasActivity)
  const inactive = normalized.filter((item) => !hasActivity(item))
  const sorted = [
    ...[...active].sort((a, b) => b.revenue7d - a.revenue7d || b.orders7d - a.orders7d || b.sessions7d - a.sessions7d),
    ...[...inactive].sort((a, b) => (a.productName || '').localeCompare(b.productName || '')),
  ]
  const top = sorted.slice(0, limit).map((item, index) => ({ ...item, displayRank: index + 1 }))
  const highAcos = top.filter((p) => getAcosLevel(p.acos) === 'danger' || getAcosLevel(p.acos) === 'warning')

  const totalRevenue = top.reduce((sum, p) => sum + p.revenue7d, 0)
  const totalAdSpend = top.reduce((sum, p) => sum + p.adSpend7d, 0)
  const withAcos = top.filter((p) => p.acos > 0)
  const avgAcos = withAcos.length
    ? Number((withAcos.reduce((s, p) => s + p.acos, 0) / withAcos.length).toFixed(1))
    : totalRevenue && totalAdSpend
      ? Number(((totalAdSpend / totalRevenue) * 100).toFixed(1))
      : 0

  return {
    top,
    total: products.filter(isValidAmazonProduct).length,
    highAcosCount: highAcos.length,
    dangerAcosCount: top.filter((p) => getAcosLevel(p.acos) === 'danger').length,
    avgAcos,
    totalRevenue,
    totalRevenueText: formatAmazonMoney(totalRevenue, 'USD'),
    totalAdSpend,
    totalAdSpendText: totalAdSpend ? formatAmazonMoney(totalAdSpend, 'USD') : '—',
    hasAdData: top.some((p) => p.adSpend7d > 0),
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
  const value = parseAmazonAmount(amount)
  if (!value) return '—'
  const prefix = currency === 'USD' ? 'US$' : `${currency} `
  return `${prefix}${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

/** 格式化卖家后台指标原文（如 US$1,882.99）为统一两位小数 */
export function formatAmazonMetricValue(value, currency = 'USD') {
  if (value == null || value === '') return '—'
  const num = parseAmazonAmount(value)
  if (num > 0) return formatAmazonMoney(num, currency)
  if (num === 0) return formatAmazonMoney(0, currency)
  const text = String(value).trim()
  return text || '—'
}

export function formatAmazonPercent(value, digits = 1) {
  const num = Number(value)
  if (!Number.isFinite(num) || num <= 0) return '—'
  return `${num.toFixed(digits)}%`
}

export function summarizeAccountSnapshot(metrics = []) {
  const pick = (key) => metrics.find((m) => m.metricKey === key)?.value || ''
  return {
    salesToday: formatAmazonMetricValue(pick('sales_today')),
    adSpendToday: formatAmazonMetricValue(pick('ad_spend_today')),
    adAcosSnapshot: pick('ad_acos_snapshot') || '—',
    paymentBalance: formatAmazonMetricValue(pick('payment_balance')),
    openOrders: pick('open_orders') || '—',
  }
}
