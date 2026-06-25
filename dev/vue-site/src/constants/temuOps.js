/** Temu 平台 SPU / SKC / SKU ID（Demo） */
export const TEMU_PLATFORM_IDS = {
  'YT-T001': { spuId: 'SPU88210001', skcId: 'SKC88210001GY', skuId: 'SKU88210001GY01' },
  'YT-T002': { spuId: 'SPU88210002', skcId: 'SKC88210002BL', skuId: 'SKU88210002BL01' },
  'YT-T003': { spuId: 'SPU88210003', skcId: 'SKC88210003BK', skuId: 'SKU88210003BK01' },
  'YT-T004': { spuId: 'SPU88210004', skcId: 'SKC88210004WH', skuId: 'SKU88210004WH01' },
  'YT-T005': { spuId: 'SPU88210005', skcId: 'SKC88210005GR', skuId: 'SKU88210005GR01' },
  'YT-T006': { spuId: 'SPU88210006', skcId: 'SKC88210006SL', skuId: 'SKU88210006SL01' },
  'YT-T007': { spuId: 'SPU88210007', skcId: 'SKC88210007NV', skuId: 'SKU88210007NV01' },
  'YT-T008': { spuId: 'SPU88210008', skcId: 'SKC88210008YL', skuId: 'SKU88210008YL01' },
}

export const TEMU_RESTOCK_STATUS_LABELS = {
  pending: { label: '未备货', type: 'danger' },
  in_progress: { label: '备货中', type: 'warning' },
  done: { label: '已完成', type: 'success' },
}

/** 需跟进备货的 SKU 初始状态 */
export const TEMU_RESTOCK_STATUS_SEED = {
  'YT-T003': { status: 'pending', note: '官方仓覆盖不足 2 天，建议补货 1,200 件' },
  'YT-T008': { status: 'in_progress', note: '本地仓已拣货 450 件，待发往官方仓' },
  'YT-T001': { status: 'done', note: '今日已完成补货入库' },
}
