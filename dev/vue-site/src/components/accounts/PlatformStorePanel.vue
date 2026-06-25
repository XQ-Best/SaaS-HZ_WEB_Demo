<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Key, Lock, Plus, Shop, User } from '@element-plus/icons-vue'
import {
  bindPlatformStoresBatch,
  deletePlatformStore,
  fetchPlatformStores,
} from '@/api/platformAccounts'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  platform: { type: String, required: true },
  label: { type: String, required: true },
  desc: { type: String, default: '' },
  tagType: { type: String, default: 'primary' },
})

const draftRules = {
  storeName: [{ required: true, message: '请填写店铺名称', trigger: 'blur' }],
  account: [{ required: true, message: '请填写登录账号', trigger: 'blur' }],
  password: [{ required: true, message: '请填写登录密码', trigger: 'blur' }],
}

const auth = useAuthStore()
const loading = ref(false)
const boundStores = ref([])
const draftStores = reactive([])
const draftFormRefs = ref({})

const storeCount = computed(() => boundStores.value.length)

function setDraftFormRef(key, el) {
  if (el) {
    draftFormRefs.value[key] = el
  } else {
    delete draftFormRefs.value[key]
  }
}

function createDraft() {
  return {
    key: `draft_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
    storeName: '',
    account: '',
    password: '',
  }
}

async function appendDraft({ notify = false } = {}) {
  const draft = createDraft()
  draftStores.push(draft)
  await nextTick()
  if (notify) {
    draftFormRefs.value[draft.key]?.$el?.scrollIntoView?.({ behavior: 'smooth', block: 'nearest' })
    ElMessage.success(`已添加店铺 ${draftStores.length}`)
  }
  return draft
}

function addDraft() {
  appendDraft({ notify: true })
}

function removeDraft(key) {
  const index = draftStores.findIndex((d) => d.key === key)
  if (index !== -1) draftStores.splice(index, 1)
  delete draftFormRefs.value[key]
}

async function loadStores() {
  try {
    const res = await fetchPlatformStores(props.platform)
    boundStores.value = res.data || []
  } catch {
    boundStores.value = []
  }
}

async function validateDrafts() {
  if (!draftStores.length) {
    ElMessage.warning('请先添加店铺')
    return false
  }

  for (const row of draftStores) {
    const form = draftFormRefs.value[row.key]
    if (!form) continue
    try {
      await form.validate()
    } catch {
      ElMessage.warning('请完善标红字段后再保存')
      form.$el?.scrollIntoView?.({ behavior: 'smooth', block: 'nearest' })
      return false
    }
  }
  return true
}

async function submitDrafts() {
  if (!(await validateDrafts())) return

  loading.value = true
  try {
    const res = await bindPlatformStoresBatch({
      companyName: auth.company.name,
      stores: draftStores.map((row) => ({
        platform: props.platform,
        storeName: row.storeName.trim(),
        account: row.account.trim(),
        password: row.password,
      })),
    })
    draftStores.splice(0, draftStores.length)
    draftFormRefs.value = {}
    await appendDraft()
    await loadStores()
    ElMessage.success(res.message || '绑定成功')
  } catch (err) {
    ElMessage.error(err.message || '绑定失败')
  } finally {
    loading.value = false
  }
}

async function removeBoundStore(row) {
  try {
    await ElMessageBox.confirm(`确定解除「${row.storeName}」的绑定？`, '解除绑定', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  loading.value = true
  try {
    await deletePlatformStore(row.id)
    await loadStores()
    ElMessage.success('已解除绑定')
  } catch (err) {
    ElMessage.error(err.message || '操作失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStores()
  appendDraft()
})

defineExpose({ loadStores, storeCount })
</script>

<template>
  <el-card shadow="never" class="platform-panel">
    <template #header>
      <el-space wrap>
        <el-tag :type="tagType" effect="plain">{{ label }}</el-tag>
        <el-tag type="info" size="small">已绑定 {{ storeCount }} 个店铺</el-tag>
      </el-space>
    </template>

    <el-text size="small" type="info">{{ desc }}</el-text>

    <el-table
      v-if="boundStores.length"
      :data="boundStores"
      size="small"
      stripe
      style="margin-top: 12px"
    >
      <el-table-column prop="storeName" label="店铺名称" min-width="120" />
      <el-table-column prop="account" label="登录账号" min-width="140" show-overflow-tooltip />
      <el-table-column label="登录密码" min-width="140">
        <template #default="{ row }">
          <el-input
            :model-value="row.password || ''"
            type="password"
            show-password
            readonly
            size="small"
            placeholder="—"
          />
        </template>
      </el-table-column>
      <el-table-column prop="boundAt" label="绑定时间" width="170" />
      <el-table-column label="操作" width="90" fixed="right">
        <template #default="{ row }">
          <el-button link type="danger" :icon="Delete" @click="removeBoundStore(row)">
            解除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-else description="暂无绑定店铺" :image-size="64" />

    <el-divider content-position="left">添加店铺</el-divider>

    <div v-for="(row, index) in draftStores" :key="row.key" class="draft-block">
      <div class="draft-head">
        <el-text tag="b">店铺 {{ index + 1 }}</el-text>
        <el-button
          v-if="draftStores.length > 1"
          link
          type="danger"
          :icon="Delete"
          @click="removeDraft(row.key)"
        >
          移除
        </el-button>
      </div>

      <el-form
        :ref="(el) => setDraftFormRef(row.key, el)"
        :model="row"
        :rules="draftRules"
        label-position="top"
      >
        <el-form-item label="店铺名称" prop="storeName" required>
          <el-input
            v-model="row.storeName"
            :prefix-icon="Shop"
            placeholder="例如：Temu 美国全托管一店"
          />
        </el-form-item>
        <el-form-item label="登录账号" prop="account" required>
          <el-input
            v-model="row.account"
            :prefix-icon="User"
            placeholder="平台登录账号 / 邮箱"
            autocomplete="off"
          />
        </el-form-item>
        <el-form-item label="登录密码" prop="password" required>
          <el-input
            v-model="row.password"
            type="password"
            show-password
            :prefix-icon="Lock"
            placeholder="平台登录密码"
            autocomplete="new-password"
          />
        </el-form-item>
      </el-form>
    </div>

    <el-space wrap>
      <el-button native-type="button" :icon="Plus" @click="addDraft">添加店铺</el-button>
      <el-button
        native-type="button"
        type="primary"
        :icon="Key"
        :loading="loading"
        @click="submitDrafts"
      >
        保存 {{ label }} 店铺
      </el-button>
    </el-space>
  </el-card>
</template>

<style scoped>
.platform-panel {
  height: 100%;
}

.draft-block {
  margin-bottom: 16px;
  padding: 16px;
  border: 1px dashed var(--el-border-color);
  border-radius: 8px;
  background: var(--el-fill-color-blank);
}

.draft-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
</style>
