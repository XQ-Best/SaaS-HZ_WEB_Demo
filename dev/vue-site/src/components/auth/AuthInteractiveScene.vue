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
const mouseInSvg = ref({ x: 110, y: 118 })
const isBlinking = ref(false)

const parallax = computed(() => ({
  x: pointer.value.x * 16,
  y: pointer.value.y * 12,
}))

const headTilt = computed(() => {
  if (coveringEyes.value) {
    return { rotate: -4, translateY: 4 }
  }
  return {
    rotate: pointer.value.x * 6,
    translateY: pointer.value.y * 3,
  }
})

const leftPupil = computed(() => (coveringEyes.value ? { x: 0, y: 0 } : pupilOffset(76, 118)))
const rightPupil = computed(() => (coveringEyes.value ? { x: 0, y: 0 } : pupilOffset(144, 118)))

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
            <linearGradient id="yotoBody" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#a5b4fc" />
              <stop offset="35%" stop-color="#6366f1" />
              <stop offset="72%" stop-color="#4f46e5" />
              <stop offset="100%" stop-color="#0284c7" />
            </linearGradient>
            <linearGradient id="yotoShine" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="rgba(255,255,255,0.42)" />
              <stop offset="55%" stop-color="rgba(255,255,255,0.08)" />
              <stop offset="100%" stop-color="rgba(255,255,255,0)" />
            </linearGradient>
            <linearGradient id="yotoEar" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#818cf8" />
              <stop offset="100%" stop-color="#4338ca" />
            </linearGradient>
            <linearGradient id="yotoHand" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#c4b5fd" />
              <stop offset="100%" stop-color="#6366f1" />
            </linearGradient>
            <radialGradient id="yotoCheek" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stop-color="rgba(251,113,133,0.45)" />
              <stop offset="100%" stop-color="rgba(251,113,133,0)" />
            </radialGradient>
            <filter id="yotoShadow" x="-30%" y="-30%" width="160%" height="160%">
              <feDropShadow dx="0" dy="20" stdDeviation="18" flood-color="#312e81" flood-opacity="0.42" />
            </filter>
            <filter id="yotoSoftGlow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          <ellipse cx="110" cy="232" rx="62" ry="11" fill="rgba(15,23,42,0.38)" />

          <!-- ears -->
          <ellipse cx="58" cy="72" rx="18" ry="22" fill="url(#yotoEar)" opacity="0.92" />
          <ellipse cx="162" cy="72" rx="18" ry="22" fill="url(#yotoEar)" opacity="0.92" />
          <ellipse cx="58" cy="74" rx="10" ry="12" fill="rgba(255,255,255,0.12)" />
          <ellipse cx="162" cy="74" rx="10" ry="12" fill="rgba(255,255,255,0.12)" />

          <!-- body -->
          <g filter="url(#yotoShadow)">
            <rect x="38" y="64" width="144" height="148" rx="48" fill="url(#yotoBody)" />
            <rect x="38" y="64" width="144" height="74" rx="48" fill="url(#yotoShine)" />
            <rect x="52" y="78" width="116" height="52" rx="26" fill="rgba(255,255,255,0.06)" />
          </g>

          <!-- antenna -->
          <path d="M 104 64 Q 110 42 116 64" fill="none" stroke="#4338ca" stroke-width="4" stroke-linecap="round" />
          <circle cx="110" cy="36" r="9" fill="#38bdf8" class="yoto-antenna" filter="url(#yotoSoftGlow)" />
          <circle cx="110" cy="36" r="4" fill="#fff" opacity="0.55" />

          <!-- idle arms -->
          <g class="yoto-arms" :class="{ 'is-hidden': coveringEyes }">
            <ellipse cx="28" cy="168" rx="14" ry="18" fill="url(#yotoHand)" />
            <ellipse cx="192" cy="168" rx="14" ry="18" fill="url(#yotoHand)" />
          </g>

          <!-- face -->
          <g class="yoto-face" :class="{ 'is-blinking': isBlinking && !coveringEyes }">
            <g class="yoto-eye">
              <ellipse cx="76" cy="124" rx="20" ry="22" fill="#f8fafc" />
              <ellipse cx="76" cy="124" rx="20" ry="22" fill="none" stroke="rgba(99,102,241,0.25)" stroke-width="1.5" />
              <circle :cx="76 + leftPupil.x" :cy="124 + leftPupil.y" r="10" fill="#4338ca" />
              <circle :cx="76 + leftPupil.x" :cy="124 + leftPupil.y" r="6" fill="#0f172a" />
              <circle :cx="70 + leftPupil.x * 0.3" :cy="118 + leftPupil.y * 0.3" r="3" fill="#fff" opacity="0.95" />
            </g>
            <g class="yoto-eye">
              <ellipse cx="144" cy="124" rx="20" ry="22" fill="#f8fafc" />
              <ellipse cx="144" cy="124" rx="20" ry="22" fill="none" stroke="rgba(99,102,241,0.25)" stroke-width="1.5" />
              <circle :cx="144 + rightPupil.x" :cy="124 + rightPupil.y" r="10" fill="#4338ca" />
              <circle :cx="144 + rightPupil.x" :cy="124 + rightPupil.y" r="6" fill="#0f172a" />
              <circle :cx="138 + rightPupil.x * 0.3" :cy="118 + rightPupil.y * 0.3" r="3" fill="#fff" opacity="0.95" />
            </g>

            <ellipse cx="58" cy="142" rx="12" ry="7" fill="url(#yotoCheek)" />
            <ellipse cx="162" cy="142" rx="12" ry="7" fill="url(#yotoCheek)" />

            <path
              v-if="!coveringEyes"
              d="M 84 158 Q 110 176 136 158"
              fill="none"
              stroke="rgba(255,255,255,0.72)"
              stroke-width="4.5"
              stroke-linecap="round"
            />
            <ellipse v-else cx="110" cy="162" rx="8" ry="6" fill="none" stroke="rgba(255,255,255,0.55)" stroke-width="3.5" />
          </g>

          <!-- chest badge -->
          <text x="110" y="98" text-anchor="middle" class="yoto-badge">Y</text>

          <!-- covering hands -->
          <g class="yoto-hands" :class="{ 'is-covering': coveringEyes }">
            <g class="yoto-hand yoto-hand--left">
              <ellipse cx="76" cy="124" rx="26" ry="22" fill="url(#yotoHand)" />
              <ellipse cx="64" cy="112" rx="7" ry="9" fill="url(#yotoHand)" />
              <ellipse cx="76" cy="108" rx="7" ry="9" fill="url(#yotoHand)" />
              <ellipse cx="88" cy="112" rx="7" ry="9" fill="url(#yotoHand)" />
            </g>
            <g class="yoto-hand yoto-hand--right">
              <ellipse cx="144" cy="124" rx="26" ry="22" fill="url(#yotoHand)" />
              <ellipse cx="132" cy="112" rx="7" ry="9" fill="url(#yotoHand)" />
              <ellipse cx="144" cy="108" rx="7" ry="9" fill="url(#yotoHand)" />
              <ellipse cx="156" cy="112" rx="7" ry="9" fill="url(#yotoHand)" />
            </g>
          </g>
        </svg>

        <p v-if="hero" class="auth-scene__name">Yoto</p>
        <p v-else class="auth-scene__hint">Yoto · CrossHub 小助手</p>
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
  inset: 18% 8% 22%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.28) 0%, transparent 68%);
  transition: transform 0.35s ease-out, background 0.4s ease;
}

