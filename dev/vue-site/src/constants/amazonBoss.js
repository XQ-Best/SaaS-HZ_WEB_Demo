/** Amazon 管理员端 — 产品 TOP20、ACOS 阈值、订单发货 Demo */

export const ACOS_THRESHOLDS = {
  good: 20,
  warning: 35,
  danger: 50,
}

export const ACOS_LEVEL_META = {
  good: { label: '健康', type: 'success' },
  normal: { label: '正常', type: 'info' },
  warning: { label: '偏高', type: 'warning' },
  danger: { label: '过高', type: 'danger' },
}

export const OUTBOUND_FULFILLMENT = {
  fba: { label: 'FBA', type: 'primary' },
  fbm: { label: '自发货', type: 'warning' },
}

export const OUTBOUND_STATUS = {
  pending: { label: '待发货', type: 'danger' },
  pending_write: { label: '写回中', type: 'warning' },
  packed: { label: '待揽收', type: 'warning' },
  shipped: { label: '已发货', type: 'success' },
  cancelled: { label: '已取消', type: 'info' },
}

const PRODUCT_CATALOG = [
  { asin: 'B08TENT001', sku: 'AMZ-001', name: '轻量双人徒步帐篷 3-4人' },
  { asin: 'B08BAG002', sku: 'AMZ-002', name: '四季露营睡袋 -10℃' },
  { asin: 'B08POLE003', sku: 'AMZ-003', name: '碳纤维登山杖一对' },
  { asin: 'B08LAMP004', sku: 'AMZ-004', name: 'USB 充电头灯套装' },
  { asin: 'B08CHAIR005', sku: 'AMZ-005', name: '折叠露营椅' },
  { asin: 'B08MAT006', sku: 'AMZ-006', name: '防水野餐垫 2x2m' },
  { asin: 'B08GRILL007', sku: 'AMZ-007', name: '便携烧烤架' },
  { asin: 'B08BOTTLE008', sku: 'AMZ-008', name: '户外保温壶 1L' },
  { asin: 'B08LIGHT009', sku: 'AMZ-009', name: '露营灯串 10m' },
  { asin: 'B08PAD010', sku: 'AMZ-010', name: '防潮睡垫' },
  { asin: 'B08PACK011', sku: 'AMZ-011', name: '防水收纳包 40L' },
  { asin: 'B08STOVE012', sku: 'AMZ-012', name: '迷你炉头套装' },
  { asin: 'B08ROPE013', sku: 'AMZ-013', name: '反光营地绳' },
  { asin: 'B08FILTER014', sku: 'AMZ-014', name: '便携滤水器' },
  { asin: 'B08GLOVE015', sku: 'AMZ-015', name: '户外保暖手套' },
  { asin: 'B08HAT016', sku: 'AMZ-016', name: '防晒渔夫帽' },
  { asin: 'B08SOCK017', sku: 'AMZ-017', name: '徒步羊毛袜 3双装' },
  { asin: 'B08TOOL018', sku: 'AMZ-018', name: '多功能露营工具钳' },
  { asin: 'B08BAG019', sku: 'AMZ-019', name: '折叠水袋 3L' },
  { asin: 'B08TARP020', sku: 'AMZ-020', name: '天幕遮阳棚 3x3m' },
  { asin: 'B08EU021', sku: 'AMZ-EU-01', name: 'EU 轻量帐篷 2人' },
  { asin: 'B08EU022', sku: 'AMZ-EU-02', name: 'EU 折叠椅 Pro' },
]

/** 预设 ACOS 分布：部分偏高供 Demo 预警 */
const ACOS_PRESETS = [
  18, 22, 25, 28, 31, 34, 38, 42, 45, 19, 21, 26, 29, 33, 36, 41, 48, 23, 27, 32, 24, 37,
]

function buildProductMetrics(storeId, index) {
  const product = PRODUCT_CATALOG[index % PRODUCT_CATALOG.length]
  const acos = ACOS_PRESETS[index % ACOS_PRESETS.length]
  const orders7d = 12 + (index % 8) * 3
  const avgPrice = 28 + (index % 6) * 12
  const revenue7d = Number((orders7d * avgPrice).toFixed(2))
  const adSpend7d = Number(((revenue7d * acos) / 100).toFixed(2))
  const sessions7d = orders7d * (8 + (index % 5))
  const conversionRate = Number(((orders7d / sessions7d) * 100).toFixed(2))
  const unitsOnHand = 40 + (index % 10) * 15

  return {
    id: `amz_prod_${storeId}_${index + 1}`,
    storeId,
    asin: product.asin,
    sku: product.sku,
    productName: product.name,
    orders7d,
    revenue7d,
    adSpend7d,
    acos,
    tacos: Number((acos * (0.85 + (index % 3) * 0.05)).toFixed(1)),
    sessions7d,
    conversionRate,
    unitsOnHand,
    profitMargin: Number((22 - acos * 0.35 + (index % 4)).toFixed(1)),
    currency: storeId.includes('eu') ? 'EUR' : 'USD',
    rank: index + 1,
  }
}

