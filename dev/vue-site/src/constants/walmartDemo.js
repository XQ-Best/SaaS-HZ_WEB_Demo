/** Walmart 运营 Demo 数据 */

export const WALMART_OPERATOR = { name: '周婷', role: 'Walmart 运营' }

export const WALMART_FULFILLMENT_LABELS = {
  wfs: 'WFS 仓发',
  seller: '自发货',
}

export const WFS_ORDER_STATUSES = ['待拣货', '待发货', '已发货', '已取消']
export const SELLER_ORDER_STATUSES = ['待确认', '待发货', '已发货', '已取消']

export const WFS_STATUS_TYPE = {
  待拣货: 'warning',
  待发货: 'danger',
  已发货: 'success',
  已取消: 'info',
}

export const SELLER_STATUS_TYPE = {
  待确认: 'warning',
  待发货: 'danger',
  已发货: 'success',
  已取消: 'info',
}

export const WALMART_LISTING_ISSUE_TYPES = {
  unpublished: { label: '未发布', type: 'danger' },
  content: { label: '内容错误', type: 'warning' },
  pricing: { label: '价格异常', type: 'warning' },
  inventory: { label: '库存不一致', type: 'info' },
}

export const WALMART_ORDERS_SEED = [
  {
    id: 'wm_order_wfs_1',
    orderNo: 'WM10092837461',
    storeId: 'demo_walmart_1',
    fulfillmentType: 'wfs',
    sku: 'WM-US-001',
    productName: '轻量双人徒步帐篷 4人',
    quantity: 2,
    amount: 159.98,
    currency: 'USD',
    status: '待发货',
    orderedAt: '2026-06-25 08:12:00',
    shipDeadline: '2026-06-25 18:00:00',
  },
  {
    id: 'wm_order_wfs_2',
    orderNo: 'WM10092837462',
    storeId: 'demo_walmart_1',
    fulfillmentType: 'wfs',
    sku: 'WM-US-002',
    productName: '四季露营睡袋 -10℃',
    quantity: 1,
    amount: 49.99,
    currency: 'USD',
    status: '待拣货',
    orderedAt: '2026-06-25 09:45:00',
    shipDeadline: '2026-06-25 18:00:00',
  },
  {
    id: 'wm_order_wfs_3',
    orderNo: 'WM10092837463',
    storeId: 'demo_walmart_1',
    fulfillmentType: 'wfs',
    sku: 'WM-US-003',
    productName: '碳纤维登山杖一对',
    quantity: 3,
    amount: 89.97,
    currency: 'USD',
    status: '已发货',
    orderedAt: '2026-06-25 07:20:00',
    shipDeadline: null,
  },
  {
    id: 'wm_order_seller_1',
    orderNo: 'WM20084729101',
    storeId: 'demo_walmart_1',
    fulfillmentType: 'seller',
    sku: 'WM-US-004',
    productName: 'USB 充电头灯套装',
    quantity: 1,
    amount: 24.99,
    currency: 'USD',
    status: '待确认',
    orderedAt: '2026-06-25 10:05:00',
    shipDeadline: '2026-06-26 23:59:00',
  },
  {
    id: 'wm_order_seller_2',
    orderNo: 'WM20084729102',
    storeId: 'demo_walmart_2',
    fulfillmentType: 'seller',
    sku: 'WM-CA-001',
    productName: '折叠露营椅',
    quantity: 2,
    amount: 79.98,
    currency: 'USD',
    status: '待发货',
    orderedAt: '2026-06-25 06:30:00',
    shipDeadline: '2026-06-26 12:00:00',
  },
  {
    id: 'wm_order_wfs_4',
    orderNo: 'WM10092837464',
    storeId: 'demo_walmart_2',
    fulfillmentType: 'wfs',
    sku: 'WM-CA-002',
    productName: '防水野餐垫',
    quantity: 1,
    amount: 32.99,
    currency: 'USD',
    status: '待发货',
    orderedAt: '2026-06-25 11:18:00',
    shipDeadline: '2026-06-25 18:00:00',
  },
]

export const WALMART_LISTING_ISSUES_SEED = [
  {
    id: 'wm_issue_1',
    storeId: 'demo_walmart_1',
    sku: 'WM-US-005',
    productName: '户外保温壶 1L',
    type: 'unpublished',
    detail: '主图分辨率低于平台要求，商品未发布',
    severity: 'high',
    reportedAt: '2026-06-25 08:00:00',
    resolved: false,
  },
  {
    id: 'wm_issue_2',
    storeId: 'demo_walmart_1',
    sku: 'WM-US-006',
    productName: '便携烧烤架',
    type: 'content',
    detail: '标题含受限词 "best"，需修改后重新提交',
    severity: 'medium',
    reportedAt: '2026-06-25 09:30:00',
    resolved: false,
  },
  {
    id: 'wm_issue_3',
    storeId: 'demo_walmart_1',
    sku: 'WM-US-001',
    productName: '轻量双人徒步帐篷 4人',
    type: 'pricing',
    detail: 'Buy Box 丢失，竞品价格低 8%',
    severity: 'medium',
    reportedAt: '2026-06-25 07:15:00',
    resolved: false,
  },
  {
    id: 'wm_issue_4',
    storeId: 'demo_walmart_2',
    sku: 'WM-CA-003',
    productName: '露营灯串',
    type: 'inventory',
    detail: 'WFS 可售库存与后台不一致，差 12 件',
    severity: 'high',
    reportedAt: '2026-06-25 10:00:00',
    resolved: false,
  },
  {
    id: 'wm_issue_5',
    storeId: 'demo_walmart_2',
    sku: 'WM-CA-004',
    productName: '防潮睡垫',
    type: 'content',
    detail: '属性「材质」缺失，需补充',
    severity: 'low',
    reportedAt: '2026-06-24 16:20:00',
    resolved: true,
  },
]
