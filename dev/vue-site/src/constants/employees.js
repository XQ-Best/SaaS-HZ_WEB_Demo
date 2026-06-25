/** 员工绑定 Demo 样本 */
import {
  DTC_PLATFORM_OPTIONS,
  MARKETPLACE_PLATFORM_OPTIONS,
  OTHER_PLATFORM_OPTIONS,
  PLATFORM_OPTION_GROUPS,
} from './platforms'

export { PLATFORM_OPTION_GROUPS }
export const DEMO_EMPLOYEES = [
  {
    id: 'demo_emp_1',
    name: '王一鸣',
    account: 'wangyiming@yituo-outdoor.com',
    password: 'Emp@Demo123',
    role: 'Temu 运营',
    platforms: ['temu'],
    assignedStoreIds: ['demo_temu_1', 'demo_temu_2'],
    phone: '13800138001',
    status: true,
    boundAt: '2026-06-20 09:15:00',
  },
  {
    id: 'demo_emp_2',
    name: '李婷',
    account: 'liting@yituo-outdoor.com',
    password: 'Emp@Demo456',
    role: '仓储主管',
    platforms: ['temu'],
    assignedStoreIds: [],
    phone: '13800138002',
    status: true,
    boundAt: '2026-06-21 10:30:00',
  },
  {
    id: 'demo_emp_3',
    name: '张强',
    account: 'zhangqiang@yituo-outdoor.com',
    password: 'Emp@Demo789',
    role: 'AliExpress 运营',
    platforms: ['aliexpress'],
    assignedStoreIds: ['demo_aliexpress_1', 'demo_aliexpress_2'],
    phone: '13800138003',
    status: true,
    boundAt: '2026-06-22 14:20:00',
  },
  {
    id: 'demo_emp_4',
    name: '陈敏',
    account: 'chenmin@yituo-outdoor.com',
    password: 'Emp@Demo321',
    role: '独立站运营',
    platforms: ['shopify', 'wordpress'],
    assignedStoreIds: ['demo_shopify_1', 'demo_shopify_2', 'demo_wordpress_1'],
    phone: '13800138004',
    status: true,
    boundAt: '2026-06-23 11:00:00',
  },
  {
    id: 'demo_emp_5',
    name: '赵磊',
    account: 'zhaolei@yituo-outdoor.com',
    password: 'Emp@Demo654',
    role: '1688 采购',
    platforms: ['1688'],
    assignedStoreIds: ['demo_1688_1', 'demo_1688_2'],
    phone: '13800138005',
    status: true,
    boundAt: '2026-06-24 08:30:00',
  },
  {
    id: 'demo_emp_6',
    name: '刘洋',
    account: 'liuyang@yituo-outdoor.com',
    password: 'Emp@Demo987',
    role: 'Amazon 运营',
    platforms: ['amazon'],
    assignedStoreIds: ['demo_amazon_1', 'demo_amazon_2'],
    phone: '13800138006',
    status: true,
    boundAt: '2026-06-24 10:00:00',
  },
]

export const PLATFORM_OPTIONS = [
  ...MARKETPLACE_PLATFORM_OPTIONS,
  ...DTC_PLATFORM_OPTIONS.map((item) => ({
    ...item,
    label: `独立站 · ${item.label}`,
  })),
  ...OTHER_PLATFORM_OPTIONS,
]

export const ROLE_OPTIONS = [
  'Temu 运营',
  'AliExpress 运营',
  '1688 采购',
  '独立站运营',
  'Amazon 运营',
  '仓储主管',
  '客服专员',
  '数据分析师',
]

export function platformLabels(platforms) {
  const map = Object.fromEntries(PLATFORM_OPTIONS.map((p) => [p.value, p.label]))
  return (platforms || []).map((p) => map[p] || p).join('、') || '—'
}
