<script setup>
import { computed } from 'vue'
import { OfficeBuilding } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { formatWarehouseScopeText } from '@/utils/warehouseScope'

const props = defineProps({
  variant: {
    type: String,
    default: 'sidebar',
    validator: (value) => ['sidebar', 'inline', 'alert'].includes(value),
  },
})

const auth = useAuthStore()

const labels = computed(() => auth.assignedWarehouseLabels)
const hasScope = computed(() => auth.isWarehouse && labels.value.length > 0)
const emptyScope = computed(() => auth.isWarehouse && !labels.value.length)
const summaryText = computed(() => formatWarehouseScopeText(labels.value))
</script>

<template>
  <div
    v-if="auth.isWarehouse && (hasScope || emptyScope)"
    class="warehouse-scope"
    :class="[`warehouse-scope--${variant}`]"
  >
    <template v-if="variant === 'alert'">
      <el-alert
        v-if="hasScope"
        type="info"
        :closable="false"
        show-icon
        class="warehouse-scope__alert"
      >
        <template #title>
          当前账号负责仓库：<strong>{{ summaryText }}</strong>
        </template>
        <template #default>
          列表仅展示以上分仓的出库单；其他仓库订单不可见。
        </template>
      </el-alert>
      <el-alert
        v-else
        type="warning"
        :closable="false"
        show-icon
        title="尚未分配负责仓库，请联系企业管理员在「仓库人员」中配置。"
      />
    </template>

    <template v-else-if="variant === 'inline'">
      <span v-if="hasScope" class="warehouse-scope__inline">
        负责仓库：<strong>{{ summaryText }}</strong>
      </span>
      <span v-else class="warehouse-scope__inline warehouse-scope__inline--warn">
        未分配负责仓库
      </span>
    </template>

    <template v-else>
      <div class="warehouse-scope__head">
        <el-icon><OfficeBuilding /></el-icon>
        <span>负责仓库</span>
      </div>
      <div v-if="hasScope" class="warehouse-scope__tags">
        <el-tag
          v-for="name in labels"
          :key="name"
          size="small"
          effect="plain"
          type="primary"
        >
          {{ name }}
        </el-tag>
      </div>
      <p v-else class="warehouse-scope__empty">未分配，请联系管理员</p>
    </template>
  </div>
</template>

<style scoped>
.warehouse-scope--sidebar {
  margin: 10px 10px 0;
  padding: 10px 12px;
  border: 1px solid var(--ch-border);
  border-radius: var(--ch-radius-md);
  background: var(--ch-surface);
}

.warehouse-scope__head {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  color: var(--ch-text-muted);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.warehouse-scope__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.warehouse-scope__empty {
  margin: 0;
  font-size: 12px;
  color: var(--ch-warning, #e6a23c);
  line-height: 1.4;
}

.warehouse-scope--inline .warehouse-scope__inline {
  font-size: 12px;
  color: var(--ch-text-muted);
}

.warehouse-scope--inline .warehouse-scope__inline strong {
  color: var(--ch-primary);
  font-weight: 600;
}

.warehouse-scope--inline .warehouse-scope__inline--warn {
  color: var(--ch-warning, #e6a23c);
}

.warehouse-scope__alert :deep(.el-alert__title) {
  font-size: 13px;
}

.warehouse-scope__alert :deep(.el-alert__description) {
  margin-top: 4px;
  font-size: 12px;
}
</style>
