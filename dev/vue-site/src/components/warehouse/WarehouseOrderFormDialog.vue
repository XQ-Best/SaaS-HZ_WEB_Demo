<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Box,
  Close,
  Delete,
  Document,
  Plus,
  PriceTag,
  Shop,
  UploadFilled,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { fetchWarehouseSites } from '@/api/warehouseSites'
import {
  ATTACHMENT_ACCEPT,
  MARK_LABEL_ACCEPT,
  MARKETPLACE_SOURCE_OPTIONS,
  SOURCE_TYPE_OPTIONS,
} from '@/constants/warehouseOrders'
import { attachmentFromUpload, emptyOrderForm } from '@/utils/warehouseOrders'
import WarehouseUploadCard from '@/components/warehouse/WarehouseUploadCard.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'submit'])

const auth = useAuthStore()
const formRef = ref(null)
const uploadList = ref([])
const cartonMarkUploadList = ref([])
const labelUploadList = ref([])
const warehouseSites = ref([])
const form = reactive(emptyOrderForm())

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const totalFiles = computed(
  () => uploadList.value.length + cartonMarkUploadList.value.length + labelUploadList.value.length,
)

const uploadedFileTags = computed(() => [
  ...uploadList.value.map((file) => ({ file, kind: '附件', listKey: 'attachments' })),
  ...cartonMarkUploadList.value.map((file) => ({ file, kind: '箱唛', listKey: 'cartonMarks' })),
  ...labelUploadList.value.map((file) => ({ file, kind: '标签', listKey: 'labels' })),
])

const rules = {
  warehouseId: [{ required: true, message: '请选择出库仓库', trigger: 'change' }],
  sourcePlatform: [{
    validator: (_rule, value, callback) => {
      if (form.sourceType === 'marketplace' && !value) callback(new Error('请选择电商平台'))
      else callback()
    },
    trigger: 'change',
  }],
  b2bCustomerName: [{
    validator: (_rule, value, callback) => {
      if (form.sourceType === 'b2b' && !value?.trim()) callback(new Error('请填写 B 端客户名称'))
      else callback()
    },
    trigger: 'blur',
  }],
}

watch(dialogVisible, async (open) => {
  if (open) {
    resetForm()
    try {
      const res = await fetchWarehouseSites(auth, { activeOnly: true })
      warehouseSites.value = res.data || []
      if (warehouseSites.value.length === 1) {
        form.warehouseId = warehouseSites.value[0].id
      }
    } catch {
      warehouseSites.value = []
    }
  }
})

function resetForm() {
  Object.assign(form, emptyOrderForm())
  uploadList.value = []
  cartonMarkUploadList.value = []
  labelUploadList.value = []
}

function setSourceType(value) {
  form.sourceType = value
}

function addLine() {
  form.items.push({
    id: `li_${Date.now()}`,
    productName: '',
    sku: '',
    quantity: 1,
    unit: '件',
  })
}

function removeLine(index) {
  if (form.items.length <= 1) {
    ElMessage.warning('至少保留一条货品明细')
    return
  }
  form.items.splice(index, 1)
}

function syncUploadFiles(fileList, targetKey) {
  form[targetKey] = fileList.map((item) =>
    item.response?.attachment || attachmentFromUpload(item.raw || item),
  )
}

function handleUploadChange(_file, fileList) {
  uploadList.value = fileList
  syncUploadFiles(fileList, 'attachments')
}

function handleUploadRemove(_file, fileList) {
  uploadList.value = fileList
  syncUploadFiles(fileList, 'attachments')
}

function handleCartonMarkChange(_file, fileList) {
  cartonMarkUploadList.value = fileList
  syncUploadFiles(fileList, 'cartonMarks')
}

function handleCartonMarkRemove(_file, fileList) {
  cartonMarkUploadList.value = fileList
  syncUploadFiles(fileList, 'cartonMarks')
}

function handleLabelChange(_file, fileList) {
  labelUploadList.value = fileList
  syncUploadFiles(fileList, 'labels')
}

