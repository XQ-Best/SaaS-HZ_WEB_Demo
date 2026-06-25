<script setup>
import { computed, ref } from 'vue'
import { RESTOCK_CONFIG } from '@/constants/temu'
import AssigneeTableColumn from '@/components/common/AssigneeTableColumn.vue'

const props = defineProps({
  products: { type: Array, required: true },
  showStoreColumn: { type: Boolean, default: false },
})

const urgencyFilter = ref('all')

const filtered = computed(() => {
  let list = [...props.products].sort((a, b) => a.restock.coverDays - b.restock.coverDays)
  if (urgencyFilter.value === 'urgent') {
    list = list.filter((p) => p.restock.urgency === 'critical' || p.restock.urgency === 'warning')
  }
  if (urgencyFilter.value === 'hot') list = list.filter((p) => p.isHot)
  return list
})

const totalSuggest = computed(() =>
  filtered.value.reduce((s, p) => s + p.restock.suggestedRestock, 0),
)

function urgencyTag(row) {
  const map = {
    critical: { type: 'danger', label: '紧急补货' },
    warning: { type: 'warning', label: '建议补货' },
    caution: { type: 'info', label: '低于安全线' },
    normal: { type: 'success', label: '正常' },
  }
  return map[row.restock.urgency] || map.normal
}
</script>

<template>
  <div>
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="24">
        <el-alert type="info" show-icon :closable="false">
          <template #title>备货逻辑说明</template>
          <template #default>
            日均需求 = max(当日销量, 7 日均值) ·
            目标库存 = 日均 × ({{ RESTOCK_CONFIG.targetCoverDays }} 天覆盖 + {{ RESTOCK_CONFIG.leadTimeDays }} 天提前期) ·
            建议补货 = 目标 − 官方仓库存（不超过本地仓可用）
          </template>
        </el-alert>
      </el-col>
    </el-row>

    <el-card shadow="never">
      <template #header>
        <el-space wrap>
          <span>本地仓 → Temu 官方仓 备货计划</span>
          <el-radio-group v-model="urgencyFilter" size="small">
            <el-radio-button value="all">全部 SKU</el-radio-button>
            <el-radio-button value="urgent">需补货</el-radio-button>
            <el-radio-button value="hot">爆款优先</el-radio-button>
          </el-radio-group>
          <el-tag type="primary">合计建议备货 {{ totalSuggest.toLocaleString() }} 件</el-tag>
        </el-space>
      </template>

      <el-table :data="filtered" stripe>
        <el-table-column v-if="showStoreColumn" prop="storeName" label="所属店铺" width="130" show-overflow-tooltip />
        <AssigneeTableColumn />
        <el-table-column prop="sku" label="SKU" width="110" fixed />
        <el-table-column prop="name" label="商品名称" min-width="160" show-overflow-tooltip />
        <el-table-column label="当日/7日均" width="120" align="center">
          <template #default="{ row }">
            {{ row.dailySales }} / {{ row.avg7DayDaily }}
          </template>
        </el-table-column>
        <el-table-column label="日均需求" width="90" align="right">
          <template #default="{ row }">{{ row.restock.dailyDemand }}</template>
        </el-table-column>
        <el-table-column label="官方仓" width="90" align="right" prop="officialStock" />
        <el-table-column label="本地仓" width="90" align="right" prop="localStock" />
        <el-table-column label="可售天数" width="100" align="right">
          <template #default="{ row }">
            <el-text :type="row.restock.coverDays <= RESTOCK_CONFIG.leadTimeDays ? 'danger' : row.restock.coverDays <= RESTOCK_CONFIG.safetyDays ? 'warning' : undefined">
              {{ row.restock.coverDays >= 999 ? '∞' : row.restock.coverDays }} 天
            </el-text>
          </template>
        </el-table-column>
        <el-table-column label="安全库存" width="100" align="right">
          <template #default="{ row }">{{ row.restock.safetyStock }}</template>
        </el-table-column>
        <el-table-column label="目标库存" width="100" align="right">
          <template #default="{ row }">{{ row.restock.targetStock }}</template>
        </el-table-column>
        <el-table-column label="建议备货" width="110" align="right" fixed="right">
          <template #default="{ row }">
            <strong>{{ row.restock.suggestedRestock }}</strong>
          </template>
        </el-table-column>
        <el-table-column label="紧急度" width="110" fixed="right">
          <template #default="{ row }">
            <el-tag :type="urgencyTag(row).type" size="small">{{ urgencyTag(row).label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="备注" width="130" fixed="right">
          <template #default="{ row }">
            <el-text v-if="row.restock.shortfall > 0" type="danger" size="small">
              本地缺 {{ row.restock.shortfall }}
            </el-text>
            <el-text v-else-if="row.isHot" type="success" size="small">爆款优先</el-text>
            <el-text v-else type="info" size="small">—</el-text>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :xs="24" :lg="12">
        <el-card shadow="never">
          <template #header>参数配置（Demo）</template>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="安全库存天数">{{ RESTOCK_CONFIG.safetyDays }} 天</el-descriptions-item>
            <el-descriptions-item label="目标覆盖">{{ RESTOCK_CONFIG.targetCoverDays }} 天</el-descriptions-item>
            <el-descriptions-item label="备货提前期">{{ RESTOCK_CONFIG.leadTimeDays }} 天</el-descriptions-item>
            <el-descriptions-item label="补货来源">本地仓库</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card shadow="never">
          <template #header>优先补货清单</template>
          <el-table
            :data="filtered.filter((p) => p.restock.suggestedRestock > 0).slice(0, 5)"
            size="small"
          >
            <el-table-column prop="name" label="商品" show-overflow-tooltip />
            <AssigneeTableColumn width="90" />
            <el-table-column label="建议量" width="90" align="right">
              <template #default="{ row }">{{ row.restock.suggestedRestock }}</template>
            </el-table-column>
            <el-table-column label="原因" min-width="120">
              <template #default="{ row }">
                可售 {{ row.restock.coverDays }} 天
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
