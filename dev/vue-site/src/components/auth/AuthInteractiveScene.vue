<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useYotoMascot } from '@/composables/useYotoMascot'

defineProps({
  hero: { type: Boolean, default: false },
})

const { coveringEyes } = useYotoMascot()

const sceneRef = ref(null)
const svgRef = ref(null)
const prefersReducedMotion = ref(false)

const pointer = ref({ x: 0, y: 0 })
const mouseInSvg = ref({ x: 110, y: 100 })
const isBlinking = ref(false)

const parallax = computed(() => ({
  x: pointer.value.x * 14,
  y: pointer.value.y * 10,
}))

const headTilt = computed(() => {
  if (coveringEyes.value) {
    return { rotate: -2, translateY: 3 }
  }
  return {
    rotate: pointer.value.x * 4,
    translateY: pointer.value.y * 2,
  }
})

const leftPupil = computed(() => (coveringEyes.value ? { x: 0, y: 0 } : pupilOffset(96, 100)))
const rightPupil = computed(() => (coveringEyes.value ? { x: 0, y: 0 } : pupilOffset(124, 100)))

let blinkTimer = null
let rafId = 0

function pupilOffset(eyeX, eyeY, max = 6) {
  const dx = mouseInSvg.value.x - eyeX
  const dy = mouseInSvg.value.y - eyeY
  const angle = Math.atan2(dy, dx)
  const distance = Math.min(max, Math.hypot(dx, dy) / 5.5)
  return {
    x: Math.cos(angle) * distance,
    y: Math.sin(angle) * distance,
  }
}

function updatePointer(clientX, clientY) {
  if (!sceneRef.value || !svgRef.value) return

  const sceneRect = sceneRef.value.getBoundingClientRect()
  const nx = (clientX - (sceneRect.left + sceneRect.width * 0.5)) / (sceneRect.width * 0.55)
  const ny = (clientY - (sceneRect.top + sceneRect.height * 0.45)) / (sceneRect.height * 0.55)

  pointer.value = {
    x: Math.max(-1, Math.min(1, nx)),
    y: Math.max(-1, Math.min(1, ny)),
  }

  const svg = svgRef.value
  const point = svg.createSVGPoint()
  point.x = clientX
  point.y = clientY
  const matrix = svg.getScreenCTM()?.inverse()
  if (!matrix) return

  const svgPoint = point.matrixTransform(matrix)
  mouseInSvg.value = { x: svgPoint.x, y: svgPoint.y }
}

function onMouseMove(event) {
  if (prefersReducedMotion.value || coveringEyes.value) return
  cancelAnimationFrame(rafId)
  rafId = requestAnimationFrame(() => {
    updatePointer(event.clientX, event.clientY)
  })
}

function scheduleBlink() {
  if (coveringEyes.value) return
  blinkTimer = window.setTimeout(() => {
    if (coveringEyes.value) {
      scheduleBlink()
      return
    }
    isBlinking.value = true
    window.setTimeout(() => {
      isBlinking.value = false
      scheduleBlink()
    }, 140)
  }, 2600 + Math.random() * 3200)
}

function onResize() {
  updatePointer(window.innerWidth * 0.42, window.innerHeight * 0.58)
}

watch(coveringEyes, (covering) => {
  if (covering) {
    isBlinking.value = false
    if (blinkTimer) {
      clearTimeout(blinkTimer)
      blinkTimer = null
    }
  } else if (!prefersReducedMotion.value) {
    scheduleBlink()
  }
})

onMounted(() => {
  prefersReducedMotion.value = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  onResize()
  window.addEventListener('mousemove', onMouseMove, { passive: true })
  window.addEventListener('resize', onResize, { passive: true })
  if (!prefersReducedMotion.value) scheduleBlink()
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('resize', onResize)
  cancelAnimationFrame(rafId)
  if (blinkTimer) clearTimeout(blinkTimer)
})
</script>

