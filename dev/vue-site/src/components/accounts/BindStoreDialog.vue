<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { bindPlatformStore } from '@/api/platformAccounts'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  visible: { type: Boolean, default: false },
  defaultPlatform: { type: String, default: 'temu' },
})

const emit = defineEmits(['update:visible', 'success'])

const auth = useAuthStore()
const formRef = ref(null)
const submitting = ref(false)

const platformGroups = [
  {
    label: '跨境平台',
    options: [
      { value: 'temu', label: 'Temu' },
      { value: 'aliexpress', label: 'AliExpress' },
      { value: 'amazon', label: 'Amazon' },
      { value: 'walmart', label: 'Walmart' },
    ],
  },
  {
    label: '国内电商',
    options: [
      { value: 'pdd', label: '拼多多' },
      { value: 'douyin', label: '抖音' },
      { value: 'channels', label: '视频号' },
    ],
  },
  {
    label: '供应链',
    options: [{ value: '1688', label: '1688' }],
  },
  {
    label: '独立站',
    options: [
      { value: 'shopify', label: 'Shopify' },
      { value: 'wordpress', label: 'WordPress' },
    ],
  },
]

const form = reactive({
  platform: 'temu',
  storeName: '',
  account: '',
  password: '',
})

const rules = {
  platform: [{ required: true, message: '请选择平台', trigger: 'change' }],
  storeName: [{ required: true, message: '请填写店铺名称', trigger: 'blur' }],
  account: [{ required: true, message: '请填写登录账号', trigger: 'blur' }],
  password: [{ required: true, message: '请填写登录密码', trigger: 'blur' }],
}

const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value),
})

function resetForm() {
  form.platform = props.defaultPlatform || 'temu'
  form.storeName = ''
  form.account = ''
  form.password = ''
  formRef.value?.clearValidate?.()
}

async function submit() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    const res = await bindPlatformStore({
      companyName: auth.company.name,
      platform: form.platform,
      storeName: form.storeName.trim(),
      account: form.account.trim(),
      password: form.password,
    })
    ElMessage.success(res.message || '绑定成功')
    emit('success')
    dialogVisible.value = false
  } catch (err) {
    ElMessage.error(err.message || '绑定失败')
  } finally {
    submitting.value = false
  }
}

watch(
  () => props.visible,
  (open) => {
    if (open) resetForm()
  },
)
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    title="绑定店铺"
    width="440px"
    destroy-on-close
    @closed="resetForm"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px" class="bind-form">
      <el-form-item label="平台" prop="platform">
        <el-select v-model="form.platform" placeholder="选择平台" style="width: 100%">
          <el-option-group v-for="group in platformGroups" :key="group.label" :label="group.label">
            <el-option
              v-for="item in group.options"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-option-group>
        </el-select>
      </el-form-item>
      <el-form-item label="店铺名称" prop="storeName">
        <el-input v-model="form.storeName" placeholder="便于识别的名称，如 Temu 美国一店" />
      </el-form-item>
      <el-form-item label="登录账号" prop="account">
        <el-input v-model="form.account" placeholder="平台登录账号 / 邮箱" autocomplete="off" />
      </el-form-item>
      <el-form-item label="登录密码" prop="password">
        <el-input
          v-model="form.password"
          type="password"
          show-password
          placeholder="平台登录密码"
          autocomplete="new-password"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">确认绑定</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.bind-form {
  padding-top: 4px;
}
</style>
