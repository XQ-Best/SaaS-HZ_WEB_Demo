<script setup>
defineProps({
  name: { type: String, default: '未分配' },
  role: { type: String, default: '' },
  showRole: { type: Boolean, default: false },
})
</script>

<template>
  <span class="assignee-tag">
    <el-tag
      size="small"
      effect="plain"
      round
      :type="name === '未分配' ? 'info' : undefined"
      class="assignee-tag__pill"
    >
      {{ name }}
    </el-tag>
    <el-text v-if="showRole && role" size="small" type="info">{{ role }}</el-text>
  </span>
</template>

<style scoped>
.assignee-tag {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

.assignee-tag__pill {
  font-weight: 500;
  border-color: var(--ch-border);
}
</style>
