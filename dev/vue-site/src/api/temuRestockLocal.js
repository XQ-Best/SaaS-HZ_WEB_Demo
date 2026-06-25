import { TEMU_RESTOCK_STATUS_SEED } from '@/constants/temuOps'

const STORAGE_KEY = 'crosshub_temu_restock_status'

function loadAll() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : { ...TEMU_RESTOCK_STATUS_SEED }
  } catch {
    return { ...TEMU_RESTOCK_STATUS_SEED }
  }
}

function saveAll(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
}

export function getTemuRestockStatusMap() {
  const stored = loadAll()
  return { ...TEMU_RESTOCK_STATUS_SEED, ...stored }
}

export function getTemuRestockStatus(sku) {
  return getTemuRestockStatusMap()[sku] || null
}

export function updateTemuRestockStatus(sku, payload) {
  const current = loadAll()
  current[sku] = { ...current[sku], ...payload }
  saveAll(current)
  return current[sku]
}
