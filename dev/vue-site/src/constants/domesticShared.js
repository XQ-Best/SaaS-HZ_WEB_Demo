/** 国内电商平台（拼多多 / 抖音 / 视频号）共享枚举 */

export const DOMESTIC_ORDER_STATUSES = ['待处理', '待发货', '已发货', '已取消']

export const DOMESTIC_ORDER_STATUS_TYPE = {
  待处理: 'warning',
  待发货: 'danger',
  已发货: 'success',
  已取消: 'info',
}

export const DOMESTIC_PENDING_STATUSES = new Set(['待处理', '待发货'])

export const DOMESTIC_SHIPPED_STATUSES = new Set(['已发货'])
