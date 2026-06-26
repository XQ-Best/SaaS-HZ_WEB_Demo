/** 仓库端口 Demo 账号 */
export const WAREHOUSE_USERS = [
  {
    id: 'wh_user_1',
    name: '张仓管',
    account: 'warehouse@yituo-outdoor.com',
    password: 'Wh@Demo123',
    role: '仓库管理员',
    phone: '13800138101',
    status: true,
    warehouseIds: ['wh_site_tz1', 'wh_site_tz_post'],
    boundAt: '2026-06-20 09:00:00',
  },
  {
    id: 'wh_user_2',
    name: '李拣货',
    account: 'picker@yituo-outdoor.com',
    password: 'Wh@Demo456',
    role: '仓库管理员',
    phone: '13800138102',
    status: true,
    warehouseIds: ['wh_site_ah'],
    boundAt: '2026-06-22 10:30:00',
  },
]
