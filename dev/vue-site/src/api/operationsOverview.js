import { fetchPlatformStores, fetchAliExpressStores, fetchAmazonStores, fetchAlibaba1688Stores, fetchDtcStores } from './platformAccounts'
import { TEMU_PRODUCTS_RAW } from '@/constants/temu'
import { enrichAllProducts } from '@/utils/temu'
import { buildOperationsOverview } from '@/utils/operationsOverview'
import { buildPlatformSalesRows } from '@/utils/platformMetrics'
import { scopeStores } from '@/utils/scope'
import { getTemuRestockStatusMap } from './temuRestockLocal'
import { loadCachedAliExpressOrders, loadAliExpressViolations } from './aliexpress'
import { ensureAliexpressDemoData } from './aliexpressDemoLocal'
import { loadAlibaba1688DemoData } from './alibaba1688DemoLocal'
import { ensureAmazonDailyData } from './amazonDailyLocal'
import { loadAmazonDailyWorkflow } from './amazon'
import { loadDtcTodayOrders, ensureDtcOrdersDemo } from './dtcOrdersLocal'
import { fetchEmployees } from './employees'
import { filterTasksForAuth } from '@/utils/operations'

function filterByStoreIds(items, storeIds) {
  const set = new Set(storeIds)
  return (items || []).filter((item) => set.has(item.storeId))
}

/** 统一运营上下文：账户绑定 → 店铺 → 员工 → 各平台运营数据 → 总览 */
export async function loadOperationsOverview(auth = null) {
  const [temuStoresRes, aeStoresRes, amazonStoresRes, stores1688Res, dtcStoresRes, employeesRes] = await Promise.all([
    fetchPlatformStores('temu'),
    fetchAliExpressStores(),
    fetchAmazonStores(),
    fetchAlibaba1688Stores(),
    fetchDtcStores(),
    fetchEmployees(),
  ])

  const employees = employeesRes.data || []
  let temuStores = scopeStores(temuStoresRes.data || [], auth)
  let aeStores = scopeStores(aeStoresRes.data || [], auth)
  let amazonStores = scopeStores(amazonStoresRes.data || [], auth)
  let stores1688 = scopeStores(stores1688Res.data || [], auth)
  let dtcStores = scopeStores(dtcStoresRes.data || [], auth)

  const temuStoreIds = temuStores.map((store) => store.id)
  const aeStoreIds = aeStores.map((store) => store.id)
  const amazonStoreIds = amazonStores.map((store) => store.id)
  const stores1688Ids = stores1688.map((store) => store.id)
  const dtcStoreIds = dtcStores.map((store) => store.id)

  const temuProducts = enrichAllProducts(
    filterByStoreIds(TEMU_PRODUCTS_RAW, temuStoreIds),
  )

  if (dtcStores.length) {
    ensureDtcOrdersDemo(dtcStores)
  }

  if (aeStores.length) {
    ensureAliexpressDemoData(aeStores)
  }

  if (amazonStores.length) {
    ensureAmazonDailyData(amazonStores)
  }

  const aeOrders = aeStores.length
    ? filterByStoreIds(loadCachedAliExpressOrders(aeStores).data.orders, aeStoreIds)
    : []
  const aeViolations = aeStores.length
    ? filterByStoreIds(loadAliExpressViolations(aeStores).data.violations, aeStoreIds)
    : []

  const amazonDaily = amazonStores.length
    ? loadAmazonDailyWorkflow(amazonStores).data
    : {
        buyerMessages: [],
        accountMetrics: [],
        reviews: [],
        coupons: [],
        sellerNews: [],
        shipments: [],
        cases: [],
      }

  const demo1688 = stores1688.length ? loadAlibaba1688DemoData(stores1688) : { purchaseOrders: [], supplierAlerts: [] }
  const purchaseOrders = filterByStoreIds(demo1688.purchaseOrders, stores1688Ids)
  const supplierAlerts = filterByStoreIds(demo1688.supplierAlerts, stores1688Ids)

  const dtcOrders = filterByStoreIds(loadDtcTodayOrders(dtcStores), dtcStoreIds)

  const temuPayload = {
    stores: temuStores,
    products: temuProducts,
    restockStatus: getTemuRestockStatusMap(),
  }
  const aliexpressPayload = {
    stores: aeStores,
    orders: aeOrders,
    violations: aeViolations,
  }
  const amazonPayload = {
    stores: amazonStores,
    buyerMessages: filterByStoreIds(amazonDaily.buyerMessages, amazonStoreIds),
    accountMetrics: filterByStoreIds(amazonDaily.accountMetrics, amazonStoreIds),
    reviews: filterByStoreIds(amazonDaily.reviews, amazonStoreIds),
    coupons: filterByStoreIds(amazonDaily.coupons, amazonStoreIds),
    sellerNews: filterByStoreIds(amazonDaily.sellerNews, amazonStoreIds),
    shipments: filterByStoreIds(amazonDaily.shipments, amazonStoreIds),
    cases: filterByStoreIds(amazonDaily.cases, amazonStoreIds),
  }
  const alibaba1688Payload = {
    stores: stores1688,
    purchaseOrders,
    supplierAlerts,
  }
  const dtcPayload = {
    stores: dtcStores,
    orders: dtcOrders,
  }

  const storeNameMaps = {
    temu: Object.fromEntries(temuStores.map((store) => [store.id, store.storeName])),
    aliexpress: Object.fromEntries(aeStores.map((store) => [store.id, store.storeName])),
    amazon: Object.fromEntries(amazonStores.map((store) => [store.id, store.storeName])),
    '1688': Object.fromEntries(stores1688.map((store) => [store.id, store.storeName])),
    dtc: Object.fromEntries(dtcStores.map((store) => [store.id, store.storeName])),
  }

  const overview = buildOperationsOverview({
    temu: temuPayload,
    aliexpress: aliexpressPayload,
    amazon: amazonPayload,
    alibaba1688: alibaba1688Payload,
    dtc: dtcPayload,
    storeNameMaps,
    employees,
  })

  const platformSales = buildPlatformSalesRows({
    temu: temuPayload,
    aliexpress: aliexpressPayload,
    amazon: amazonPayload,
    alibaba1688: alibaba1688Payload,
    dtc: dtcPayload,
    employees,
  })

  const tasks = filterTasksForAuth(employees, auth)

  return {
    success: true,
    data: {
      ...overview,
      platformSales,
      tasks,
      employees,
      stores: {
        temu: temuStores,
        aliexpress: aeStores,
        amazon: amazonStores,
        '1688': stores1688,
        dtc: dtcStores,
      },
    },
  }
}