<template>
  <div
    ref="sceneRef"
    class="auth-scene"
    :class="{ 'auth-scene--hero': hero, 'auth-scene--shy': coveringEyes }"
    aria-hidden="true"
  >
    <div
      class="auth-scene__glow"
      :style="{ transform: `translate(${parallax.x * 0.35}px, ${parallax.y * 0.35}px)` }"
    />

    <div
      class="auth-scene__orb auth-scene__orb--1"
      :style="{ transform: `translate(${parallax.x}px, ${parallax.y}px)` }"
    />
    <div
      class="auth-scene__orb auth-scene__orb--2"
      :style="{ transform: `translate(${-parallax.x * 0.65}px, ${parallax.y * 0.45}px)` }"
    />
    <div
      class="auth-scene__orb auth-scene__orb--3"
      :style="{ transform: `translate(${parallax.x * 0.45}px, ${-parallax.y * 0.7}px)` }"
    />

    <div
      class="auth-scene__ring-wrap"
      :style="{ transform: `translate(${parallax.x * 0.2}px, ${parallax.y * 0.2}px)` }"
    >
      <div class="auth-scene__ring" />
    </div>

    <div
      class="auth-scene__mascot-wrap"
      :style="{
        transform: `translate(${parallax.x * 0.12}px, ${parallax.y * 0.12}px) rotate(${headTilt.rotate}deg) translateY(${headTilt.translateY}px)`,
      }"
    >
      <div class="auth-scene__mascot">
        <svg ref="svgRef" viewBox="0 0 220 260" class="mascot-svg">
          <defs>
            <linearGradient id="koiWhite" x1="20%" y1="0%" x2="80%" y2="100%">
              <stop offset="0%" stop-color="#fffefb" />
              <stop offset="100%" stop-color="#f5ebe0" />
            </linearGradient>
            <linearGradient id="koiOrange" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#ff9a76" />
              <stop offset="50%" stop-color="#ff6b4a" />
              <stop offset="100%" stop-color="#e84a3f" />
            </linearGradient>
            <linearGradient id="koiFin" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#ffc9b5" />
              <stop offset="100%" stop-color="#ff8a65" />
            </linearGradient>
            <linearGradient id="koiTail" x1="50%" y1="0%" x2="50%" y2="100%">
              <stop offset="0%" stop-color="#ff8a65" />
              <stop offset="100%" stop-color="#e84a3f" />
            </linearGradient>
            <radialGradient id="koiBlush" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stop-color="rgba(255,138,120,0.35)" />
              <stop offset="100%" stop-color="rgba(255,138,120,0)" />
            </radialGradient>
            <filter id="koiShadow" x="-20%" y="-10%" width="140%" height="140%">
              <feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#1a1a2e" flood-opacity="0.25" />
            </filter>
          </defs>

          <ellipse cx="110" cy="242" rx="46" ry="7" fill="rgba(0,0,0,0.12)" />

          <g filter="url(#koiShadow)">
            <!-- tail -->
            <g class="koi-tail">
              <path
                d="M 110 178 C 88 192 72 212 64 234 C 82 224 96 216 110 212 C 124 216 138 224 156 234 C 148 212 132 192 110 178 Z"
                fill="url(#koiTail)"
              />
              <path
                d="M 110 178 C 98 186 90 198 86 212 C 96 206 104 202 110 200 C 116 202 124 206 134 212 C 130 198 122 186 110 178 Z"
                fill="rgba(255,255,255,0.2)"
              />
            </g>

            <!-- body -->
            <path
              d="M 110 52
                 C 138 52 154 68 158 88
                 C 162 108 160 138 150 162
                 C 142 180 128 188 110 188
                 C 92 188 78 180 70 162
                 C 60 138 58 108 62 88
                 C 66 68 82 52 110 52 Z"
              fill="url(#koiWhite)"
            />

            <!-- kohaku patch -->
            <path
              d="M 110 54
                 C 132 56 146 70 148 90
                 C 150 112 144 140 128 162
                 C 118 152 112 130 110 108
                 C 106 82 96 62 82 58
                 C 92 54 100 52 110 54 Z"
              fill="url(#koiOrange)"
              opacity="0.88"
            />

            <!-- belly highlight -->
            <ellipse cx="110" cy="130" rx="28" ry="38" fill="rgba(255,255,255,0.45)" />

            <!-- dorsal fin -->
            <path
              d="M 108 82 C 102 70 104 60 110 54 C 116 60 118 70 112 82 Z"
              fill="url(#koiFin)"
              opacity="0.75"
            />
          </g>

          <!-- idle fins -->
          <g class="yoto-arms" :class="{ 'is-hidden': coveringEyes }">
            <ellipse cx="68" cy="148" rx="14" ry="10" fill="url(#koiFin)" opacity="0.8" transform="rotate(-20 68 148)" />
            <ellipse cx="152" cy="148" rx="14" ry="10" fill="url(#koiFin)" opacity="0.8" transform="rotate(20 152 148)" />
          </g>

          <!-- face -->
          <g class="yoto-face" :class="{ 'is-blinking': isBlinking && !coveringEyes }">
            <g class="yoto-eye">
              <circle cx="96" cy="100" r="13" fill="#fff" />
              <circle cx="96" cy="100" r="13" fill="none" stroke="rgba(232,74,63,0.12)" stroke-width="1" />
              <circle :cx="96 + leftPupil.x" :cy="100 + leftPupil.y" r="6.5" fill="#3d3d3d" />
              <circle :cx="93 + leftPupil.x * 0.25" :cy="97 + leftPupil.y * 0.25" r="2.2" fill="#fff" />
            </g>
            <g class="yoto-eye">
              <circle cx="124" cy="100" r="13" fill="#fff" />
              <circle cx="124" cy="100" r="13" fill="none" stroke="rgba(232,74,63,0.12)" stroke-width="1" />
              <circle :cx="124 + rightPupil.x" :cy="100 + rightPupil.y" r="6.5" fill="#3d3d3d" />
              <circle :cx="121 + rightPupil.x * 0.25" :cy="97 + rightPupil.y * 0.25" r="2.2" fill="#fff" />
            </g>

            <ellipse cx="84" cy="112" rx="7" ry="4.5" fill="url(#koiBlush)" />
            <ellipse cx="136" cy="112" rx="7" ry="4.5" fill="url(#koiBlush)" />

            <path
              v-if="!coveringEyes"
              d="M 102 116 Q 110 122 118 116"
              fill="none"
              stroke="#d4847a"
              stroke-width="2.5"
              stroke-linecap="round"
            />
            <circle v-else cx="110" cy="118" r="3" fill="none" stroke="#d4847a" stroke-width="2" />
          </g>

          <!-- covering fins -->
          <g class="yoto-hands" :class="{ 'is-covering': coveringEyes }">
            <g class="yoto-hand yoto-hand--left">
              <ellipse cx="96" cy="100" rx="22" ry="18" fill="url(#koiFin)" opacity="0.95" />
            </g>
            <g class="yoto-hand yoto-hand--right">
              <ellipse cx="124" cy="100" rx="22" ry="18" fill="url(#koiFin)" opacity="0.95" />
            </g>
          </g>
        </svg>

        <p v-if="hero" class="auth-scene__name">小鲤</p>
        <p v-else class="auth-scene__hint">小鲤 · CrossHub 小助手</p>
      </div>
    </div>

    <div v-if="!hero" class="auth-scene__tags">
      <span
        class="auth-scene__tag"
        :style="{ transform: `translate(${parallax.x * 0.3}px, ${parallax.y * 0.18}px)` }"
      >
        多平台
      </span>
      <span
        class="auth-scene__tag auth-scene__tag--delay"
        :style="{ transform: `translate(${-parallax.x * 0.22}px, ${-parallax.y * 0.3}px)` }"
      >
        实时同步
      </span>
    </div>

    <p v-if="coveringEyes && hero" class="auth-scene__whisper">我不看 · 你放心输</p>
  </div>