function handleLabelRemove(_file, fileList) {
  labelUploadList.value = fileList
  syncUploadFiles(fileList, 'labels')
}

function removeUploadedFile(entry) {
  const { file, listKey } = entry
  if (listKey === 'attachments') {
    handleUploadRemove(file, uploadList.value.filter((item) => item.uid !== file.uid))
  } else if (listKey === 'cartonMarks') {
    handleCartonMarkRemove(file, cartonMarkUploadList.value.filter((item) => item.uid !== file.uid))
  } else {
    handleLabelRemove(file, labelUploadList.value.filter((item) => item.uid !== file.uid))
  }
}

async function handleSubmit() {
  await formRef.value?.validate()
  emit('submit', {
    warehouseId: form.warehouseId,
    sourceType: form.sourceType,
    sourcePlatform: form.sourcePlatform,
    sourceStoreName: form.sourceStoreName,
    b2bCustomerName: form.b2bCustomerName,
    remark: form.remark,
    items: form.items.map((row) => ({ ...row })),
    attachments: [...form.attachments],
    cartonMarks: [...form.cartonMarks],
    labels: [...form.labels],
  })
}
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    width="780px"
    align-center
    destroy-on-close
    class="wh-order-dialog"
    :show-close="true"
  >
    <template #header>
      <div class="wh-head">
        <div class="wh-head__icon">
          <el-icon><Box /></el-icon>
        </div>
        <div class="wh-head__text">
          <h3>新建仓库出库单</h3>
          <p>提交后由仓库审核，反馈是否可发及预计出库时间</p>
        </div>
      </div>
    </template>

    <el-form ref="formRef" :model="form" :rules="rules" class="wh-form" @submit.prevent>
      <section class="wh-panel">
        <div class="wh-panel__title">
          <span class="wh-panel__dot" />出库仓库
        </div>
        <el-form-item prop="warehouseId" label-width="0" class="wh-form-item--full">
          <el-select
            v-model="form.warehouseId"
            placeholder="选择目标仓库"
            style="width: 100%"
          >
            <el-option
              v-for="site in warehouseSites"
              :key="site.id"
              :label="site.name"
              :value="site.id"
            >
              <span>{{ site.name }}</span>
              <span v-if="site.address" class="site-option-sub">{{ site.address }}</span>
            </el-option>
          </el-select>
        </el-form-item>
      </section>

      <!-- 货源 -->
      <section class="wh-panel">
        <div class="wh-panel__title">
          <span class="wh-panel__dot" />货源
        </div>

        <div class="type-pick">
          <button
            v-for="opt in SOURCE_TYPE_OPTIONS"
            :key="opt.value"
            type="button"
            class="type-pick__item"
            :class="{ 'is-active': form.sourceType === opt.value }"
            @click="setSourceType(opt.value)"
          >
            <el-icon v-if="opt.value === 'marketplace'"><Shop /></el-icon>
            <el-icon v-else><Box /></el-icon>
            {{ opt.label }}
          </button>
        </div>

        <div v-if="form.sourceType === 'marketplace'" class="wh-fields wh-fields--2">
          <el-form-item label="电商平台" prop="sourcePlatform">
            <el-select v-model="form.sourcePlatform" placeholder="选择平台">
              <el-option
                v-for="opt in MARKETPLACE_SOURCE_OPTIONS"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="店铺 / 站点">
            <el-input v-model="form.sourceStoreName" placeholder="如：亿拓户外旗舰店" />
          </el-form-item>
        </div>
        <el-form-item v-else label="B 端客户" prop="b2bCustomerName">
          <el-input v-model="form.b2bCustomerName" placeholder="客户公司全称" />
        </el-form-item>
      </section>

      <!-- 货品 -->
      <section class="wh-panel">
        <div class="wh-panel__head">
          <div class="wh-panel__title">
            <span class="wh-panel__dot" />货品明细
          </div>
          <button type="button" class="wh-link-btn" @click="addLine">
            <el-icon><Plus /></el-icon>添加一行
          </button>
        </div>

        <div class="item-grid item-grid--head">
          <span>货品名称</span>
          <span>SKU</span>
          <span>数量</span>
          <span>单位</span>
          <span />
        </div>
        <div v-for="(row, index) in form.items" :key="row.id" class="item-grid">
          <el-input v-model="row.productName" placeholder="名称" size="default" />
          <el-input v-model="row.sku" placeholder="SKU" size="default" />
          <el-input-number
            v-model="row.quantity"
            :min="1"
            :max="999999"
            size="default"
            controls-position="right"
          />
          <el-input v-model="row.unit" placeholder="件" size="default" />
          <button
            type="button"
            class="item-grid__del"
            :disabled="form.items.length <= 1"
            @click="removeLine(index)"
          >
            <el-icon><Delete /></el-icon>
          </button>
        </div>
      </section>

      <!-- 备注 + 资料 -->
      <section class="wh-panel wh-panel--last">
        <div class="wh-panel__title">
          <span class="wh-panel__dot" />补充说明
        </div>

        <el-form-item label="备注" class="wh-remark">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="2"
            resize="none"
            placeholder="包装要求、发货优先级、特殊说明…"
          />
        </el-form-item>

        <div class="wh-upload-label">
          资料附件
          <span v-if="totalFiles" class="wh-upload-count">已选 {{ totalFiles }} 个</span>
        </div>
        <div class="wh-upload-row">
          <WarehouseUploadCard
            title="附件"
            sub="清单 / 合同"
            :accept="ATTACHMENT_ACCEPT"
            :file-list="uploadList"
            @change="handleUploadChange"
            @remove="handleUploadRemove"
          >
            <template #icon><Document /></template>
          </WarehouseUploadCard>
          <WarehouseUploadCard
            title="箱唛"
            sub="外箱 / FBA"
            optional
            :accept="MARK_LABEL_ACCEPT"
            :file-list="cartonMarkUploadList"
            @change="handleCartonMarkChange"
            @remove="handleCartonMarkRemove"
          >
            <template #icon><UploadFilled /></template>
          </WarehouseUploadCard>
          <WarehouseUploadCard
            title="标签"
            sub="FNSKU / 条码"
            optional
            :accept="MARK_LABEL_ACCEPT"
            :file-list="labelUploadList"
            @change="handleLabelChange"
            @remove="handleLabelRemove"
          >
            <template #icon><PriceTag /></template>
          </WarehouseUploadCard>
        </div>
        <div v-if="uploadedFileTags.length" class="wh-upload-files">
          <span
            v-for="entry in uploadedFileTags"
            :key="`${entry.kind}-${entry.file.uid || entry.file.name}`"
            class="wh-upload-tag"
            :title="entry.file.name"
          >
            <em>{{ entry.kind }}</em>
            {{ entry.file.name }}
            <button type="button" class="wh-upload-tag__x" @click="removeUploadedFile(entry)">
              <el-icon><Close /></el-icon>
            </button>
          </span>
        </div>
      </section>
    </el-form>

    <template #footer>
      <div class="wh-foot">
        <span class="wh-foot__hint">PDF · Word · Excel · 图片 · Demo 仅保存文件名</span>
        <div class="wh-foot__actions">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">提交审核</el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.wh-head {
  display: flex;
  align-items: center;
  gap: 12px;
}

