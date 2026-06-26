/** 泰州亿拓户外用品 — 全局 Demo 样本 */

/** 员工端登录身份（与 Temu 运营、运营绑定一致） */
export const EMPLOYEE_PROFILE = { name: '王一鸣', platform: 'Temu', role: 'Temu 运营' }

export const PLATFORMS = [
  { id: 'temu', name: 'Temu', owner: '王一鸣', revenue: 982000, orders: 11080, conversion: 9.4, alerts: 5, trend: 19.5, health: 84, syncStatus: 'syncing' },
  { id: 'aliexpress', name: 'AliExpress', owner: '张强', revenue: 638000, orders: 5390, conversion: 6.1, alerts: 2, trend: 8.2, health: 88, syncStatus: 'connected' },
]

export const ACTIVITIES = [
  { time: '11:20', title: 'Temu 爆款「轻量双人帐篷」日销突破 320 件', type: 'success', desc: '王一鸣已发起全公司通报，建议同步加大官方仓补货。' },
  { time: '10:42', title: 'Temu 官方仓库存低于安全线', type: 'warning', desc: '碳纤维登山杖仅剩 8 天覆盖，建议补货 1,200 件。' },
  { time: '10:15', title: '竞店「松本户外」今日上新 2 款帐篷', type: 'primary', desc: '竞店分析已标记，建议关注定价与差异化。' },
  { time: '09:48', title: 'Temu 2 个 SKU 单件亏损待处理', type: 'danger', desc: '便携燃气炉头、折叠露营椅需调价或下架评估。' },
  { time: '09:20', title: '速卖通户外睡袋系列刊登完成', type: 'primary', desc: '张强完成 86 个 SKU 多语言资料发布。' },
]

export const STAFF = [
  { id: 1, name: '王一鸣', role: 'Temu 运营', platforms: ['Temu'], permissions: ['查看数据', '编辑商品', '库存调整'], status: true },
  { id: 2, name: '李婷', role: 'Temu 运营', platforms: ['Temu'], permissions: ['查看数据', '库存调整'], status: true },
  { id: 3, name: '张强', role: 'AliExpress 运营', platforms: ['AliExpress'], permissions: ['查看数据', '编辑商品'], status: true },
]

export const PERMISSION_OPTIONS = ['查看数据', '编辑商品', '广告投放', '库存调整', '财务利润', '员工管理', 'AI 工具']

export const AI_QUICK_PROMPTS = [
  { label: '今日 Temu 摘要', prompt: '帮我汇总今日 Temu 关键指标与异常项' },
  { label: '库存预警分析', prompt: '分析当前 Temu 库存预警并给出补货优先级' },
  { label: '滞销 SKU 处理', prompt: '哪些 Temu SKU 滞销最严重，如何处理' },
  { label: '竞店上新分析', prompt: '竞店最近上了哪些新品，我们如何应对' },
]

export const AI_EMPLOYEE_PROMPTS = [
  { label: '今日待办', prompt: '帮我整理今日 Temu 运营待办优先级' },
  { label: 'Listing 优化', prompt: '轻量双人帐篷的标题和卖点怎么优化' },
  { label: '补货建议', prompt: '哪些 SKU 需要优先补货到官方仓' },
  { label: '亏损 SKU', prompt: '当前亏损 SKU 应该怎么处理' },
]

export const AI_MOCK_REPLIES = {
  default: '已收到你的请求。Demo 模式下基于亿拓户外 Temu 样本数据回复，正式版将接入真实平台数据。',
  summary: '今日 Temu 汇总：销售额 ¥982,000，订单 11,080 单（+19.5%）。5 条预警待处理：2 个亏损 SKU、3 个滞销 SKU、1 个爆款待补货。建议优先处理碳纤维登山杖补货与亏损 SKU 调价。',
  inventory: '补货优先级：① 轻量双人帐篷（爆款，覆盖 6 天）② 碳纤维登山杖（覆盖 8 天）③ 太阳能露营马灯（覆盖 9 天）。本地仓库存充足，可安排本周内向官方仓发货。',
  slow: '滞销最严重：户外速干裤（47 日未动销）、折叠露营椅（32 日）、露营睡袋（18 日）。建议 45 日+ SKU 清仓，30 日+ 降价促销，15 日+ 加大曝光。',
  competitor: '竞店「松本户外」今日上新 2 款帐篷，「山野装备」防晒冰袖日销激增 96%。建议关注帐篷品类定价，冰袖类可评估是否跟款。',
  listing: '「轻量双人帐篷」建议标题突出：3-4人、全自动、防雨、便携。卖点强调 1.2kg 超轻、快开 30 秒、双层防雨。当前价格 ¥189.9 处于品类中游，可维持。',
  loss: '亏损 SKU：便携燃气炉头（单件亏 ¥2.3）、折叠露营椅（单件亏 ¥1.8）。建议炉头提价至 ¥78 或更换供应商；露营椅可捆绑销售或下架。',
}

export const EMPLOYEE_TASKS = [
  { id: 1, title: 'Temu 爆款双人帐篷官方仓补货 1,800 件', priority: 'high', due: '今天 18:00', status: '进行中' },
  { id: 2, title: '2 个亏损 SKU 调价方案确认', priority: 'high', due: '今天 20:00', status: '待处理' },
  { id: 3, title: '45 日滞销 SKU 清仓方案', priority: 'medium', due: '明天', status: '待处理' },
  { id: 4, title: '竞店松本户外新品对比分析', priority: 'medium', due: '明天', status: '待处理' },
  { id: 5, title: 'LED 头灯 Listing 主图更新', priority: 'low', due: '本周五', status: '待处理' },
]
