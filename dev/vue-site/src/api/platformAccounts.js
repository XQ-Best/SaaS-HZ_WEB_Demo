import {
  bindLocalPlatformStoresBatch,
  deleteLocalPlatformStore,
  fetchLocalPlatformStores,
} from './platformAccountsLocal'
import { ensureAliexpressDemoData } from './aliexpressDemoLocal'
import { DTC_PLATFORMS } from '@/constants/platforms'
import { ensureDtcDemoData } from './dtcDemoLocal'
import { ensureDtcOrdersDemo } from './dtcOrdersLocal'
import { ensureAlibaba1688DemoData } from './alibaba1688DemoLocal'
import { ensureAmazonDailyData } from './amazonDailyLocal'
import { ensureAmazonBossData } from './amazonBossLocal'
import { fetchCachedWalmartOrders } from './walmartOrdersLocal'
import { fetchWalmartListingIssues } from './walmartListingsLocal'
import { loadCachedPddOrders, loadPddIssues, loadCachedDouyinOrders, loadDouyinIssues, loadCachedChannelsOrders, loadChannelsIssues } from './domesticPlatforms'

/** Demo 模式：账户绑定数据保存在浏览器 localStorage，无需后端 */
export function bindPlatformStore(payload) {
  return bindLocalPlatformStoresBatch({ companyName: payload.companyName, stores: [payload] })
}

export function bindPlatformStoresBatch(payload) {
  return bindLocalPlatformStoresBatch(payload)
}

export function fetchPlatformStores(platform) {
  return fetchLocalPlatformStores(platform)
}

/** 获取全部已绑定店铺（用于店铺编排） */
export function fetchAllPlatformStores() {
  return fetchLocalPlatformStores()
}

export function deletePlatformStore(id) {
  return deleteLocalPlatformStore(id)
}

/** 获取 AliExpress 运营已绑定的全部店铺 */
export async function fetchAliExpressStores() {
  const res = await fetchLocalPlatformStores('aliexpress')
  ensureAliexpressDemoData(res.data || [])
  return res
}

/** 获取 Walmart 运营已绑定的全部店铺 */
export async function fetchWalmartStores() {
  const res = await fetchLocalPlatformStores('walmart')
  if (res.data?.length) {
    fetchCachedWalmartOrders(res.data)
    fetchWalmartListingIssues(res.data)
  }
  return res
}

function ensureDomesticStoreData(stores, loadOrders, loadIssues) {
  if (stores?.length) {
    loadOrders(stores)
    loadIssues(stores)
  }
}

/** 获取拼多多运营已绑定的全部店铺 */
export async function fetchPddStores() {
  const res = await fetchLocalPlatformStores('pdd')
  ensureDomesticStoreData(res.data, loadCachedPddOrders, loadPddIssues)
  return res
}

/** 获取抖音运营已绑定的全部店铺 */
export async function fetchDouyinStores() {
  const res = await fetchLocalPlatformStores('douyin')
  ensureDomesticStoreData(res.data, loadCachedDouyinOrders, loadDouyinIssues)
  return res
}

/** 获取视频号运营已绑定的全部店铺 */
export async function fetchChannelsStores() {
  const res = await fetchLocalPlatformStores('channels')
  ensureDomesticStoreData(res.data, loadCachedChannelsOrders, loadChannelsIssues)
  return res
}

/** 获取 Amazon 运营已绑定的全部店铺 */
export async function fetchAmazonStores() {
  const res = await fetchLocalPlatformStores('amazon')
  ensureAmazonDailyData(res.data || [])
  ensureAmazonBossData(res.data || [])
  return res
}

/** 获取 1688 运营已绑定的全部采购账号 */
export async function fetchAlibaba1688Stores() {
  const res = await fetchLocalPlatformStores('1688')
  ensureAlibaba1688DemoData(res.data || [])
  return res
}

/** 获取独立站运营已绑定的全部店铺（Shopify + WordPress） */
export async function fetchDtcStores() {
  const results = await Promise.all(DTC_PLATFORMS.map((platform) => fetchLocalPlatformStores(platform)))
  const data = results.flatMap((res) => res.data || [])
  ensureDtcDemoData(data)
  ensureDtcOrdersDemo(data)
  return {
    success: true,
    data,
  }
}
