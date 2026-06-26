import { MARKETPLACE_PLATFORM_OPTIONS, DTC_PLATFORM_OPTIONS } from './platforms'

export const WAREHOUSE_ORDER_STORAGE_KEY = 'crosshub_warehouse_orders'

export const ORDER_STATUS_OPTIONS = [
  { value: 'pending_review', label: '待仓库审核', tag: 'warning' },
  { value: 'pending_shipment', label: '待发货', tag: 'success' },
  { value: 'blocked', label: '暂不可发', tag: 'danger' },
  { value: 'shipped', label: '已发货', tag: 'info' },
  { value: 'cancelled', label: '已取消', tag: 'info' },
]

export const ORDER_STATUS_MAP = Object.fromEntries(
  ORDER_STATUS_OPTIONS.map((item) => [item.value, item]),
)

export const SOURCE_TYPE_OPTIONS = [
  { value: 'marketplace', label: '电商平台货' },
  { value: 'b2b', label: 'B 端客户货' },
]

export const MARKETPLACE_SOURCE_OPTIONS = [
  ...MARKETPLACE_PLATFORM_OPTIONS.map((item) => ({
    value: item.value,
    label: item.label,
  })),
  ...DTC_PLATFORM_OPTIONS.map((item) => ({
    value: item.value,
    label: item.label,
  })),
]

export const ATTACHMENT_ACCEPT = '.pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg'

/** 箱唛、标签等（选填） */
export const MARK_LABEL_ACCEPT = '.pdf,.png,.jpg,.jpeg,.doc,.docx,.xls,.xlsx'

export const WAREHOUSE_ORDERS_SEED = [
  {
    id: 'wh_ord_seed_1',
    orderNo: 'WH20260624001',
    status: 'pending_shipment',
    warehouseId: 'wh_site_tz1',
    warehouseName: '泰州1号仓',
    items: [
      { id: 'li_1', productName: '户外折叠椅 · 黑色', sku: 'YT-CHAIR-BK', quantity: 200, unit: '件' },
      { id: 'li_2', productName: '便携露营灯', sku: 'YT-LAMP-01', quantity: 150, unit: '件' },
    ],
    remark: 'Temu 爆款补货，请优先安排 WFS 仓出库。',
    sourceType: 'marketplace',
    sourcePlatform: 'temu',
    sourceLabel: 'Temu · 亿拓户外旗舰店',
    b2bCustomerName: '',
    attachments: [
      {
        id: 'att_1',
        name: 'Temu补货清单.xlsx',
        size: 48200,
        mime: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        uploadedAt: '2026-06-24 09:15:00',
      },
    ],
    cartonMarks: [
      {
        id: 'cm_1',
        name: '外箱唛-FBA.pdf',
        size: 156000,
        mime: 'application/pdf',
        uploadedAt: '2026-06-24 09:14:00',
      },
    ],
    labels: [
      {
        id: 'lb_1',
        name: 'FNSKU标签.pdf',
        size: 89000,
        mime: 'application/pdf',
        uploadedAt: '2026-06-24 09:14:00',
      },
    ],
    submittedByRole: 'employee',
    submittedById: 'demo_emp_1',
    submittedByName: '王一鸣',
    submittedAt: '2026-06-24 09:12:00',
    warehouseReview: {
      canShip: true,
      estimatedShipAt: '2026-06-26',
      missingMaterials: '',
      packagingNotes: '需加贴 FBA 标签，外箱缠膜',
      extraOrderNotes: '',
      reviewRemark: '库存充足，预计 6/26 下午可出库。',
      reviewedById: 'wh_user_1',
      reviewedByName: '张仓管',
      reviewedAt: '2026-06-24 14:30:00',
    },
    updatedAt: '2026-06-24 14:30:00',
  },
  {
    id: 'wh_ord_seed_2',
    orderNo: 'WH20260625002',
    status: 'pending_review',
    warehouseId: 'wh_site_tz_post',
    warehouseName: '泰州邮政仓',
    items: [
      { id: 'li_3', productName: '定制 LOGO 帆布袋', sku: 'B2B-BAG-LOGO', quantity: 5000, unit: '件' },
    ],
    remark: 'B 端客户「杭州野趣贸易」首批大货，附合同与包装设计稿。',
    sourceType: 'b2b',
    sourcePlatform: '',
    sourceLabel: 'B 端 · 杭州野趣贸易',
    b2bCustomerName: '杭州野趣贸易有限公司',
    attachments: [
      {
        id: 'att_2',
        name: '采购合同.pdf',
        size: 256000,
        mime: 'application/pdf',
        uploadedAt: '2026-06-25 11:20:00',
      },
      {
        id: 'att_3',
        name: '包装设计稿.docx',
        size: 128000,
        mime: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        uploadedAt: '2026-06-25 11:20:00',
      },
    ],
    submittedByRole: 'boss',
    submittedById: 'boss_admin',
    submittedByName: '企业管理员',
    submittedAt: '2026-06-25 11:18:00',
    warehouseReview: null,
    updatedAt: '2026-06-25 11:18:00',
  },
  {
    id: 'wh_ord_seed_3',
    orderNo: 'WH20260625003',
    status: 'blocked',
    warehouseId: 'wh_site_ah',
    warehouseName: '安徽仓库',
    items: [
      { id: 'li_4', productName: 'Amazon 专用外箱（大号）', sku: 'AMZ-BOX-L', quantity: 800, unit: '箱' },
    ],
    remark: 'Amazon FBA 补货，需按 ASIN 分箱清单出库。',
    sourceType: 'marketplace',
    sourcePlatform: 'amazon',
    sourceLabel: 'Amazon · US-Store-01',
    b2bCustomerName: '',
    attachments: [
      {
        id: 'att_4',
        name: 'FBA分箱清单.xlsx',
        size: 64000,
        mime: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        uploadedAt: '2026-06-25 15:40:00',
      },
    ],
    submittedByRole: 'employee',
    submittedById: 'demo_emp_6',
    submittedByName: '刘洋',
    submittedAt: '2026-06-25 15:38:00',
    warehouseReview: {
      canShip: false,
      estimatedShipAt: '',
      missingMaterials: '大号外箱库存不足，仅剩 120 箱',
      packagingNotes: '需追加定制 FBA 标签纸',
      extraOrderNotes: '已向包材供应商追加订购 1000 箱，预计 6/28 到货',
      reviewRemark: '暂不可发，缺外箱与标签，已启动追加订货。',
      reviewedById: 'wh_user_1',
      reviewedByName: '张仓管',
      reviewedAt: '2026-06-25 16:05:00',
    },
    updatedAt: '2026-06-25 16:05:00',
  },
]
