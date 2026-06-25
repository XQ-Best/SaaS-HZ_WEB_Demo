/** 独立站 Demo 数据种子与生成模板 */

export const DTC_STORE_META_SEED = {
  demo_shopify_1: { domain: 'www.yituo-outdoor.com', currency: 'USD' },
  demo_shopify_2: { domain: 'eu.yituo-outdoor.com', currency: 'EUR' },
  demo_wordpress_1: { domain: 'blog.yituo-outdoor.com', currency: '—' },
}

export const DTC_PRODUCTS_SEED = [
  { sku: 'DTC-001', storeId: 'demo_shopify_1', name: '轻量双人徒步帐篷', category: '帐篷', price: 89.9, cost: 38, stock: 420, dailyOrders: 28, dailyViews: 1860, conversionRate: 1.51, daysWithoutSale: 0 },
  { sku: 'DTC-002', storeId: 'demo_shopify_1', name: '四季露营睡袋', category: '睡袋', price: 59.9, cost: 24, stock: 680, dailyOrders: 18, dailyViews: 920, conversionRate: 1.96, daysWithoutSale: 2 },
  { sku: 'DTC-003', storeId: 'demo_shopify_1', name: '碳纤维登山杖', category: '登山杖', price: 39.9, cost: 16, stock: 1200, dailyOrders: 42, dailyViews: 2100, conversionRate: 2.0, daysWithoutSale: 0 },
  { sku: 'DTC-004', storeId: 'demo_shopify_1', name: 'USB 充电头灯', category: '户外照明', price: 24.9, cost: 9, stock: 890, dailyOrders: 35, dailyViews: 1580, conversionRate: 2.22, daysWithoutSale: 0 },
  { sku: 'DTC-005', storeId: 'demo_shopify_1', name: '折叠露营椅', category: '运动配件', price: 45.0, cost: 42, stock: 310, dailyOrders: 2, dailyViews: 180, conversionRate: 1.11, daysWithoutSale: 28 },
  { sku: 'DTC-006', storeId: 'demo_shopify_2', name: '防水冲锋衣', category: '户外服饰', price: 79.9, cost: 35, stock: 540, dailyOrders: 12, dailyViews: 760, conversionRate: 1.58, daysWithoutSale: 5 },
  { sku: 'DTC-007', storeId: 'demo_shopify_2', name: '太阳能露营灯', category: '户外照明', price: 34.9, cost: 14, stock: 95, dailyOrders: 22, dailyViews: 1100, conversionRate: 2.0, daysWithoutSale: 0 },
  { sku: 'DTC-008', storeId: 'demo_shopify_2', name: '便携燃气炉头', category: '露营炊具', price: 49.9, cost: 48, stock: 220, dailyOrders: 1, dailyViews: 95, conversionRate: 1.05, daysWithoutSale: 35 },
  { sku: 'DTC-009', storeId: 'demo_wordpress_1', name: '户外露营完全指南（电子书）', category: '数字内容', price: 19.9, cost: 2, stock: 9999, dailyOrders: 8, dailyViews: 620, conversionRate: 1.29, daysWithoutSale: 0 },
  { sku: 'DTC-010', storeId: 'demo_wordpress_1', name: 'WooCommerce 联名睡袋', category: '睡袋', price: 69.9, cost: 28, stock: 180, dailyOrders: 6, dailyViews: 340, conversionRate: 1.76, daysWithoutSale: 3 },
  { sku: 'DTC-011', storeId: 'demo_wordpress_1', name: '品牌故事合集（会员专享）', category: '会员内容', price: 9.9, cost: 1, stock: 9999, dailyOrders: 14, dailyViews: 880, conversionRate: 1.59, daysWithoutSale: 0 },
]

export const DTC_CAMPAIGNS_SEED = [
  { id: 'camp_demo_shopify_1_1', name: '春季帐篷促销', storeId: 'demo_shopify_1', status: '进行中', budget: 3000, spent: 1860, orders: 68, roas: 3.2 },
  { id: 'camp_demo_shopify_1_2', name: '新品头灯首发', storeId: 'demo_shopify_1', status: '已结束', budget: 800, spent: 800, orders: 42, roas: 4.5 },
  { id: 'camp_demo_shopify_1_3', name: '弃单召回邮件', storeId: 'demo_shopify_1', status: '进行中', budget: 200, spent: 120, orders: 18, roas: 6.8 },
  { id: 'camp_demo_shopify_2_1', name: '欧洲站清仓', storeId: 'demo_shopify_2', status: '进行中', budget: 1500, spent: 920, orders: 24, roas: 2.1 },
  { id: 'camp_demo_wordpress_1_1', name: '露营内容专栏推广', storeId: 'demo_wordpress_1', status: '进行中', budget: 600, spent: 380, orders: 32, roas: 2.8 },
  { id: 'camp_demo_wordpress_1_2', name: '会员订阅增长计划', storeId: 'demo_wordpress_1', status: '进行中', budget: 300, spent: 210, orders: 45, roas: 5.1 },
]

