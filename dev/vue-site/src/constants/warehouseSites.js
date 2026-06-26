export const WAREHOUSE_SITES_STORAGE_KEY = 'crosshub_warehouse_sites'

/** Demo 分仓（与 Java 种子 wh_site_* 对齐） */
export const WAREHOUSE_SITES_SEED = [
  {
    id: 'wh_site_tz1',
    name: '泰州1号仓',
    code: 'tz1',
    address: '江苏省泰州市海陵区',
    status: true,
    sortOrder: 10,
    createdAt: '2026-06-20 09:00:00',
  },
  {
    id: 'wh_site_tz_post',
    name: '泰州邮政仓',
    code: 'tz_post',
    address: '江苏省泰州市邮政物流园',
    status: true,
    sortOrder: 20,
    createdAt: '2026-06-20 09:00:00',
  },
  {
    id: 'wh_site_ah',
    name: '安徽仓库',
    code: 'ah',
    address: '安徽省合肥市',
    status: true,
    sortOrder: 30,
    createdAt: '2026-06-20 09:00:00',
  },
]

export function warehouseSiteLabel(site) {
  if (!site) return '—'
  return site.name || site.id
}
