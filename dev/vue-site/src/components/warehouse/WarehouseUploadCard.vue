<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, required: true },
  sub: { type: String, default: '' },
  optional: { type: Boolean, default: false },
  accept: { type: String, default: '' },
  fileList: { type: Array, default: () => [] },
})

const emit = defineEmits(['change', 'remove'])

const count = computed(() => props.fileList.length)

function onChange(file, list) {
  emit('change', file, list)
}

function onRemove(file, list) {
  emit('remove', file, list)
}
</script>

<template>
  <div class="upload-slot" :class="{ 'is-active': count > 0 }">
    <el-upload
      multiple
      :auto-upload="false"
      :accept="accept"
      :file-list="fileList"
      :show-file-list="false"
      class="upload-slot__uploader"
      @change="onChange"
      @remove="onRemove"
    >
      <button type="button" class="upload-slot__btn">
        <span class="upload-slot__icon">
          <slot name="icon" />
        </span>
        <span class="upload-slot__label">{{ title }}</span>
        <span class="upload-slot__opt">{{ optional ? '选填' : '' }}</span>
        <span class="upload-slot__sub">{{ sub }}</span>
        <span v-if="count" class="upload-slot__badge">{{ count }}</span>
      </button>
    </el-upload>
  </div>
</template>

<style scoped>
.upload-slot {
  height: 92px;
  min-width: 0;
}

.upload-slot__uploader {
  width: 100%;
  height: 100%;
}

.upload-slot__uploader :deep(.el-upload) {
  width: 100%;
  height: 100%;
}

.upload-slot__btn {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  width: 100%;
  height: 92px;
  padding: 8px;
  border: 1px dashed var(--ch-border-strong);
  border-radius: var(--ch-radius-md);
  background: #fff;
  cursor: pointer;
  box-sizing: border-box;
  transition: border-color 0.18s ease, background 0.18s ease, box-shadow 0.18s ease;
}

.upload-slot__btn:hover,
.upload-slot.is-active .upload-slot__btn {
  border-color: var(--ch-primary-muted);
  background: var(--ch-primary-soft);
  box-shadow: var(--ch-shadow-xs);
}

.upload-slot__icon {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 999px;
  background: var(--ch-surface-muted);
  color: var(--ch-primary);
  font-size: 15px;
  flex-shrink: 0;
  transition: background 0.18s ease;
}

.upload-slot__btn:hover .upload-slot__icon,
.upload-slot.is-active .upload-slot__icon {
  background: #fff;
}

.upload-slot__label {
  font-size: 13px;
  font-weight: 600;
  color: var(--ch-text);
  line-height: 1.2;
}

.upload-slot__opt {
  min-height: 14px;
  font-size: 10px;
  color: var(--ch-text-muted);
  line-height: 14px;
}

.upload-slot__sub {
  font-size: 10px;
  color: var(--ch-text-muted);
  line-height: 1.2;
  text-align: center;
}

.upload-slot__badge {
  position: absolute;
  top: 6px;
  right: 6px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 999px;
  background: var(--ch-primary);
  color: #fff;
  font-size: 10px;
  font-weight: 600;
  line-height: 18px;
}
</style>
