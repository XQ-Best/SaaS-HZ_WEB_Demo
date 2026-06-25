import { fetchPlatformStores, fetchAliExpressStores, fetchWalmartStores, fetchPddStores, fetchDouyinStores, fetchChannelsStores, fetchAmazonStores, fetchAlibaba1688Stores, fetchDtcStores } from './platformAccounts'
import { TEMU_PRODUCTS_RAW } from '@/constants/temu'
import { enrichAllProducts } from '@/utils/temu'
import { buildOperationsOverview } from '@/utils/operationsOverview'
import { buildPlatformSalesRows } from '@/utils/platformMetrics'
import { scopeStores } from '@/utils/scope'
import { getTemuRestockStatusMap } from './temuRestockLocal'
import { loadCachedAliExpressOrders, loadAliExpressViolations } from './aliexpress'
import { loadCachedWalmartOrders, loadWalmartListingIssues } from './walmart'
import { enrichListingIssue } from '@/utils/walmart'
import { enrichDomesticIssue } from '@/utils/domesticPlatform'
import { PDD_ISSUE_TYPES } from '@/constants/pddDemo'
import { DOUYIN_ISSUE_TYPES } from '@/constants/douyinDemo'
import { CHANNELS_ISSUE_TYPES } from '@/constants/channelsDemo'
import { loadCachedPddOrders, loadPddIssues, loadCachedDouyinOrders, loadDouyinIssues, loadCachedChannelsOrders, loadChannelsIssues } from './domesticPlatforms'
import { ensureAliexpressDemoData } from './aliexpressDemoLocal'
import { loadAlibaba1688DemoData } from './alibaba1688DemoLocal'
import { ensureAmazonDailyData } from './amazonDailyLocal'
import { loadAmazonDailyWorkflow } from './amazon'
import { loadDtcTodayOrders, ensureDtcOrdersDemo } from './dtcOrdersLocal'
import { fetchEmployees } from './employees'
import { buildTaskCenterForAuth } from '@/utils/employeeTasks'
import { buildDailyOpsReport } from '@/utils/dailyOpsReport'
import { loadTodayOpsFeedback } from '@/api/opsFeedback'

function filterByStoreIds(items, storeIds) {
  const set = new Set(storeIds)
  return (items || []).filter((item) => set.has(item.storeId))
}