.auth-scene--shy .auth-scene__glow {
  background: radial-gradient(circle, rgba(244, 114, 182, 0.22) 0%, transparent 68%);
}

.auth-scene__orb {
  position: absolute;
  border-radius: 50%;
  transition: transform 0.45s ease-out;
}

.auth-scene__orb--1 {
  top: 8%;
  left: 4%;
  width: 14px;
  height: 14px;
  background: rgba(56, 189, 248, 0.75);
  box-shadow: 0 0 24px rgba(56, 189, 248, 0.55);
  animation: orb-float 5s ease-in-out infinite;
}

.auth-scene__orb--2 {
  top: 18%;
  right: 0;
  width: 10px;
  height: 10px;
  background: rgba(167, 139, 250, 0.8);
  box-shadow: 0 0 20px rgba(167, 139, 250, 0.5);
  animation: orb-float 6.5s ease-in-out infinite reverse;
}

.auth-scene__orb--3 {
  bottom: 28%;
  left: 0;
  width: 8px;
  height: 8px;
  background: rgba(129, 140, 248, 0.85);
  box-shadow: 0 0 16px rgba(129, 140, 248, 0.45);
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
  border: 1px dashed rgba(165, 180, 252, 0.22);
  border-radius: 50%;
  animation: ring-spin 28s linear infinite;
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
  width: 250px;
  height: auto;
  overflow: visible;
}

.yoto-antenna {
  animation: antenna-pulse 2.4s ease-in-out infinite;
}

.yoto-badge {
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 0.02em;
  fill: rgba(255, 255, 255, 0.78);
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
  transform: translateY(48px);
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
  margin: 10px 0 0;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(248, 250, 252, 0.72);
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
    transform: translateY(-8px);
  }
}

@keyframes ring-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes antenna-pulse {
  0%,
  100% {
    opacity: 0.75;
  }
  50% {
    opacity: 1;
    filter: drop-shadow(0 0 10px rgba(56, 189, 248, 0.85));
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
  inset: 8% 0 12%;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.38) 0%, transparent 62%);
}

.auth-scene--hero.auth-scene--shy .auth-scene__glow {
  background: radial-gradient(circle, rgba(244, 114, 182, 0.28) 0%, transparent 62%);
}

@media (prefers-reduced-motion: reduce) {
  .auth-scene__mascot,
  .auth-scene__orb,
  .auth-scene__ring,
  .yoto-antenna {
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
