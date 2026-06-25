<script setup>
import { Refresh } from '@element-plus/icons-vue'

defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  syncedAt: { type: String, default: '' },
  actionLabel: { type: String, default: '刷新' },
  loading: { type: Boolean, default: false },
})

defineEmits(['action'])
</script>

<template>
  <div class="panel-header">
    <div class="panel-header__main">
      <div class="panel-header__title">{{ title }}</div>
      <div v-if="description" class="panel-header__desc">{{ description }}</div>
    </div>
    <div class="panel-header__actions">
      <el-text v-if="syncedAt" size="small" type="info">最近同步 {{ syncedAt }}</el-text>
      <el-button type="primary" :icon="Refresh" :loading="loading" @click="$emit('action')">
        {{ actionLabel }}
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.panel-header {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 16px;
  align-items: flex-start;
  justify-content: space-between;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.panel-header__title {
  font-size: 15px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.panel-header__desc {
  margin-top: 4px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.panel-header__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}
</style>
