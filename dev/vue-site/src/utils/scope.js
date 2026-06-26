/** 按登录身份（企业管理员 / 员工负责店铺）过滤可见店铺 */
import { DTC_PLATFORM_KEY, isDtcStorePlatform, storeMatchesPlatforms } from '@/constants/platforms'

function employeePlatformList(auth) {
  return auth.backendLinked
    ? (auth.platforms || [])
    : (auth.employee?.platforms || [])
}

export function scopeStores(stores = [], auth) {
  if (!auth || auth.isBoss) return stores

  const assigned = auth.backendLinked
    ? (auth.shopScope || [])
    : (auth.employee?.assignedStoreIds || [])
  if (assigned.length) {
    return stores.filter((store) => assigned.includes(store.id))
  }

  const platforms = employeePlatformList(auth)
  if (!platforms.length) return []

  return stores.filter((store) => storeMatchesPlatforms(store.platform, platforms))
}

export function scopeStoreIds(stores, auth) {
  return new Set(scopeStores(stores, auth).map((store) => store.id))
}

export function employeeHasPlatform(auth, platform) {
  if (!auth || auth.isBoss) return true
  const key = String(platform || '').toLowerCase()
  const list = employeePlatformList(auth).map((item) => String(item).toLowerCase())
  if (list.includes(key)) return true
  if (isDtcStorePlatform(key) && list.includes(DTC_PLATFORM_KEY)) return true
  if (key === DTC_PLATFORM_KEY && list.some((item) => isDtcStorePlatform(item))) return true
  return false
}

export function employeeModuleMenus(auth) {
  if (!auth || auth.isBoss) return []

  const platforms = employeePlatformList(auth)
  const menus = []
  const seen = new Set()

  const defs = {
    temu: { index: '/employee/temu', label: 'Temu 运营' },
    aliexpress: { index: '/employee/aliexpress', label: 'AliExpress 运营' },
    amazon: { index: '/employee/amazon', label: 'Amazon 运营' },
    walmart: { index: '/employee/walmart', label: 'Walmart 运营' },
    pdd: { index: '/employee/pdd', label: '拼多多运营' },
    douyin: { index: '/employee/douyin', label: '抖音运营' },
    channels: { index: '/employee/channels', label: '视频号运营' },
    '1688': { index: '/employee/1688', label: '1688 运营' },
    [DTC_PLATFORM_KEY]: { index: '/employee/dtc', label: '独立站运营' },
    shopify: { index: '/employee/dtc', label: '独立站运营' },
    wordpress: { index: '/employee/dtc', label: '独立站运营' },
  }

  for (const platform of platforms) {
    const def = defs[platform]
    if (!def || seen.has(def.index)) continue
    seen.add(def.index)
    menus.push({ ...def, platform })
  }

  return menus
}
