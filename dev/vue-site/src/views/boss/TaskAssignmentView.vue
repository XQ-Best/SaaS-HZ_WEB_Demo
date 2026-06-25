<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Plus, Refresh } from '@element-plus/icons-vue'
import {
  assignTaskToEmployee,
  cancelAssignedTask,
  fetchAssignedTasks,
  removeAssignedTask,
  updateAssignedTask,
} from '@/api/assignedTasks'
import { fetchEmployees } from '@/api/employees'
import { TASK_STATUS_META } from '@/constants/operations'
import {
  TASK_CATEGORY_OPTIONS,
  TASK_DUE_OPTIONS,
  TASK_PLATFORM_OPTIONS,
  TASK_PRIORITY_OPTIONS,
  TASK_STATUS_OPTIONS,
} from '@/constants/assignedTasks'
import PageHeader from '@/components/common/PageHeader.vue'
import PageScroll from '@/components/common/PageScroll.vue'

const loading = ref(false)
const employees = ref([])
const tasks = ref([])
const dialogVisible = ref(false)
const submitting = ref(false)
const editingId = ref(null)
const filterEmployeeId = ref('all')
const filterStatus = ref('active')

const priorityMap = Object.fromEntries(TASK_PRIORITY_OPTIONS.map((item) => [item.value, item]))

const activeEmployees = computed(() => employees.value.filter((emp) => emp.status !== false))

const filteredTasks = computed(() => {
  let list = tasks.value
  if (filterEmployeeId.value !== 'all') {
    list = list.filter((task) => task.employeeId === filterEmployeeId.value)
  }
  if (filterStatus.value === 'active') {
    list = list.filter((task) => task.status !== '已完成' && task.status !== '已取消')
  } else if (filterStatus.value !== 'all') {
    list = list.filter((task) => task.status === filterStatus.value)
  }
  return list
})

const stats = computed(() => ({
  total: tasks.value.length,
  active: tasks.value.filter((t) => t.status !== '已完成' && t.status !== '已取消').length,
  done: tasks.value.filter((t) => t.status === '已完成').length,
}))

const form = reactive({
  employeeId: '',
  title: '',
  description: '',
  platformKey: 'temu',
  category: '运营',
  priority: 'medium',
  due: '今天 18:00',
})

const formRules = {
  employeeId: [{ required: true, message: '请选择员工', trigger: 'change' }],
  title: [{ required: true, message: '请填写任务标题', trigger: 'blur' }],
  platformKey: [{ required: true, message: '请选择平台', trigger: 'change' }],
}

const formRef = ref(null)

const dialogTitle = computed(() => (editingId.value ? '编辑任务' : '分配任务'))

function resetForm() {
  form.employeeId = activeEmployees.value[0]?.id || ''
  form.title = ''
  form.description = ''
  form.platformKey = 'temu'
  form.category = '运营'
  form.priority = 'medium'
  form.due = '今天 18:00'
  editingId.value = null
  formRef.value?.clearValidate?.()
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  form.employeeId = row.employeeId
  form.title = row.title
  form.description = row.description || ''
  form.platformKey = row.platformKey
  form.category = row.category
  form.priority = row.priority
  form.due = row.due
  dialogVisible.value = true
}

function onEmployeeChange(employeeId) {
  const employee = activeEmployees.value.find((emp) => emp.id === employeeId)
  if (!employee?.platforms?.length) return
  if (!employee.platforms.includes(form.platformKey)) {
    const key = employee.platforms[0]
    form.platformKey = key === 'shopify' || key === 'wordpress' ? 'dtc' : key
  }
}