export const TOP_PRODUCTS_SEED = [
  ...Array.from({ length: 20 }, (_, i) => buildProductMetrics('demo_amazon_1', i)),
  ...Array.from({ length: 12 }, (_, i) => buildProductMetrics('demo_amazon_2', i)),
]

export const OUTBOUND_ORDERS_SEED = [
  {
    id: 'out_1',
    storeId: 'demo_amazon_1',
    orderNo: '114-2847561-9283746',
    asin: 'B08TENT001',
    sku: 'AMZ-001',
    productName: '轻量双人徒步帐篷 3-4人',
    quantity: 1,
    fulfillmentType: 'fbm',
    status: 'pending',
    amount: 89.99,
    currency: 'USD',
    orderedAt: '2026-06-25 07:42:00',
    shipDeadline: '2026-06-25 23:59:00',
    buyerRegion: 'US-CA',
  },
  {
    id: 'out_2',
    storeId: 'demo_amazon_1',
    orderNo: '114-9182736-4528190',
    asin: 'B08POLE003',
    sku: 'AMZ-003',
    productName: '碳纤维登山杖一对',
    quantity: 2,
    fulfillmentType: 'fba',
    status: 'pending',
    amount: 59.98,
    currency: 'USD',
    orderedAt: '2026-06-25 08:15:00',
    shipDeadline: '2026-06-25 18:00:00',
    buyerRegion: 'US-TX',
  },
  {
    id: 'out_3',
    storeId: 'demo_amazon_1',
    orderNo: '114-5566778-3344556',
    asin: 'B08LAMP004',
    sku: 'AMZ-004',
    productName: 'USB 充电头灯套装',
    quantity: 1,
    fulfillmentType: 'fbm',
    status: 'packed',
    amount: 24.99,
    currency: 'USD',
    orderedAt: '2026-06-25 06:30:00',
    shipDeadline: '2026-06-25 20:00:00',
    buyerRegion: 'US-NY',
  },
  {
    id: 'out_4',
    storeId: 'demo_amazon_1',
    orderNo: '114-1122334-5566778',
    asin: 'B08BAG002',
    sku: 'AMZ-002',
    productName: '四季露营睡袋 -10℃',
    quantity: 1,
    fulfillmentType: 'fba',
    status: 'shipped',
    amount: 49.99,
    currency: 'USD',
    orderedAt: '2026-06-25 05:00:00',
    shipDeadline: null,
    buyerRegion: 'US-FL',
    trackingNo: 'TBA1234567890',
  },
  {
    id: 'out_5',
    storeId: 'demo_amazon_1',
    orderNo: '114-9988776-1122334',
    asin: 'B08GRILL007',
    sku: 'AMZ-007',
    productName: '便携烧烤架',
    quantity: 1,
    fulfillmentType: 'fbm',
    status: 'pending',
    amount: 39.99,
    currency: 'USD',
    orderedAt: '2026-06-25 09:20:00',
    shipDeadline: '2026-06-26 12:00:00',
    buyerRegion: 'US-WA',
  },
  {
    id: 'out_6',
    storeId: 'demo_amazon_2',
    orderNo: '171-4455667-7788990',
    asin: 'B08EU021',
    sku: 'AMZ-EU-01',
    productName: 'EU 轻量帐篷 2人',
    quantity: 1,
    fulfillmentType: 'fba',
    status: 'pending',
    amount: 79.99,
    currency: 'EUR',
    orderedAt: '2026-06-25 08:00:00',
    shipDeadline: '2026-06-25 23:59:00',
    buyerRegion: 'DE',
  },
  {
    id: 'out_7',
    storeId: 'demo_amazon_2',
    orderNo: '171-2233445-6677889',
    asin: 'B08EU022',
    sku: 'AMZ-EU-02',
    productName: 'EU 折叠椅 Pro',
    quantity: 2,
    fulfillmentType: 'fbm',
    status: 'pending',
    amount: 69.98,
    currency: 'EUR',
    orderedAt: '2026-06-25 10:10:00',
    shipDeadline: '2026-06-26 18:00:00',
    buyerRegion: 'FR',
  },
]
