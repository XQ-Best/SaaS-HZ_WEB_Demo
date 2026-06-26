import { fetchOpsFeedback, submitOpsFeedback, fetchFeedbacksByTaskId } from './opsFeedbackLocal'

export function loadTodayOpsFeedback(options = {}) {
  return {
    success: true,
    data: fetchOpsFeedback(options),
  }
}

export function loadTaskFeedbacks(taskId) {
  return {
    success: true,
    data: fetchFeedbacksByTaskId(taskId),
  }
}

export function submitTaskFeedback(payload) {
  return submitOpsFeedback(payload)
}
