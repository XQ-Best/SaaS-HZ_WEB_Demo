import { PLATFORM_ORDER_STORAGE_KEYS } from '@/constants/platformShipRequests'
import { statusLabel } from '@/utils/warehouseOrders'

const ALIBABA1688_STORAGE_KEY = 'crosshub_1688_demo'

function loadDomesticState(storageKey) {
  try {
    const raw = localStorage.getItem(storageKey)
    return raw ? JSON.parse(raw) : { date: '', syncedAt: '', items: [] }
  } catch {
    return { date: '', syncedAt: '', items: [] }
  }
}

function saveDomesticState(storageKey, state) {
  localStorage.setItem(storageKey, JSON.stringify(state))
}

export function updateDomesticPlatformOrder(platformKey, orderId, patch) {
  const storageKey = PLATFORM_ORDER_STORAGE_KEYS[platformKey]
  if (!storageKey) throw new Error('不支持的平台')

  const state = loadDomesticState(storageKey)
  const index = state.items.findIndex((item) => item.id === orderId)
  if (index === -1) throw new Error('平台订单不存在')

  state.items[index] = { ...state.items[index], ...patch }
  saveDomesticState(storageKey, state)
  return state.items[index]
}

export function update1688PlatformOrder(orderId, patch) {
  try {
    const raw = localStorage.getItem(ALIBABA1688_STORAGE_KEY)
    const data = raw ? JSON.parse(raw) : { purchaseOrders: [], supplierAlerts: [] }
    const index = data.purchaseOrders.findIndex((item) => item.id === orderId)
    if (index === -1) throw new Error('采购单不存在')

    data.purchaseOrders[index] = { ...data.purchaseOrders[index], ...patch }
    localStorage.setItem(ALIBABA1688_STORAGE_KEY, JSON.stringify(data))
    return data.purchaseOrders[index]
  } catch (err) {
    throw err instanceof Error ? err : new Error('采购单更新失败')
  }
}

export function summarizeWarehouseFeedback(warehouseOrder) {
  const review = warehouseOrder?.warehouseReview
  if (!review) return ''

  if (warehouseOrder.status === 'shipped') return '仓库已发货'
  if (warehouseOrder.status === 'cancelled') return '出库单已取消'
  if (warehouseOrder.status === 'blocked') {
    const parts = ['暂不可发']
    if (review.missingMaterials) parts.push(review.missingMaterials)
    if (review.reviewRemark) parts.push(review.reviewRemark)
    return parts.join(' · ')
  }
  if (warehouseOrder.status === 'pending_shipment') {
    if (review.releasedAt) {
      return review.estimatedShipAt
        ? `已补货可发，预计 ${review.estimatedShipAt}`
        : '已补货，确认可发货'
    }
    if (review.estimatedShipAt) return `可发货，预计 ${review.estimatedShipAt}`
    return review.reviewRemark || '仓库确认可发货'
  }
  return review.reviewRemark || statusLabel(warehouseOrder.status)
}

export function buildWarehouseFeedbackPatch(warehouseOrder) {
  if (!warehouseOrder) return null

  const review = warehouseOrder.warehouseReview
  const patch = {
    warehouseStatus: warehouseOrder.status,
    warehouseOrderNo: warehouseOrder.orderNo,
    warehouseName: warehouseOrder.warehouseName,
    warehouseFeedbackSummary: summarizeWarehouseFeedback(warehouseOrder),
  }

  if (review) {
    patch.warehouseReviewAt = review.reviewedAt || ''
    patch.warehouseReviewBy = review.reviewedByName || ''
    patch.warehouseEstimatedShipAt = review.estimatedShipAt || ''
    patch.warehouseMissingMaterials = review.missingMaterials || ''
    patch.warehousePackagingNotes = review.packagingNotes || ''
    patch.warehouseExtraOrderNotes = review.extraOrderNotes || ''
    patch.warehouseReviewRemark = review.reviewRemark || ''
    patch.warehouseReleaseRemark = review.releaseRemark || ''
    patch.warehouseReleasedAt = review.releasedAt || ''
    patch.warehouseReleasedBy = review.releasedByName || ''
  }

  return patch
}

/** 仓管审批/发货后，回写关联的平台订单 */
export function syncPlatformOrderFromWarehouseOrder(warehouseOrder) {
  if (!warehouseOrder?.fromPlatformOrder || !warehouseOrder.platformOrderId) return null

  const platformKey = warehouseOrder.sourcePlatform
  const patch = buildWarehouseFeedbackPatch(warehouseOrder)
  if (!patch) return null

  if (platformKey === '1688') {
    return update1688PlatformOrder(warehouseOrder.platformOrderId, patch)
  }
  if (PLATFORM_ORDER_STORAGE_KEYS[platformKey]) {
    return updateDomesticPlatformOrder(platformKey, warehouseOrder.platformOrderId, patch)
  }
  return null
}
