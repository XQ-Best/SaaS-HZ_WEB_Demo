import {
  deleteLocalCompetitor,
  ensureDemoCompetitors,
  fetchLocalCompetitors,
  markCompetitorAnalyzed,
  saveLocalCompetitor,
} from './temuCompetitorsLocal'
import {
  deleteCompetitorSnapshots,
  getLatestSnapshot,
  resetCompetitorSnapshots,
} from './temuCompetitorSnapshotsLocal'
import { buildCompetitorMonitorReport } from '@/utils/temuCompetitor'

function loadAllCompetitors() {
  ensureDemoCompetitors()
  return fetchLocalCompetitors().data || []
}

function resolveTargets(competitors) {
  const all = loadAllCompetitors()
  if (!competitors?.length) return all
  const ids = new Set(competitors.map((item) => item.id))
  return all.filter((item) => ids.has(item.id))
}

function buildReportsForCompetitors(competitors) {
  return (competitors || [])
    .map((competitor) => buildCompetitorMonitorReport(competitor))
    .filter(Boolean)
}

export function fetchCompetitors() {
  return fetchLocalCompetitors()
}

export function saveCompetitor(payload) {
  const result = saveLocalCompetitor(payload)
  if (result.error) throw new Error(result.error)
  return result
}

export function deleteCompetitor(id) {
  deleteCompetitorSnapshots(id)
  const result = deleteLocalCompetitor(id)
  if (result.error) throw new Error(result.error)
  return result
}

/** 读取已有快照生成报告，缺失时自动补 Demo 快照 */
export function fetchCompetitorReports(competitors) {
  const targets = resolveTargets(competitors)
  for (const competitor of targets) {
    if (!getLatestSnapshot(competitor.id)) {
      resetCompetitorSnapshots(competitor)
    }
  }
  const reports = buildReportsForCompetitors(targets)
  return { success: true, data: reports, competitors: targets }
}

/** 每日爬取：为列表中每个竞店重建快照并生成报告 */
export function analyzeCompetitors(competitors) {
  const targets = resolveTargets(competitors)
  if (!targets.length) {
    return { success: true, data: [], competitors: [] }
  }

  for (const competitor of targets) {
    resetCompetitorSnapshots(competitor)
  }

  const reports = buildReportsForCompetitors(targets)
  for (const report of reports) {
    markCompetitorAnalyzed(report.id)
  }
  return { success: true, data: reports, competitors: targets }
}
