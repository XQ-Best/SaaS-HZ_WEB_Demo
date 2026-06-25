import { WALMART_LISTING_ISSUE_TYPES } from '@/constants/walmartDemo'
import { formatMoney, formatMoneyDecimal } from '@/utils/format'

const WFS_PENDING = new Set(['待拣货', '待发货'])
const SELLER_PENDING = new Set(['待确认', '待发货'])

export function summarizeWalmartOrders(orders = []) {
  const wfsOrders = orders.filter((o) => o.fulfillmentType === 'wfs')
  const sellerOrders = orders.filter((o) => o.fulfillmentType === 'seller')
  const wfsPending = wfsOrders.filter((o) => WFS_PENDING.has(o.status)).length
  const sellerPending = sellerOrders.filter((o) => SELLER_PENDING.has(o.status)).length
  const totalAmount = orders.reduce((sum, o) => sum + (o.amount || 0), 0)

  return {
    total: orders.length,
    wfsTotal: wfsOrders.length,
    sellerTotal: sellerOrders.length,
    wfsPending,
    sellerPending,
    pending: wfsPending + sellerPending,
    totalAmount,
    totalAmountText: formatMoney(totalAmount),
  }
}

export function summarizeWalmartListings(issues = []) {
  const openItems = issues.filter((item) => !item.resolved)
  const high = openItems.filter((item) => item.severity === 'high').length
  return {
    total: issues.length,
    open: openItems.length,
    high,
    resolved: issues.filter((item) => item.resolved).length,
  }
}

export function summarizeWalmartByStore(orders, issues, stores = []) {
  return stores.map((store) => {
    const storeOrders = orders.filter((o) => o.storeId === store.id)
    const storeIssues = issues.filter((i) => i.storeId === store.id)
    return {
      store,
      orders: summarizeWalmartOrders(storeOrders),
      listings: summarizeWalmartListings(storeIssues),
    }
  })
}

export function enrichListingIssue(issue) {
  const meta = WALMART_LISTING_ISSUE_TYPES[issue.type] || { label: issue.type, type: 'info' }
  return {
    ...issue,
    typeLabel: meta.label,
    typeTag: meta.type,
  }
}

export function formatWalmartAmount(amount, currency = 'USD') {
  return `${formatMoneyDecimal(amount)} ${currency}`
}
