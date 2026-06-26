import { findLocalWarehouseStaffByAccount } from './warehouseStaffLocal'

export function loginLocalWarehouse({ account, password }) {
  const acc = String(account || '').trim().toLowerCase()
  const pwd = String(password || '')
  const user = findLocalWarehouseStaffByAccount(acc)
  if (!user || user.password !== pwd) {
    return { error: '仓库账号或密码错误' }
  }
  return {
    data: {
      id: user.id,
      name: user.name,
      account: user.account,
      role: user.role,
      phone: user.phone,
      warehouseIds: user.warehouseIds || [],
    },
  }
}
