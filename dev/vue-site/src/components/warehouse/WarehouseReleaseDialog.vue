<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { emptyReleaseForm } from '@/utils/warehouseOrders'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  order: { type: Object, default: null },
})

const emit = defineEmits(['update:modelValue', 'submit'])

const formRef = ref(null)
const form = reactive(emptyReleaseForm())

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const rules = {
  estimatedShipAt: [{ required: true, message: '请填写预计出库时间', trigger: 'change' }],
  releaseRemark: [{ required: true, message: '请填写补货/可发说明', trigger: 'blur' }],
}

watch(dialogVisible, (open) => {
  if (open) Object.assign(form, emptyReleaseForm())
})

async function handleSubmit() {
  await formRef.value?.validate()
  emit('submit', { ...form })
}
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    :title="`确认可发 · ${order?.orderNo || ''}`"
    width="560px"
    destroy-on-close
  >
    <el-alert
      type="success"
      :closable="false"
      show-icon
      title="包材/原料已到位后，确认订单进入待发货，后续可执行出库。"
      style="margin-bottom: 16px"
    />

    <div v-if="order?.warehouseReview?.missingMaterials" class="prior-block">
      <span class="prior-label">此前缺料说明</span>
      <p>{{ order.warehouseReview.missingMaterials }}</p>
      <p v-if="order.warehouseReview.extraOrderNotes" class="prior-extra">
        {{ order.warehouseReview.extraOrderNotes }}
      </p>
    </div>

    <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
      <el-form-item label="预计出库" prop="estimatedShipAt">
        <el-date-picker
          v-model="form.estimatedShipAt"
          type="date"
          value-format="YYYY-MM-DD"
          placeholder="选择预计出库日期"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="可发说明" prop="releaseRemark">
        <el-input
          v-model="form.releaseRemark"
          type="textarea"
          :rows="3"
          placeholder="如：外箱与标签已到货，可安排出库"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="success" @click="handleSubmit">确认 · 进入待发货</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.prior-block {
  margin-bottom: 16px;
  padding: 12px 14px;
  border-radius: var(--ch-radius-md);
  background: var(--el-fill-color-light);
  font-size: 13px;
}

.prior-label {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--ch-text-muted);
}

.prior-block p {
  margin: 0;
  color: var(--ch-text);
}

.prior-extra {
  margin-top: 6px !important;
  color: var(--ch-text-muted);
}
</style>
