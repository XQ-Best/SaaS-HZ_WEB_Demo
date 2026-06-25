/** 员工 AI 办公 — 技能与上下文 Demo 数据 */

export const AI_SKILL_GROUPS = [
  {
    id: 'listing',
    label: 'Listing 优化',
    color: '#165dff',
    skills: [
      {
        id: 'title',
        label: '标题优化',
        desc: '关键词与合规检查',
        prompt: '帮我优化「轻量双人徒步帐篷」的 Listing 标题，突出 3-4 人、防雨、便携卖点',
      },
      {
        id: 'bullet',
        label: '卖点提炼',
        desc: '五点描述与 A+ 思路',
        prompt: '为碳纤维登山杖写 5 条高转化 Bullet Points，面向美国市场',
      },
      {
        id: 'translate',
        label: '多语言润色',
        desc: '英/西/法文案本地化',
        prompt: '将以下露营睡袋卖点翻译并润色为地道英文，避免机翻感',
      },
    ],
  },
  {
    id: 'ops',
    label: '运营决策',
    color: '#14c9c9',
    skills: [
      {
        id: 'priority',
        label: '待办优先级',
        desc: '结合预警排今日序',
        prompt: '根据我负责店铺的待处理预警，帮我排今日工作优先级',
      },
      {
        id: 'restock',
        label: '补货建议',
        desc: '安全库存与发货节奏',
        prompt: '哪些 SKU 需要优先补货到官方仓？给出理由和数量建议',
      },
      {
        id: 'slow',
        label: '滞销处理',
        desc: '清仓 / 降价 / 曝光',
        prompt: '当前滞销最严重的 SKU 有哪些？分别建议怎么处理',
      },
    ],
  },
  {
    id: 'service',
    label: '客服回复',
    color: '#722ed1',
    skills: [
      {
        id: 'review',
        label: '差评回复',
        desc: '专业且可申诉的草稿',
        prompt: '买家给了 2 星差评说帐篷漏水，帮我写一封专业回复草稿',
      },
      {
        id: 'message',
        label: '买家消息',
        desc: '24h 内回复模板',
        prompt: '买家询问订单能否改地址，帮我写简短专业的英文回复',
      },
      {
        id: 'case',
        label: 'Case 说明',
        desc: '平台申诉材料要点',
        prompt: '因物流延迟收到 A-to-Z 索赔，帮我整理申诉要点和证据清单',
      },
    ],
  },
]

export const AI_CONTEXT_HINTS = [
  { label: '待处理预警', value: '5', type: 'warning' },
  { label: '今日订单', value: '128', type: 'primary' },
  { label: '待完成任务', value: '3', type: 'danger' },
]

export const AI_SUGGESTED_PROMPTS = [
  {
    title: '今日工作摘要',
    desc: '汇总负责店铺的订单、预警与任务',
    prompt: '帮我生成本日运营工作摘要，包含待处理预警和优先事项',
  },
  {
    title: '亏损 SKU 诊断',
    desc: '分析原因并给出调价建议',
    prompt: '当前亏损 SKU 应该怎么处理？请给出具体调价或下架建议',
  },
  {
    title: '竞店动态',
    desc: '竞品上新与应对策略',
    prompt: '竞店最近上了哪些新品？我们如何应对',
  },
]

export const AI_EMPLOYEE_WELCOME = (name, platforms) =>
  `你好，${name}。我是 CrossHub AI 助手，已接入你负责的 ${platforms || '运营'} 工作上下文。可以帮你优化 Listing、起草客服回复、分析库存与任务优先级。`

export const AI_EMPLOYEE_MOCK_REPLIES = {
  default:
    '已收到你的请求。Demo 模式下基于亿拓户外样本数据回复；正式版将接入你负责店铺的真实运营数据。',
  summary:
    '**今日工作摘要**\n\n· 待处理预警 5 条：2 个亏损 SKU、2 个补货紧急、1 个 Listing 问题\n· 今日订单 128 单，较昨日 +12%\n· 建议优先：① 碳纤维登山杖补货 ② 亏损 SKU 调价确认 ③ Walmart Listing 主图修复',
  priority:
    '**今日优先级建议**\n\n1. 【高】碳纤维登山杖官方仓补货 — 覆盖仅 6 天，爆款连带风险\n2. 【高】2 个亏损 SKU 调价 — 今日 20:00 前需确认方案\n3. 【中】Walmart 未发布 Listing — 主图分辨率问题\n4. 【中】竞店新品对比分析 — 明日截止\n5. 【低】LED 头灯主图更新 — 本周内完成',
  listing:
    '**标题优化建议**（轻量双人徒步帐篷）\n\n推荐标题：\nLightweight 3-4 Person Camping Tent — Waterproof, Easy Setup, Portable Hiking Tent\n\n要点：前 80 字符放核心词；避免 best / #1 等受限词；Walmart 与 Amazon 可微调副标题。',
  review:
    '**差评回复草稿**\n\nDear Customer,\n\nThank you for your feedback. We\'re sorry the tent did not meet your expectations regarding waterproof performance. We\'d like to offer a replacement or full refund. Please contact us with your order number — your satisfaction is our priority.\n\n— Yituo Outdoor Support',
  restock:
    '**补货优先级**\n\n① 轻量双人帐篷 — 爆款，WFS 覆盖 6 天，建议补 1,800 件\n② 碳纤维登山杖 — 覆盖 8 天，本地仓可发\n③ 太阳能露营灯 — 覆盖 9 天，非紧急但需本周安排',
  slow: '**滞销 SKU 处理**\n\n· 户外速干裤（47 日未动销）→ 清仓 -30%\n· 折叠露营椅（32 日）→ 捆绑促销或降价\n· 露营睡袋（18 日）→ 加大广告曝光 7 天再评估',
  competitor:
    '**竞店动态**\n\n· 松本户外：今日上新 2 款帐篷，定价低我们 8%\n· 山野装备：防晒冰袖日销 +96%\n\n建议：帐篷维持差异化卖点；冰袖类评估是否跟款测款。',
  loss: '**亏损 SKU 方案**\n\n· 便携燃气炉头（单件 -¥2.3）→ 提价至 ¥78 或换供应商\n· 折叠露营椅（单件 -¥1.8）→ 捆绑销售或下架评估',
}
