import {
  fetchAmazonDailyData,
  markBuyerMessageReplied,
  markCaseRead,
  markReviewHandled,
  syncAmazonDailyData,
} from './amazonDailyLocal'

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
