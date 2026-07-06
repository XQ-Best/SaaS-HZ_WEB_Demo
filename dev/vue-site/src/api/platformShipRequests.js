import { pushPlatformOrderToWarehouse as pushLocal } from './platformShipRequestsLocal'

export { enrichOrdersWithWarehouseFeedback, enrichOrderWithWarehouseFeedback } from './platformShipRequestsLocal'

/** 平台订单推送 / 催促发货至仓库（Demo：localStorage + 出库单） */
export async function pushPlatformOrderToWarehouse(auth, payload) {
  const result = pushLocal(auth, payload)
  return {
    success: true,
    message: payload.type === 'urge'
      ? `已催促 ${result.warehouseOrder.warehouseName} 发货`
      : `已推送至 ${result.warehouseOrder.warehouseName}，等待仓库审核`,
    data: result,
  }
}
