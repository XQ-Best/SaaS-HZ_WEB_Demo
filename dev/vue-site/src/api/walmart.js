import { syncTodayWalmartOrders, fetchCachedWalmartOrders } from './walmartOrdersLocal'
import {
  fetchWalmartListingIssues,
  syncWalmartListingIssues,
  resolveWalmartListingIssue,
} from './walmartListingsLocal'

export async function fetchTodayWalmartOrders(stores, options = {}) {
  return syncTodayWalmartOrders(stores, options)
}

export function loadCachedWalmartOrders(stores) {
  return fetchCachedWalmartOrders(stores)
}

export function loadWalmartListingIssues(stores) {
  return fetchWalmartListingIssues(stores)
}

export async function crawlWalmartListingIssues(stores, options = {}) {
  return syncWalmartListingIssues(stores, options)
}

export function resolveWalmartIssue(id, payload) {
  return resolveWalmartListingIssue(id, payload)
}
