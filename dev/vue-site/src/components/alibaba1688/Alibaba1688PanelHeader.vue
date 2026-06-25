<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  syncedAt: { type: String, default: '' },
  actionLabel: { type: String, default: '' },
  loading: { type: Boolean, default: false },
})

defineEmits(['action'])
</script>

<template>
  <div class="panel-header">
    <div>
      <strong>{{ title }}</strong>
      <el-text v-if="description" size="small" type="info" tag="p">{{ description }}</el-text>
    </div>
    <el-space>
      <el-text v-if="syncedAt" size="small" type="info">同步于 {{ syncedAt }}</el-text>
      <el-button
        v-if="actionLabel"
        type="primary"
        size="small"
        :loading="loading"
        @click="$emit('action')"
      >
        {{ actionLabel }}
      </el-button>
    </el-space>
  </div>
</template>

<style scoped>
.panel-header {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: flex-start;
  justify-content: space-between;
}

.panel-header p {
  margin: 4px 0 0;
}
</style>
