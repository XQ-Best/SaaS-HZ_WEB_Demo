<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
})
</script>

<template>
  <div class="page-header">
    <div class="page-header__main">
      <h3 class="ch-page-title">{{ title }}</h3>
      <el-text v-if="description" class="page-header__desc" type="info">{{ description }}</el-text>
    </div>
    <div v-if="$slots.actions" class="actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.page-header__desc {
  display: block;
  margin-top: 4px;
  font-size: 13px;
  line-height: 1.5;
  color: var(--ch-text-muted);
}

.actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
</style>
