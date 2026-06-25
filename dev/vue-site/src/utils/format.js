export function formatMoney(value) {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    maximumFractionDigits: 0,
  }).format(value)
}

export function formatTrend(value) {
  const prefix = value >= 0 ? '+' : ''
  return `${prefix}${value}%`
}

export function formatMoneyDecimal(value) {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

export function formatPercent(value, digits = 1) {
  const prefix = value >= 0 ? '+' : ''
  return `${prefix}${value.toFixed(digits)}%`
}
