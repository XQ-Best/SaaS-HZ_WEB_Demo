import {
  pddOrdersLocal,
  pddIssuesLocal,
  douyinOrdersLocal,
  douyinIssuesLocal,
  channelsOrdersLocal,
  channelsIssuesLocal,
} from './domesticStoresLocal'

export async function fetchTodayPddOrders(stores, options = {}) {
  return pddOrdersLocal.syncTodayOrders(stores, options)
}

export function loadCachedPddOrders(stores) {
  return pddOrdersLocal.fetchCachedOrders(stores)
}

export function loadPddIssues(stores) {
  return pddIssuesLocal.fetchIssues(stores)
}

export async function crawlPddIssues(stores, options = {}) {
  return pddIssuesLocal.syncIssues(stores, options)
}

export function resolvePddIssue(id, payload) {
  return pddIssuesLocal.resolveIssue(id, payload)
}

export async function fetchTodayDouyinOrders(stores, options = {}) {
  return douyinOrdersLocal.syncTodayOrders(stores, options)
}

export function loadCachedDouyinOrders(stores) {
  return douyinOrdersLocal.fetchCachedOrders(stores)
}

export function loadDouyinIssues(stores) {
  return douyinIssuesLocal.fetchIssues(stores)
}

export async function crawlDouyinIssues(stores, options = {}) {
  return douyinIssuesLocal.syncIssues(stores, options)
}

export function resolveDouyinIssue(id, payload) {
  return douyinIssuesLocal.resolveIssue(id, payload)
}

export async function fetchTodayChannelsOrders(stores, options = {}) {
  return channelsOrdersLocal.syncTodayOrders(stores, options)
}

export function loadCachedChannelsOrders(stores) {
  return channelsOrdersLocal.fetchCachedOrders(stores)
}

export function loadChannelsIssues(stores) {
  return channelsIssuesLocal.fetchIssues(stores)
}

export async function crawlChannelsIssues(stores, options = {}) {
  return channelsIssuesLocal.syncIssues(stores, options)
}

export function resolveChannelsIssue(id, payload) {
  return channelsIssuesLocal.resolveIssue(id, payload)
}
