import { fetchOpsFeedback, submitOpsFeedback } from './opsFeedbackLocal'

export function loadTodayOpsFeedback(options = {}) {
  return {
    success: true,
    data: fetchOpsFeedback(options),
  }
}

export function submitTaskFeedback(payload) {
  return submitOpsFeedback(payload)
}
