<script setup>
import AssigneeTag from '@/components/common/AssigneeTag.vue'

defineProps({
  width: { type: [Number, String], default: 96 },
  fixed: { type: [Boolean, String], default: false },
  label: { type: String, default: '负责人' },
  showRole: { type: Boolean, default: false },
})
</script>

<template>
  <el-table-column :label="label" :width="width" :fixed="fixed" show-overflow-tooltip>
    <template #default="{ row }">
      <AssigneeTag
        :name="row.assigneeName || '未分配'"
        :role="row.assigneeRole"
        :show-role="showRole"
      />
    </template>
  </el-table-column>
</template>
