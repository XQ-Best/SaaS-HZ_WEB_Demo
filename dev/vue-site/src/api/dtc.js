import { fetchDtcDemoData } from './dtcDemoLocal'
import { ensureDtcOrdersDemo } from './dtcOrdersLocal'

export function loadDtcOperationalData(stores) {
  ensureDtcOrdersDemo(stores)
  return fetchDtcDemoData(stores)
}