/** 统一运营上下文：账户绑定 → 店铺 → 员工 → 各平台运营数据 → 总览 */
export async function loadOperationsOverview(auth = null) {
  const [temuStoresRes, aeStoresRes, walmartStoresRes, pddStoresRes, douyinStoresRes, channelsStoresRes, amazonStoresRes, stores1688Res, dtcStoresRes, employeesRes] = await Promise.all([
    fetchPlatformStores('temu'),
    fetchAliExpressStores(),
    fetchWalmartStores(),
    fetchPddStores(),
    fetchDouyinStores(),
    fetchChannelsStores(),
    fetchAmazonStores(),
    fetchAlibaba1688Stores(),
    fetchDtcStores(),
    fetchEmployees(),
  ])

  const employees = employeesRes.data || []
  let temuStores = scopeStores(temuStoresRes.data || [], auth)
  let aeStores = scopeStores(aeStoresRes.data || [], auth)
  let walmartStores = scopeStores(walmartStoresRes.data || [], auth)
  let pddStores = scopeStores(pddStoresRes.data || [], auth)
  let douyinStores = scopeStores(douyinStoresRes.data || [], auth)
  let channelsStores = scopeStores(channelsStoresRes.data || [], auth)
  let amazonStores = scopeStores(amazonStoresRes.data || [], auth)
  let stores1688 = scopeStores(stores1688Res.data || [], auth)
  let dtcStores = scopeStores(dtcStoresRes.data || [], auth)

  const temuStoreIds = temuStores.map((store) => store.id)
  const aeStoreIds = aeStores.map((store) => store.id)
  const walmartStoreIds = walmartStores.map((store) => store.id)
  const pddStoreIds = pddStores.map((store) => store.id)
  const douyinStoreIds = douyinStores.map((store) => store.id)
  const channelsStoreIds = channelsStores.map((store) => store.id)
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

  const wmOrders = walmartStores.length
    ? filterByStoreIds(loadCachedWalmartOrders(walmartStores).data.orders, walmartStoreIds)
    : []
  const wmIssues = walmartStores.length
    ? filterByStoreIds(
        loadWalmartListingIssues(walmartStores).data.issues.map((issue) => enrichListingIssue(issue)),
        walmartStoreIds,
      )
    : []

  const pddOrders = pddStores.length
    ? filterByStoreIds(loadCachedPddOrders(pddStores).data.orders, pddStoreIds)
    : []
  const pddIssues = pddStores.length
    ? filterByStoreIds(
        loadPddIssues(pddStores).data.issues.map((issue) => enrichDomesticIssue(issue, PDD_ISSUE_TYPES)),
        pddStoreIds,
      )
    : []

  const douyinOrders = douyinStores.length
    ? filterByStoreIds(loadCachedDouyinOrders(douyinStores).data.orders, douyinStoreIds)
    : []
  const douyinIssues = douyinStores.length
    ? filterByStoreIds(
        loadDouyinIssues(douyinStores).data.issues.map((issue) => enrichDomesticIssue(issue, DOUYIN_ISSUE_TYPES)),
        douyinStoreIds,
      )
    : []

  const channelsOrders = channelsStores.length
    ? filterByStoreIds(loadCachedChannelsOrders(channelsStores).data.orders, channelsStoreIds)
    : []
  const channelsIssues = channelsStores.length
    ? filterByStoreIds(
        loadChannelsIssues(channelsStores).data.issues.map((issue) => enrichDomesticIssue(issue, CHANNELS_ISSUE_TYPES)),
        channelsStoreIds,
      )
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
  const walmartPayload = {
    stores: walmartStores,
    orders: wmOrders,
    issues: wmIssues,
  }
  const pddPayload = {
    stores: pddStores,
    orders: pddOrders,
    issues: pddIssues,
  }
  const douyinPayload = {
    stores: douyinStores,
    orders: douyinOrders,
    issues: douyinIssues,
  }
  const channelsPayload = {
    stores: channelsStores,
    orders: channelsOrders,
    issues: channelsIssues,
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
    walmart: Object.fromEntries(walmartStores.map((store) => [store.id, store.storeName])),
    pdd: Object.fromEntries(pddStores.map((store) => [store.id, store.storeName])),
    douyin: Object.fromEntries(douyinStores.map((store) => [store.id, store.storeName])),
    channels: Object.fromEntries(channelsStores.map((store) => [store.id, store.storeName])),
    amazon: Object.fromEntries(amazonStores.map((store) => [store.id, store.storeName])),
    '1688': Object.fromEntries(stores1688.map((store) => [store.id, store.storeName])),
    dtc: Object.fromEntries(dtcStores.map((store) => [store.id, store.storeName])),
  }

  const overview = buildOperationsOverview({
    temu: temuPayload,
    aliexpress: aliexpressPayload,
    walmart: walmartPayload,
    pdd: pddPayload,
    douyin: douyinPayload,
    channels: channelsPayload,
    amazon: amazonPayload,
    alibaba1688: alibaba1688Payload,
    dtc: dtcPayload,
    storeNameMaps,
    employees,
  })

  const platformSales = buildPlatformSalesRows({
    temu: temuPayload,
    aliexpress: aliexpressPayload,
    walmart: walmartPayload,
    pdd: pddPayload,
    douyin: douyinPayload,
    channels: channelsPayload,
    amazon: amazonPayload,
    alibaba1688: alibaba1688Payload,
    dtc: dtcPayload,
    employees,
  })

  const tasks = buildTaskCenterForAuth(
    { platforms: overview.platforms, totalIssues: overview.totalIssues, syncedAt: overview.syncedAt },
    auth,
    employees,
  )

  const feedbacks = loadTodayOpsFeedback().data
  const dailyReport = auth?.isBoss
    ? buildDailyOpsReport({
        overview,
        platformSales,
        employees,
        tasks,
        feedbacks,
      })
    : null

  return {
    success: true,
    data: {
      ...overview,
      platformSales,
      tasks,
      employees,
      feedbacks,
      dailyReport,
      stores: {
        temu: temuStores,
        aliexpress: aeStores,
        walmart: walmartStores,
        pdd: pddStores,
        douyin: douyinStores,
        channels: channelsStores,
        amazon: amazonStores,
        '1688': stores1688,
        dtc: dtcStores,
      },
    },
  }
}
