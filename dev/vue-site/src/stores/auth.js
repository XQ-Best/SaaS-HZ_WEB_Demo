import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const isLoggedIn = ref(false)
  const role = ref('boss')
  const company = ref({
    name: '泰州亿拓户外用品有限公司',
    account: 'admin@crosshub.cn',
  })
  const employee = ref({
    id: '',
    name: '',
    account: '',
    role: '',
    platforms: [],
    assignedStoreIds: [],
  })

  const isBoss = computed(() => role.value === 'boss')
  const portalLabel = computed(() => (isBoss.value ? '企业管理员' : '员工端口'))
  const displayName = computed(() =>
    isBoss.value ? company.value.name : employee.value.name,
  )

  function setCompany(payload) {
    company.value = {
      name: payload.company,
      account: payload.account,
    }
  }

  function setEmployee(payload) {
    employee.value = {
      id: payload.id || '',
      name: payload.name,
      account: payload.account,
      role: payload.role,
      platforms: payload.platforms || [],
      assignedStoreIds: payload.assignedStoreIds || [],
    }
  }

  function login(nextRole) {
    role.value = nextRole
    isLoggedIn.value = true
  }

  function logout() {
    isLoggedIn.value = false
  }

  return {
    isLoggedIn,
    role,
    company,
    employee,
    isBoss,
    portalLabel,
    displayName,
    setCompany,
    setEmployee,
    login,
    logout,
  }
})
