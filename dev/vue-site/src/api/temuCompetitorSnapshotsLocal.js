import {
  buildDemoSnapshotsForCompetitor,
  DEMO_COMPETITOR_IDS,
} from '@/constants/temuCompetitors'
import { localDateKey } from '@/utils/date'

const STORAGE_KEY = 'crosshub_temu_competitor_snapshots'
const MAX_DAYS = 30

function loadAll() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveAll(snapshots) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshots))
}

function todayKey() {
  return localDateKey()
}

/** 批量替换某竞店的全部快照 */
export function replaceCompetitorSnapshots(competitorId, snapshots) {
  const others = loadAll().filter((item) => item.competitorId !== competitorId)
  const merged = [
    ...others,
    ...snapshots
      .filter((item) => item.competitorId === competitorId)
      .sort((a, b) => b.date.localeCompare(a.date))
      .slice(0, MAX_DAYS),
  ]
  saveAll(merged)
}

/** 为单个竞店重建 Demo 快照（绑定到该竞店 id） */
export function resetCompetitorSnapshots(competitor) {
  const snapshots = buildDemoSnapshotsForCompetitor(competitor).map((item) => ({
    ...item,
    demoVersion: 'v1',
  }))
  replaceCompetitorSnapshots(competitor.id, snapshots)
  return snapshots
}

/** 确保所有 Demo 竞店 id 的快照存在 */
export function ensureDemoSnapshots() {
  for (const competitorId of DEMO_COMPETITOR_IDS) {
    if (getLatestSnapshot(competitorId)) continue
    const snapshots = buildDemoSnapshotsForCompetitor({ id: competitorId, url: '' })
    replaceCompetitorSnapshots(competitorId, snapshots.map((s) => ({ ...s, demoVersion: 'v1' })))
  }
}

/** @deprecated 使用 resetCompetitorSnapshots */
export function resetDemoSnapshots() {
  for (const competitorId of DEMO_COMPETITOR_IDS) {
    resetCompetitorSnapshots({ id: competitorId, url: '' })
  }
}

export function getCompetitorSnapshots(competitorId) {
  return loadAll()
    .filter((item) => item.competitorId === competitorId)
    .sort((a, b) => b.date.localeCompare(a.date))
}

export function getLatestSnapshot(competitorId) {
  const list = getCompetitorSnapshots(competitorId)
  return list[0] || null
}

export function getSnapshotByDate(competitorId, date) {
  return loadAll().find(
    (item) => item.competitorId === competitorId && item.date === date,
  ) || null
}

export function saveSnapshot(snapshot) {
  const existing = getCompetitorSnapshots(snapshot.competitorId).filter(
    (item) => item.date !== snapshot.date,
  )
  replaceCompetitorSnapshots(snapshot.competitorId, [...existing, snapshot])
  return snapshot
}

export function deleteCompetitorSnapshots(competitorId) {
  saveAll(loadAll().filter((item) => item.competitorId !== competitorId))
}

export function canCrawlToday(competitorId) {
  return !getSnapshotByDate(competitorId, todayKey())
}

export { todayKey }
