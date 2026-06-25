import {
  deleteLocalEmployee,
  fetchLocalEmployees,
  saveLocalEmployee,
  toggleLocalEmployeeStatus,
} from './employeesLocal'

export function fetchEmployees() {
  return fetchLocalEmployees()
}

export function saveEmployee(payload) {
  const result = saveLocalEmployee(payload)
  if (result.error) throw new Error(result.error)
  return result
}

export function deleteEmployee(id) {
  const result = deleteLocalEmployee(id)
  if (result.error) throw new Error(result.error)
  return result
}

export function toggleEmployeeStatus(id, status) {
  const result = toggleLocalEmployeeStatus(id, status)
  if (result.error) throw new Error(result.error)
  return result
}
