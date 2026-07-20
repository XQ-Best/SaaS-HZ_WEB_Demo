import { AppApiError, getAppErrorMessage } from '@/utils/appErrorCode'
import { loadScoped, saveScoped, resolveTenantId } from '@/utils/tenantStorage'
const LAST_CRAWL_KEY = 'platform_sync_last_crawl_at'
const LAST_HYDRATE_KEY = 'platform_sync_last_hydrate_at'

export const CRAWL_COOLDOWN_ERROR = 'CRAWL_COOLDOWN'

/** 全量爬取冷却：默认 3 小时（多平台全量同步可能需十余分钟） */
export const PLATFORM_SYNC_COOLDOWN_MS = 3 * 60 * 60 * 1000

/** 侧栏状态回填冷却：默认 1 分钟（仅读库，避免频繁打 API） */
export const PLATFORM_HYDRATE_COOLDOWN_MS = 60 * 1000

function readTimestamp(auth, baseKey) {
  const raw = loadScoped(resolveTenantId(auth), baseKey, 0)
  const value = Number(raw)
  return Number.isFinite(value) && value > 0 ? value : 0
}

function writeTimestamp(auth, baseKey) {
  saveScoped(resolveTenantId(auth), baseKey, Date.now())
}

export function getLastPlatformCrawlAt(auth) {
  return readTimestamp(auth, LAST_CRAWL_KEY)
}

export function markPlatformCrawlCompleted(auth) {
  writeTimestamp(auth, LAST_CRAWL_KEY)
}

export function getLastPlatformHydrateAt(auth) {
  return readTimestamp(auth, LAST_HYDRATE_KEY)
}

export function markPlatformHydrateCompleted(auth) {
  writeTimestamp(auth, LAST_HYDRATE_KEY)
}

export function getCooldownRemainingMs(auth, { cooldownMs = PLATFORM_SYNC_COOLDOWN_MS } = {}) {
  const last = getLastPlatformCrawlAt(auth)
  if (!last) return 0
  const remaining = cooldownMs - (Date.now() - last)
  return remaining > 0 ? remaining : 0
}

export function isPlatformCrawlInCooldown(auth, { force = false, cooldownMs = PLATFORM_SYNC_COOLDOWN_MS } = {}) {
  if (force) return false
  return getCooldownRemainingMs(auth, { cooldownMs }) > 0
}

export function isPlatformHydrateInCooldown(auth, { cooldownMs = PLATFORM_HYDRATE_COOLDOWN_MS } = {}) {
  const last = getLastPlatformHydrateAt(auth)
  if (!last) return false
  return Date.now() - last < cooldownMs
}

export function hasSuccessfulSyncItems(items = []) {
  return items.some((item) => item.status === 'success' || item.status === 'partial')
}

/** 仅侧栏批量同步内部使用，外部不可伪造 */
export const PLATFORM_SYNC_BATCH_GUARD = Symbol.for('crosshub.platformSync.batch')

/** 侧栏全量同步批次的 crawl 选项（跳过前端冷却检查，不在子任务写冷却） */
export function createPlatformSyncBatchOptions(force = false) {
  return {
    force,
    [PLATFORM_SYNC_BATCH_GUARD]: true,
    recordCooldown: false,
  }
}

function isPlatformSyncBatch(options = {}) {
  return options[PLATFORM_SYNC_BATCH_GUARD] === true
}

export function normalizeCrawlOptions(options = {}) {
  const force = Boolean(options.force)
  const withinBatch = isPlatformSyncBatch(options)
  const recordCooldown = options.recordCooldown ?? !withinBatch
  return { force, withinBatch, recordCooldown }
}

export function isPlatformSyncBatchOptions(options = {}) {
  return isPlatformSyncBatch(options)
}

export function assertPlatformCrawlAllowed(auth = null, { force = false, withinBatch = false } = {}) {
  if (force || withinBatch) return
  if (!isPlatformCrawlInCooldown(auth)) return
  const remaining = formatCooldownRemaining(getCooldownRemainingMs(auth))
  throw new AppApiError(
    `同步冷却中，${remaining}后可再次爬取（侧栏「重新同步」可强制刷新）`,
    CRAWL_COOLDOWN_ERROR,
  )
}

export function markPlatformCrawlOnSuccess(auth = null, result, { enabled = true } = {}) {
  if (!enabled) return
  if (Array.isArray(result)) {
    if (hasSuccessfulSyncItems(result)) markPlatformCrawlCompleted(auth)
    return
  }
  if (result?.success || result?.partial) {
    markPlatformCrawlCompleted(auth)
  }
}

export function applyCrawlRequestFlags(body, options = {}) {
  const crawlOpts = normalizeCrawlOptions(options)
  if (crawlOpts.force) {
    body.force = true
  }
  if (!crawlOpts.recordCooldown) {
    body.record_cooldown = false
  }
  return body
}

/** @deprecated 使用 applyCrawlRequestFlags */
export function applyCrawlForceFlag(body, options = {}) {
  return applyCrawlRequestFlags(body, options)
}

export function throwIfCrawlCooldownResponse(res, payload, fallbackMessage = '触发爬取失败') {
  if (res?.status === 429 || payload?.error_code === CRAWL_COOLDOWN_ERROR) {
    throw new AppApiError(
      getAppErrorMessage(payload?.error_code || CRAWL_COOLDOWN_ERROR, payload?.msg || fallbackMessage),
      CRAWL_COOLDOWN_ERROR,
    )
  }
}

export function formatCooldownRemaining(ms) {
  if (ms <= 0) return ''
  const totalMinutes = Math.ceil(ms / 60000)
  if (totalMinutes < 60) {
    return totalMinutes <= 1 ? '不到 1 分钟' : `约 ${totalMinutes} 分钟`
  }
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  if (minutes === 0) return `约 ${hours} 小时`
  return `约 ${hours} 小时 ${minutes} 分钟`
}
