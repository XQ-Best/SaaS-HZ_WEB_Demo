import { ref } from 'vue'
import { fetchEmployees } from '@/api/employees'
import {
  buildStoreAssigneeMap,
  attachAssignee,
  enrichWithAssignee,
  resolveStoreAssignee,
} from '@/utils/storeAssignment'

export function useStoreAssignees() {
  const assigneeMap = ref({})
  const loaded = ref(false)

  async function loadAssignees() {
    try {
      const res = await fetchEmployees()
      assigneeMap.value = buildStoreAssigneeMap(res.data || [])
    } catch {
      assigneeMap.value = {}
    } finally {
      loaded.value = true
    }
  }

  function enrichItem(item) {
    return attachAssignee(item, item.storeId, assigneeMap.value)
  }

  function enrichItems(items = []) {
    return enrichWithAssignee(items, assigneeMap.value)
  }

  function resolveAssignee(storeId, fallback = '未分配') {
    return resolveStoreAssignee(storeId, assigneeMap.value, fallback)
  }

  return {
    assigneeMap,
    loaded,
    loadAssignees,
    enrichItem,
    enrichItems,
    resolveAssignee,
  }
}