.wh-head__icon {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: var(--ch-radius-md);
  background: linear-gradient(135deg, var(--ch-primary) 0%, #4080ff 100%);
  color: #fff;
  font-size: 20px;
  flex-shrink: 0;
}

.wh-head__text h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--ch-text);
  line-height: 1.3;
}

.wh-head__text p {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--ch-text-muted);
  line-height: 1.4;
}

.wh-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.wh-form :deep(.el-form-item__label) {
  padding-bottom: 4px;
  font-size: 12px;
  font-weight: 500;
  color: var(--ch-text-secondary);
  line-height: 1.2;
}

.wh-panel {
  padding-bottom: 14px;
  margin-bottom: 14px;
  border-bottom: 1px solid var(--ch-border);
}

.wh-panel--last {
  padding-bottom: 0;
  margin-bottom: 0;
  border-bottom: none;
}

.wh-panel__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.wh-panel__title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--ch-text);
}

.wh-panel__dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: var(--ch-primary);
}

.type-pick {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 12px;
}

.type-pick__item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 40px;
  border: 1px solid var(--ch-border);
  border-radius: var(--ch-radius-md);
  background: #fff;
  color: var(--ch-text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.18s ease;
}

.type-pick__item:hover {
  border-color: var(--ch-primary-muted);
  color: var(--ch-primary);
}

