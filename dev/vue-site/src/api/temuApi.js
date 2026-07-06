import { service } from './request'
import { mapReptileSaleToTemuProduct } from '@/utils/mapReptileSaleToTemuProduct'
import { enrichAllProducts } from '@/utils/temu'
import { applyServerAlgorithms } from '@/utils/temuServerAlgo'
import { scopeStores } from '@/utils/scope'
import { getAccessToken } from './request'
import { isTemuBackendEnabled } from './config'
import {
  fetchLocalTemuSalesTrend,
  fetchLocalTemuStores,
  loadLocalTemuOperationalData,
} from './temuDemoLocal'

const TEMU_PLATFORM = 'temu'

export function canUseTemuBackend(auth) {
  if (!isTemuBackendEnabled()) return false
  return Boolean(getAccessToken() && auth?.backendLinked)
}

export async function fetchTemuStores(auth) {
  if (canUseTemuBackend(auth)) {
    const res = await service.get('/api/temu/shops', { skipGlobalErrorToast: true })
    const list = res?.data ?? []
    const stores = (Array.isArray(list) ? list : []).map((shop) => ({
      id: shop.shop_id,
      storeName: shop.shop_name || shop.shop_id,
      platform: TEMU_PLATFORM,
      isUpload: shop.is_upload,
    }))
    return scopeStores(stores, auth)
  }
  return fetchLocalTemuStores(auth)
}

export async function fetchTemuOperationalData({ shopId } = {}) {
  const params = {}
  if (shopId && shopId !== 'all') params.shop_id = shopId

  const res = await service.get('/api/temu/operational', { params })
  const products = (res.products || []).map((row) => mapReptileSaleToTemuProduct(row))
  const enriched = enrichAllProducts(products)
  const merged = applyServerAlgorithms(enriched, {
    loseProducts: res.lose_products || [],
    lowWarnings: res.low_warnings || [],
    inventoryWarnings: res.inventory_warnings || [],
    overloadProducts: res.overload_products || [],
  })

  return {
    products: merged,
    meta: {
      source: 'backend',
      reportTime: res.report_time,
      salesCount: products.length,
      loseCount: (res.lose_products || []).length,
      restockCount: (res.inventory_warnings || []).length,
      overloadCount: (res.overload_products || []).length,
    },
  }
}

export async function fetchTemuSalesTrend({ auth, shopId, days = 7 } = {}) {
  if (canUseTemuBackend(auth)) {
    const params = { days }
    if (shopId && shopId !== 'all') params.shop_id = shopId
    const res = await service.get('/api/temu/trend', { params })
    return {
      labels: res.labels || [],
      values: res.values || [],
    }
  }
  return fetchLocalTemuSalesTrend({ shopId, days })
}

export async function loadTemuModuleData({ auth, shopId }) {
  if (canUseTemuBackend(auth)) {
    return fetchTemuOperationalData({ shopId })
  }
  return loadLocalTemuOperationalData({ shopId })
}