</template>

<style scoped>
.auth-scene {
  position: relative;
  width: 100%;
  max-width: 300px;
  height: min(420px, 76vh);
  margin: 0 auto;
  pointer-events: none;
  user-select: none;
}

.auth-scene__glow {
  position: absolute;
  inset: 20% 10% 24%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 138, 101, 0.14) 0%, transparent 70%);
  transition: transform 0.35s ease-out, background 0.4s ease;
}

.auth-scene--shy .auth-scene__glow {
  background: radial-gradient(circle, rgba(255, 154, 118, 0.18) 0%, transparent 70%);
}

.auth-scene__orb {
  position: absolute;
  border-radius: 50%;
  transition: transform 0.45s ease-out;
}

.auth-scene__orb--1 {
  top: 10%;
  left: 8%;
  width: 10px;
  height: 10px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.15);
  animation: orb-float 5s ease-in-out infinite;
}

.auth-scene__orb--2 {
  top: 22%;
  right: 6%;
  width: 6px;
  height: 6px;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.1);
  animation: orb-float 6.5s ease-in-out infinite reverse;
}

.auth-scene__orb--3 {
  bottom: 30%;
  left: 6%;
  width: 5px;
  height: 5px;
  background: rgba(255, 255, 255, 0.18);
  animation: orb-float 4.8s ease-in-out infinite;
}

