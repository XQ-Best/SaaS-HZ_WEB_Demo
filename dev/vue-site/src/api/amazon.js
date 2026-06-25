import {
  fetchAmazonDailyData,
  markBuyerMessageReplied,
  markCaseRead,
  markReviewHandled,
  syncAmazonDailyData,
} from './amazonDailyLocal'

import {
  fetchAmazonBossData,
  markOutboundShipped,
  syncAmazonBossData,
} from './amazonBossLocal'

export function loadAmazonBossInsights(stores) {
  return fetchAmazonBossData(stores)
}

export async function refreshAmazonBossInsights(stores, options = {}) {
  return syncAmazonBossData(stores, options)
}

export function shipOutboundOrder(id, payload) {
  return markOutboundShipped(id, payload)
}

export function loadAmazonDailyWorkflow(stores) {
  return fetchAmazonDailyData(stores)
}

export async function refreshAmazonDailyWorkflow(stores, options = {}) {
  return syncAmazonDailyData(stores, options)
}

export function replyBuyerMessage(id, payload) {
  return markBuyerMessageReplied(id, payload)
}

export function handleReview(id, payload) {
  return markReviewHandled(id, payload)
}

export function acknowledgeCase(id) {
  return markCaseRead(id)
}

/** @deprecated */
export function loadAmazonOperationalData(stores) {
  return loadAmazonDailyWorkflow(stores)
}
