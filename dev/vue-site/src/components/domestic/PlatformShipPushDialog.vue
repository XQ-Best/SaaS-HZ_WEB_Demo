<script setup>
import { computed, ref, watch } from 'vue'
import { Van, WarningFilled } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { fetchWarehouseSites } from '@/api/warehouseSites'
import { SHIP_REQUEST_TYPES } from '@/constants/platformShipRequests'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  order: { type: Object, default: null },
  platformKey: { type: String, default: '' },
  platformLabel: { type: String, default: '' },
  storeName: { type: String, default: '' },
  requestType: { type: String, default: 'push' },
  submitting: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'submit'])

const auth = useAuthStore()
const warehouseId = ref('')
const remark = ref('')
const sites = ref([])
const loadingSites = ref(false)

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const isUrge = computed(() => props.requestType === 'urge')
const typeMeta = computed(() => SHIP_REQUEST_TYPES[props.requestType] || SHIP_REQUEST_TYPES.push)

const dialogTitle = computed(() =>
  isUrge.value ? '催促仓库发货' : '推送订单至仓库发货',
)

async function loadSites() {
  loadingSites.value = true
  try {
    const res = await fetchWarehouseSites(auth, { activeOnly: true })
    sites.value = res.data || []
    if (!isUrge.value && sites.value.length && !warehouseId.value) {
      warehouseId.value = sites.value[0].id
    }
    if (isUrge.value && props.order?.warehouseId) {
      warehouseId.value = props.order.warehouseId
    }
  } catch {
    sites.value = []
  } finally {
    loadingSites.value = false
  }
}

watch(
  () => [visible.value, props.order?.id, props.requestType],
  ([open]) => {
    if (open) {
      remark.value = ''
      warehouseId.value = props.order?.warehouseId || ''
      loadSites()
    }
  },
)

function handleSubmit() {
  emit('submit', {
    warehouseId: isUrge.value ? props.order?.warehouseId : warehouseId.value,
    type: props.requestType,
    remark: remark.value.trim(),
  })
}
</script>

<template>
  <el-dialog
    v-model="visible"
    :title="dialogTitle"
    width="480px"
    align-center
    destroy-on-close
    :close-on-click-modal="!submitting"
  >
    <template v-if="order">
      <div class="order-card">
        <div class="order-card__tags">
          <el-tag size="small" effect="plain">{{ platformLabel || platformKey }}</el-tag>
          <el-tag :type="typeMeta.tag" size="small">{{ typeMeta.label }}</el-tag>
        </div>
        <strong>{{ order.orderNo }}</strong>
        <p>{{ order.productName }}</p>
        <p v-if="storeName" class="order-card__meta">店铺：{{ storeName }}</p>
        <p v-if="order.shipDeadline" class="order-card__meta">发货截止：{{ order.shipDeadline }}</p>
        <p v-else-if="order.expectedShipAt" class="order-card__meta">预计发货：{{ order.expectedShipAt }}</p>
        <p v-if="isUrge && order.warehouseName" class="order-card__meta">
          已分配仓库：<strong>{{ order.warehouseName }}</strong>
          <span v-if="order.warehouseOrderNo"> · 出库单 {{ order.warehouseOrderNo }}</span>
        </p>
      </div>

      <el-alert
        v-if="isUrge"
        type="warning"
        :closable="false"
        show-icon
        class="hint-alert"
        title="将向该仓库发送催促通知"
        description="仓管可在「待审核 / 待发货」中看到催促记录与备注。"
      />
      <el-alert
        v-else
        type="info"
        :closable="false"
        show-icon
        class="hint-alert"
        title="推送后将生成本地出库单"
        description="仓库侧栏「待审核」会出现该订单，审核通过后可安排发货。"
      />

      <el-form v-loading="loadingSites" label-width="88px" class="ship-form">
        <el-form-item v-if="!isUrge" label="出库仓库" required>
          <el-select v-model="warehouseId" placeholder="选择负责发货的仓库" style="width: 100%">
            <el-option
              v-for="site in sites"
              :key="site.id"
              :label="site.name"
              :value="site.id"
            >
              <span>{{ site.name }}</span>
              <span v-if="site.address" class="site-option-addr">{{ site.address }}</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item :label="isUrge ? '催促说明' : '推送说明'">
          <el-input
            v-model="remark"
            type="textarea"
            :rows="3"
            :placeholder="isUrge
              ? '说明紧急程度、平台 SLA 或客户催单原因…'
              : '补充打包要求、物流偏好或平台发货备注…'"
          />
        </el-form-item>
      </el-form>
    </template>

    <template #footer>
      <el-button :disabled="submitting" @click="visible = false">取消</el-button>
      <el-button
        :type="isUrge ? 'warning' : 'primary'"
        :loading="submitting"
        :icon="isUrge ? WarningFilled : Van"
        @click="handleSubmit"
      >
        {{ isUrge ? '发送催促' : '确认推送' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.order-card {
  margin-bottom: 14px;
  padding: 14px 16px;
  border: 1px solid var(--ch-border);
  border-left: 3px solid var(--ch-primary);
  border-radius: var(--ch-radius-md);
  background: var(--ch-surface-muted);
}

.order-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.order-card strong {
  font-size: 15px;
  color: var(--ch-text);
}

.order-card p {
  margin: 6px 0 0;
  font-size: 13px;
  color: var(--ch-text-secondary);
}

.order-card__meta {
  font-size: 12px !important;
  color: var(--ch-text-muted) !important;
}

.hint-alert {
  margin-bottom: 16px;
}

.ship-form {
  margin-top: 4px;
}

.site-option-addr {
  margin-left: 8px;
  font-size: 12px;
  color: var(--ch-text-muted);
}
</style>