.type-pick__item.is-active {
  border-color: var(--ch-primary);
  background: var(--ch-primary-soft);
  color: var(--ch-primary);
  box-shadow: inset 0 0 0 1px rgba(22, 93, 255, 0.12);
}

.wh-fields {
  display: grid;
  gap: 10px 12px;
}

.wh-fields--2 {
  grid-template-columns: 1fr 1fr;
}

.wh-link-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0;
  border: none;
  background: none;
  color: var(--ch-primary);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
}

.wh-link-btn:hover {
  color: var(--ch-primary-hover);
}

.item-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr) 108px 64px 32px;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}

.item-grid--head {
  margin-bottom: 6px;
}

.item-grid--head span {
  font-size: 11px;
  font-weight: 500;
  color: var(--ch-text-muted);
  padding-left: 2px;
}

.item-grid :deep(.el-input-number) {
  width: 100%;
}

.item-grid__del {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border: none;
  border-radius: var(--ch-radius-sm);
  background: transparent;
  color: var(--ch-text-muted);
  cursor: pointer;
  transition: color 0.15s ease, background 0.15s ease;
}

.item-grid__del:hover:not(:disabled) {
  color: var(--ch-error);
  background: rgba(245, 63, 63, 0.08);
}

.item-grid__del:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.wh-remark {
  margin-bottom: 12px;
}

.wh-upload-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 500;
  color: var(--ch-text-secondary);
}

.wh-upload-count {
  font-size: 11px;
  font-weight: 400;
  color: var(--ch-primary);
}

.wh-upload-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  align-items: stretch;
}

.wh-upload-files {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
  min-height: 0;
}

.wh-upload-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  max-width: 100%;
  padding: 3px 6px 3px 8px;
  border-radius: 999px;
  background: #fff;
  border: 1px solid var(--ch-border);
  font-size: 11px;
  color: var(--ch-text-secondary);
}

.wh-upload-tag em {
  font-style: normal;
  font-size: 10px;
  font-weight: 600;
  color: var(--ch-primary);
}

.wh-upload-tag__x {
  display: grid;
  place-items: center;
  width: 16px;
  height: 16px;
  padding: 0;
  border: none;
  border-radius: 999px;
  background: transparent;
  color: var(--ch-text-muted);
  cursor: pointer;
}

.wh-upload-tag__x:hover {
  color: var(--ch-error);
  background: rgba(245, 63, 63, 0.1);
}

.wh-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
}

.wh-foot__hint {
  font-size: 11px;
  color: var(--ch-text-muted);
}

.wh-foot__actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
</style>

<style>
.wh-order-dialog.el-dialog {
  border-radius: var(--ch-radius-lg);
  overflow: hidden;
  box-shadow: var(--ch-shadow-lg);
}

.wh-order-dialog .el-dialog__header {
  margin: 0;
  padding: 18px 22px 14px;
  border-bottom: 1px solid var(--ch-border);
}

.wh-order-dialog .el-dialog__body {
  padding: 16px 22px 8px;
  overflow: hidden;
  background: var(--ch-layout-bg);
}

.wh-order-dialog .el-dialog__footer {
  padding: 12px 22px 16px;
  border-top: 1px solid var(--ch-border);
  background: #fff;
}
</style>
