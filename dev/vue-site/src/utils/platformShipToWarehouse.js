import { DOMESTIC_PENDING_STATUSES } from '@/constants/domesticShared'
import { ALIBABA1688_SHIPPABLE_STATUSES, SHIP_REQUEST_TYPES } from '@/constants/platformShipRequests'
import { statusLabel } from '@/utils/warehouseOrders'

export function isDomesticOrderShippable(order) {
  if (!order) return false
  return DOMESTIC_PENDING_STATUSES.has(order.status)
}

export function is1688OrderShippable(order) {
  if (!order) return false
  return ALIBABA1688_SHIPPABLE_STATUSES.has(order.status)
}

export function canPushPlatformOrder(order, kind = 'domestic') {
  if (kind === '1688') return is1688OrderShippable(order) && !order.warehouseOrderId
  return isDomesticOrderShippable(order) && !order.warehouseOrderId
}

export function canUrgePlatformOrder(order) {
  if (!order?.warehouseOrderId) return false
  if (order.warehouseStatus === 'shipped' || order.warehouseStatus === 'cancelled') return false
  return true
}

export function shipRequestMeta(order) {
  if (!order?.warehouseOrderId) return null
  const type = order.shipUrgeCount > 0 ? 'urge' : order.shipRequestType || 'push'
  const meta = SHIP_REQUEST_TYPES[type] || SHIP_REQUEST_TYPES.push
  const hasFeedback = Boolean(
    order.warehouseFeedbackSummary
    || order.warehouseReviewRemark
    || order.warehouseMissingMaterials,
  )
  return {
    ...meta,
    warehouseName: order.warehouseName || '—',
    warehouseOrderNo: order.warehouseOrderNo || '—',
    warehouseStatus: order.warehouseStatus,
    warehouseStatusLabel: statusLabel(order.warehouseStatus),
    urgeCount: order.shipUrgeCount || 0,
    feedbackSummary: order.warehouseFeedbackSummary || '',
    hasFeedback,
    feedbackDetail: [
      order.warehouseFeedbackSummary,
      order.warehouseMissingMaterials ? `缺料：${order.warehouseMissingMaterials}` : '',
      order.warehouseEstimatedShipAt ? `预计出库：${order.warehouseEstimatedShipAt}` : '',
      order.warehouseReviewRemark ? `备注：${order.warehouseReviewRemark}` : '',
      order.warehouseReleaseRemark ? `补货说明：${order.warehouseReleaseRemark}` : '',
      order.warehouseReviewBy && order.warehouseReviewAt
        ? `${order.warehouseReviewBy} · ${order.warehouseReviewAt}`
        : '',
    ].filter(Boolean).join('\n'),
  }
}

export function buildWarehousePayloadFromDomesticOrder(order, platformKey, storeName, { warehouseId, type, remark }) {
  const platformLabel = platformKey === 'pdd' ? '拼多多' : platformKey === 'douyin' ? '抖音' : platformKey === 'channels' ? '视频号' : platformKey
  const actionLabel = type === 'urge' ? '催促发货' : '推送发货'
  return {
    warehouseId,
    sourceType: 'marketplace',
    sourcePlatform: platformKey,
    sourceStoreName: storeName,
    fromPlatformOrder: true,
    platformOrderId: order.id,
    platformOrderNo: order.orderNo,
    platformStoreId: order.storeId,
    shipRequestType: type,
    remark: [
      `[${actionLabel}] ${platformLabel} 订单 ${order.orderNo}`,
      order.shipDeadline ? `发货截止：${order.shipDeadline}` : '',
      remark || '',
    ].filter(Boolean).join('\n'),
    items: [
      {
        id: `li_${order.id}`,
        productName: order.productName,
        sku: order.sku || '',
        quantity: Number(order.quantity) || 1,
        unit: '件',
      },
    ],
    attachments: [],
    cartonMarks: [],
    labels: [],
  }
}

export function buildWarehousePayloadFrom1688Order(order, storeName, { warehouseId, type, remark }) {
  const actionLabel = type === 'urge' ? '催促发货' : '推送发货'
  return {
    warehouseId,
    sourceType: 'marketplace',
    sourcePlatform: '1688',
    sourceStoreName: storeName,
    fromPlatformOrder: true,
    platformOrderId: order.id,
    platformOrderNo: order.orderNo,
    platformStoreId: order.storeId,
    shipRequestType: type,
    remark: [
      `[${actionLabel}] 1688 采购单 ${order.orderNo}`,
      order.linkedPlatform ? `关联销售平台：${order.linkedPlatform}` : '',
      order.expectedShipAt ? `预计供应商发货：${order.expectedShipAt}` : '',
      remark || '',
    ].filter(Boolean).join('\n'),
    items: [
      {
        id: `li_${order.id}`,
        productName: order.productName,
        sku: order.sku || '',
        quantity: Number(order.quantity) || 1,
        unit: '件',
      },
    ],
    attachments: [],
    cartonMarks: [],
    labels: [],
  }
}