.auth-scene__ring-wrap {
  position: absolute;
  inset: 10% 0 18%;
  transition: transform 0.45s ease-out;
}

.auth-scene__ring {
  width: 100%;
  height: 100%;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 50%;
}

.auth-scene__mascot-wrap {
  position: absolute;
  inset: 0;
  transition: transform 0.45s cubic-bezier(0.34, 1.2, 0.64, 1);
}

.auth-scene__mascot {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
  animation: mascot-float 5.5s ease-in-out infinite;
}

.mascot-svg {
  width: 230px;
  height: auto;
  overflow: visible;
}

.koi-tail {
  transform-origin: 110px 178px;
  animation: tail-sway 3.5s ease-in-out infinite;
}

.yoto-arms {
  transition: opacity 0.25s ease, transform 0.35s ease;
}

.yoto-arms.is-hidden {
  opacity: 0;
  transform: translateY(6px);
}

.yoto-face.is-blinking .yoto-eye {
  animation: blink 0.14s ease-in-out;
  transform-box: fill-box;
  transform-origin: center;
}

.yoto-hands {
  pointer-events: none;
}

.yoto-hand {
  opacity: 0;
  transform: translateY(28px) scale(0.85);
  transition:
    opacity 0.32s ease,
    transform 0.45s cubic-bezier(0.34, 1.45, 0.64, 1);
}

.yoto-hands.is-covering .yoto-hand {
  opacity: 1;
  transform: translateY(0);
}

.yoto-hands.is-covering .yoto-hand--left {
  transition-delay: 0.02s;
}

.yoto-hands.is-covering .yoto-hand--right {
  transition-delay: 0.08s;
}

.auth-scene__name {
  margin: 12px 0 0;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.2em;
  color: rgba(255, 255, 255, 0.45);
}

.auth-scene__hint {
  margin: 8px 0 0;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.04em;
  color: rgba(248, 250, 252, 0.38);
}

.auth-scene__whisper {
  position: absolute;
  bottom: 8%;
  left: 50%;
  margin: 0;
  padding: 6px 14px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: rgba(248, 250, 252, 0.55);
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(8px);
  transform: translateX(-50%);
  animation: whisper-in 0.4s ease;
}

.auth-scene__tags {
  position: absolute;
  inset: 0;
}

.auth-scene__tag {
  position: absolute;
  padding: 6px 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  color: rgba(248, 250, 252, 0.62);
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(8px);
  transition: transform 0.45s ease-out;
}

.auth-scene__tag:first-child {
  top: 6%;
  right: 2%;
}

.auth-scene__tag--delay {
  bottom: 16%;
  left: -4%;
}

@keyframes tail-sway {
  0%,
  100% {
    transform: rotate(0deg);
  }
  50% {
    transform: rotate(4deg);
  }
}

@keyframes mascot-float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes orb-float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-6px);
  }
}

@keyframes blink {
  0%,
  100% {
    transform: scaleY(1);
  }
  50% {
    transform: scaleY(0.08);
  }
}

@keyframes whisper-in {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.auth-scene--hero .auth-scene__mascot {
  justify-content: center;
}

.auth-scene--hero .auth-scene__ring-wrap {
  inset: 4% 2% 8%;
}

.auth-scene--hero .auth-scene__glow {
  inset: 10% 2% 14%;
  background: radial-gradient(circle, rgba(255, 138, 101, 0.18) 0%, transparent 65%);
}

.auth-scene--hero.auth-scene--shy .auth-scene__glow {
  background: radial-gradient(circle, rgba(255, 154, 118, 0.22) 0%, transparent 65%);
}

@media (prefers-reduced-motion: reduce) {
  .auth-scene__mascot,
  .auth-scene__orb,
  .koi-tail {
    animation: none;
  }

  .auth-scene__glow,
  .auth-scene__orb,
  .auth-scene__ring-wrap,
  .auth-scene__tag,
  .yoto-hand,
  .yoto-arms {
    transition: none;
  }

  .yoto-hands.is-covering .yoto-hand {
    transform: none;
    opacity: 1;
  }
}
</style>
