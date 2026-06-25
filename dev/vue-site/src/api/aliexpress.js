import { fetchAliexpressDemoData } from './aliexpressDemoLocal'
import {
  fetchCachedAliExpressOrders,
  syncTodayAliExpressOrders,
} from './aliexpressOrdersLocal'
import {
  confirmViolationAppeal,
  fetchAliExpressViolations as loadStoredViolations,
  syncAliExpressViolations,
} from './aliexpressViolationsLocal'

export function loadAliExpressOperationalData(stores) {
  return fetchAliexpressDemoData(stores)
}

export async function fetchTodayAliExpressOrders(stores, options = {}) {
  const demoRes = fetchAliexpressDemoData(stores)
  return syncTodayAliExpressOrders(stores, demoRes.data.products, options)
}

export function loadCachedAliExpressOrders(stores) {
  return fetchCachedAliExpressOrders(stores)
}

export function loadAliExpressViolations(stores) {
  return loadStoredViolations(stores)
}

export async function crawlAliExpressViolations(stores, options = {}) {
  return syncAliExpressViolations(stores, options)
}

export function confirmAliExpressViolationAppeal(id, payload) {
  return confirmViolationAppeal(id, payload)
}
