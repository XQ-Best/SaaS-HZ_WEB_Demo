import { fetchLocalEmployees } from './employeesLocal'
import {
  ensureDefaultUser,
  loginLocalBoss,
  registerLocalUser,
} from './authLocal'

export function registerCompany(payload) {
  const result = registerLocalUser(payload)
  if (result.error) throw new Error(result.error)
  return result
}

export function loginBoss(payload) {
  const result = loginLocalBoss(payload)
  if (result.error) throw new Error(result.error)
  return result
}

export function loginEmployee({ account, password }) {
  ensureDefaultUser()
  const acc = String(account || '').trim().toLowerCase()
  const pwd = String(password || '')
  const employees = fetchLocalEmployees().data || []
  const employee = employees.find(
    (e) => e.account.toLowerCase() === acc && e.password === pwd && e.status !== false,
  )
  if (!employee) {
    throw new Error('员工账号或密码错误，请联系管理员在员工绑定中添加')
  }
  return {
    success: true,
    data: {
      id: employee.id,
      name: employee.name,
      account: employee.account,
      role: employee.role,
      platforms: employee.platforms,
      assignedStoreIds: employee.assignedStoreIds || [],
    },
  }
}