async function loadData() {
  loading.value = true
  try {
    const [empRes, taskRes] = await Promise.all([fetchEmployees(), fetchAssignedTasks()])
    employees.value = empRes.data || []
    tasks.value = taskRes.data || []
  } catch {
    employees.value = []
    tasks.value = []
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function submitForm() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    const employee = activeEmployees.value.find((emp) => emp.id === form.employeeId)
    if (editingId.value) {
      await updateAssignedTask(editingId.value, {
        employeeId: form.employeeId,
        assignee: employee?.name,
        title: form.title.trim(),
        description: form.description.trim(),
        platformKey: form.platformKey,
        category: form.category,
        priority: form.priority,
        due: form.due,
      })
      ElMessage.success('任务已更新')
    } else {
      await assignTaskToEmployee(
        {
          employeeId: form.employeeId,
          title: form.title,
          description: form.description,
          platformKey: form.platformKey,
          category: form.category,
          priority: form.priority,
          due: form.due,
          assignedBy: '企业管理员',
        },
        employees.value,
      )
      ElMessage.success('任务已分配')
    }
    dialogVisible.value = false
    await loadData()
  } catch (err) {
    ElMessage.error(err.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function handleCancel(row) {
  try {
    await ElMessageBox.confirm(`确定取消任务「${row.title}」？`, '取消任务', { type: 'warning' })
    await cancelAssignedTask(row.id)
    ElMessage.success('任务已取消')
    await loadData()
  } catch {
    /* user dismissed */
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除任务「${row.title}」？`, '删除任务', { type: 'warning' })
    await removeAssignedTask(row.id)
    ElMessage.success('任务已删除')
    await loadData()
  } catch {
    /* user dismissed */
  }
}

onMounted(loadData)
</script>

<template>
  <PageScroll>
    <template #header>
      <PageHeader title="任务分配" description="向员工指派运营任务，员工将在任务中心收到并提交反馈">
        <template #actions>
          <el-button :icon="Refresh" :loading="loading" @click="loadData">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="openCreate">分配任务</el-button>
        </template>
      </PageHeader>
    </template>

    <div v-loading="loading" class="assign-page">
      <div class="metrics-bar metrics-bar--3">
        <div class="metric-item">
          <div class="metric-value">{{ stats.total }}</div>
          <div class="metric-label">全部分配</div>
        </div>
        <div class="metric-item">
          <div class="metric-value is-warning">{{ stats.active }}</div>
          <div class="metric-label">进行中</div>
        </div>
        <div class="metric-item">
          <div class="metric-value is-success">{{ stats.done }}</div>
          <div class="metric-label">已完成</div>
        </div>
      </div>

      <div class="filter-bar">
        <el-select v-model="filterEmployeeId" placeholder="员工" style="width: 160px" size="small">
          <el-option label="全部员工" value="all" />
          <el-option
            v-for="emp in activeEmployees"
            :key="emp.id"
            :label="`${emp.name} · ${emp.role}`"
            :value="emp.id"
          />
        </el-select>
        <el-select v-model="filterStatus" placeholder="状态" style="width: 130px" size="small">
          <el-option label="进行中" value="active" />
          <el-option label="全部状态" value="all" />
          <el-option v-for="status in TASK_STATUS_OPTIONS" :key="status" :label="status" :value="status" />
        </el-select>
      </div>

      <el-empty v-if="!loading && !filteredTasks.length" description="暂无分配任务" :image-size="88">
        <el-button type="primary" :icon="Plus" @click="openCreate">分配第一个任务</el-button>
      </el-empty>

      <el-table v-else :data="filteredTasks" stripe size="small" class="task-table">
        <el-table-column label="任务" min-width="220">
          <template #default="{ row }">
            <div class="task-title">{{ row.title }}</div>
            <div v-if="row.description" class="task-desc">{{ row.description }}</div>
          </template>
        </el-table-column>
        <el-table-column label="负责人" width="100">
          <template #default="{ row }">
            <div>{{ row.assignee }}</div>
          </template>
        </el-table-column>
        <el-table-column label="平台" width="100">
          <template #default="{ row }">
            {{ TASK_PLATFORM_OPTIONS.find((p) => p.value === row.platformKey)?.label || row.platformKey }}
          </template>
        </el-table-column>
        <el-table-column prop="category" label="类型" width="80" />
        <el-table-column label="优先级" width="72" align="center">
          <template #default="{ row }">
            <el-tag :type="priorityMap[row.priority]?.type || 'info'" size="small">
              {{ priorityMap[row.priority]?.label || '中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="due" label="截止" width="110" />
        <el-table-column label="状态" width="88" align="center">
          <template #default="{ row }">
            <el-tag :type="TASK_STATUS_META[row.status]?.type || 'info'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assignedAt" label="分配时间" width="160" />
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status !== '已完成' && row.status !== '已取消'"
              link
              type="primary"
              size="small"
              @click="openEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              v-if="row.status !== '已完成' && row.status !== '已取消'"
              link
              type="warning"
              size="small"
              @click="handleCancel(row)"
            >
              取消
            </el-button>
            <el-button link type="danger" size="small" :icon="Delete" @click="handleDelete(row)" />
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="520px"
      destroy-on-close
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="80px">
        <el-form-item label="负责人" prop="employeeId">
          <el-select
            v-model="form.employeeId"
            placeholder="选择员工"
            style="width: 100%"
            @change="onEmployeeChange"
          >
            <el-option
              v-for="emp in activeEmployees"
              :key="emp.id"
              :label="`${emp.name}（${emp.role}）`"
              :value="emp.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="任务标题" prop="title">
          <el-input v-model="form.title" placeholder="简明描述需完成的事项" maxlength="80" show-word-limit />
        </el-form-item>
        <el-form-item label="任务说明">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="补充背景、要求或验收标准"
          />
        </el-form-item>
        <el-form-item label="关联平台" prop="platformKey">
          <el-select v-model="form.platformKey" style="width: 100%">
            <el-option
              v-for="item in TASK_PLATFORM_OPTIONS"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="任务类型">
          <el-select v-model="form.category" style="width: 100%">
            <el-option v-for="item in TASK_CATEGORY_OPTIONS" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-radio-group v-model="form.priority">
            <el-radio v-for="item in TASK_PRIORITY_OPTIONS" :key="item.value" :value="item.value">
              {{ item.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="截止时间">
          <el-select v-model="form.due" style="width: 100%">
            <el-option v-for="item in TASK_DUE_OPTIONS" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">
          {{ editingId ? '保存' : '确认分配' }}
        </el-button>
      </template>
    </el-dialog>
  </PageScroll>
</template>

<style scoped>
.assign-page {
  display: grid;
  gap: 16px;
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.task-table {
  border-radius: var(--ch-radius-lg);
}

.task-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--ch-text);
}

.task-desc {
  margin-top: 4px;
  font-size: 12px;
  color: var(--ch-text-muted);
  line-height: 1.4;
}
</style>