export const DTC_TRAFFIC_TEMPLATE = [
  { source: 'Google 广告', visits: 4280, orders: 86, conversion: 2.01, spend: 1280 },
  { source: 'Facebook 广告', visits: 3120, orders: 52, conversion: 1.67, spend: 960 },
  { source: '自然搜索', visits: 2860, orders: 48, conversion: 1.68, spend: 0 },
  { source: '邮件营销', visits: 980, orders: 38, conversion: 3.88, spend: 120 },
  { source: '直接访问', visits: 1540, orders: 22, conversion: 1.43, spend: 0 },
]

export const DTC_PRODUCT_TEMPLATES = {
  shopify: [
    { name: '轻量双人徒步帐篷', category: '帐篷', price: 89.9, cost: 38, stock: 420, dailyOrders: 28, dailyViews: 1860, conversionRate: 1.51, daysWithoutSale: 0 },
    { name: '四季露营睡袋', category: '睡袋', price: 59.9, cost: 24, stock: 680, dailyOrders: 18, dailyViews: 920, conversionRate: 1.96, daysWithoutSale: 2 },
    { name: '碳纤维登山杖', category: '登山杖', price: 39.9, cost: 16, stock: 1200, dailyOrders: 42, dailyViews: 2100, conversionRate: 2.0, daysWithoutSale: 0 },
    { name: 'USB 充电头灯', category: '户外照明', price: 24.9, cost: 9, stock: 890, dailyOrders: 35, dailyViews: 1580, conversionRate: 2.22, daysWithoutSale: 0 },
    { name: '折叠露营椅', category: '运动配件', price: 45.0, cost: 42, stock: 310, dailyOrders: 2, dailyViews: 180, conversionRate: 1.11, daysWithoutSale: 28 },
  ],
  wordpress: [
    { name: '户外露营完全指南（电子书）', category: '数字内容', price: 19.9, cost: 2, stock: 9999, dailyOrders: 8, dailyViews: 620, conversionRate: 1.29, daysWithoutSale: 0 },
    { name: 'WooCommerce 联名睡袋', category: '睡袋', price: 69.9, cost: 28, stock: 180, dailyOrders: 6, dailyViews: 340, conversionRate: 1.76, daysWithoutSale: 3 },
    { name: '品牌故事合集（会员专享）', category: '会员内容', price: 9.9, cost: 1, stock: 9999, dailyOrders: 14, dailyViews: 880, conversionRate: 1.59, daysWithoutSale: 0 },
  ],
}

export const DTC_CAMPAIGN_TEMPLATES = {
  shopify: [
    { name: '新品首发推广', status: '进行中', budget: 2500, spent: 1620, orders: 54, roas: 3.1 },
    { name: '季节性促销', status: '进行中', budget: 1800, spent: 980, orders: 36, roas: 2.4 },
    { name: '弃单召回邮件', status: '已结束', budget: 400, spent: 400, orders: 22, roas: 5.2 },
  ],
  wordpress: [
    { name: '内容专栏推广', status: '进行中', budget: 600, spent: 380, orders: 32, roas: 2.8 },
    { name: '会员订阅增长', status: '进行中', budget: 300, spent: 210, orders: 45, roas: 5.1 },
  ],
}

export const DTC_TRAFFIC_WORDPRESS_TEMPLATE = [
  { source: 'Google 搜索', visits: 2180, orders: 42, conversion: 1.93, spend: 680 },
  { source: '社交媒体', visits: 1560, orders: 28, conversion: 1.79, spend: 420 },
  { source: '自然搜索', visits: 3240, orders: 52, conversion: 1.61, spend: 0 },
  { source: 'Newsletter', visits: 860, orders: 36, conversion: 4.19, spend: 80 },
  { source: '直接访问', visits: 1120, orders: 18, conversion: 1.61, spend: 0 },
]
