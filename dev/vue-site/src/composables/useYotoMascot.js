import { ref } from 'vue'

const coveringEyes = ref(false)
let focusCount = 0

export function useYotoMascot() {
  function onPasswordFocus() {
    focusCount += 1
    coveringEyes.value = true
  }

  function onPasswordBlur() {
    focusCount = Math.max(0, focusCount - 1)
    coveringEyes.value = focusCount > 0
  }

  return {
    coveringEyes,
    onPasswordFocus,
    onPasswordBlur,
  }
}
