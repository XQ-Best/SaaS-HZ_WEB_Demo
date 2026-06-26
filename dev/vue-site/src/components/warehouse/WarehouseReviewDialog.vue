<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { emptyReviewForm } from '@/utils/warehouseOrders'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  order: { type: Object, default: null },
})

const emit = defineEmits(['update:modelValue', 'submit'])

const formRef = ref(null)
const form = reactive(emptyReviewForm())

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const rules = {
  reviewRemark: [{ required: true, message: '请填写审批反馈说明', trigger: 'blur' }],
  estimatedShipAt: [{
    validator: (_rule, value, callback) => {
      if (form.canShip && !value) callback(new Error('可发货时请填写预计出库时间'))
      else callback()
    },
    trigger: 'change',
  }],
}

watch(dialogVisible, (open) => {
  if (open) Object.assign(form, emptyReviewForm())
})

async function handleSubmit() {
  await formRef.value?.validate()
  emit('submit', { ...form })
}
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    :title="`仓库审批 · ${order?.orderNo || ''}`"
    width="640px"
    destroy-on-close
  >
    <el-alert
      type="info"
      :closable="false"
      show-icon
      title="请向运营反馈：是否可发、预计出库时间、缺料/包装/追加订货等情况。"
      style="margin-bottom: 16px"
    />

    <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
      <el-form-item label="审批结论">
        <el-radio-group v-model="form.canShip">
          <el-radio-button :value="true">可发货</el-radio-button>
          <el-radio-button :value="false">暂不可发</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <el-form-item v-if="form.canShip" label="预计出库" prop="estimatedShipAt">
        <el-date-picker
          v-model="form.estimatedShipAt"
          type="date"
          value-format="YYYY-MM-DD"
          placeholder="选择预计出库日期"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item v-if="!form.canShip" label="缺少材料">
        <el-input
          v-model="form.missingMaterials"
          type="textarea"
          :rows="2"
          placeholder="如：外箱库存不足、标签纸缺货等"
        />
      </el-form-item>

      <el-form-item label="包装说明">
        <el-input
          v-model="form.packagingNotes"
          type="textarea"
          :rows="2"
          placeholder="特殊包装、贴标、缠膜等要求或问题"
        />
      </el-form-item>

      <el-form-item label="追加订货">
        <el-input
          v-model="form.extraOrderNotes"
          type="textarea"
          :rows="2"
          placeholder="如需向供应商追加包材/原料，请说明"
        />
      </el-form-item>

      <el-form-item label="综合反馈" prop="reviewRemark">
        <el-input
          v-model="form.reviewRemark"
          type="textarea"
          :rows="3"
          placeholder="给运营的整体反馈，提交后订单将更新状态并通知下单人"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">
        {{ form.canShip ? '确认 · 进入待发货' : '提交 · 标记暂不可发' }}
      </el-button>
    </template>
  </el-dialog>
</template>
