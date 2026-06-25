<script setup>
import AuthInteractiveScene from './AuthInteractiveScene.vue'
</script>

<template>
  <div class="auth-split">
    <aside class="auth-split__hero">
      <div class="hero-bg" aria-hidden="true">
        <div class="hero-bg__mesh" />
        <div class="hero-bg__ring hero-bg__ring--1" />
        <div class="hero-bg__ring hero-bg__ring--2" />
        <div class="hero-bg__ring hero-bg__ring--3" />
      </div>

      <header class="hero-top">
        <div class="hero-brand">
          <div class="hero-brand__mark">CH</div>
          <span class="hero-brand__name">CrossHub</span>
        </div>
        <span class="hero-demo-tag">Demo</span>
      </header>

      <div class="hero-copy">
        <h1 class="hero-copy__title">
          跨境运营<span class="hero-copy__accent">指挥台</span>
        </h1>
        <p class="hero-copy__desc">多平台数据 · 预警协同 · 分级管理</p>
      </div>

      <div class="hero-stage">
        <AuthInteractiveScene hero />
      </div>
    </aside>

    <main class="auth-split__main">
      <div class="auth-panel">
        <slot />
      </div>
    </main>
  </div>
</template>

<style scoped>
.auth-split {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(420px, 0.92fr);
  height: 100%;
  min-height: 100%;
  overflow: hidden;
}

.auth-split__hero {
  position: relative;
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding: clamp(24px, 3.5vh, 40px) clamp(28px, 3vw, 48px);
  overflow: hidden;
  border-right: 1px solid rgba(255, 255, 255, 0.06);
}

.hero-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.hero-bg__mesh {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 50% 42%, rgba(99, 102, 241, 0.32) 0%, transparent 48%),
    radial-gradient(circle at 20% 80%, rgba(14, 165, 233, 0.14) 0%, transparent 38%),
    radial-gradient(circle at 80% 18%, rgba(124, 58, 237, 0.12) 0%, transparent 32%);
}

.hero-bg__ring {
  position: absolute;
  top: 50%;
  left: 50%;
  border: 1px solid rgba(165, 180, 252, 0.1);
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

.hero-bg__ring--1 {
  width: min(420px, 52vw);
  height: min(420px, 52vw);
  animation: ring-pulse 8s ease-in-out infinite;
}

.hero-bg__ring--2 {
  width: min(560px, 68vw);
  height: min(560px, 68vw);
  border-color: rgba(165, 180, 252, 0.06);
  animation: ring-pulse 8s ease-in-out infinite reverse;
}

.hero-bg__ring--3 {
  width: min(700px, 82vw);
  height: min(700px, 82vw);
  border-color: rgba(165, 180, 252, 0.04);
}

.hero-top {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.hero-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.hero-brand__mark {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(145deg, #6366f1, #4f46e5 55%, #0ea5e9);
  box-shadow: 0 8px 24px rgba(79, 70, 229, 0.4);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.05em;
  color: #fff;
}

.hero-brand__name {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: rgba(248, 250, 252, 0.88);
}

.hero-demo-tag {
  padding: 4px 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(248, 250, 252, 0.55);
  background: rgba(255, 255, 255, 0.04);
}

.hero-copy {
  position: relative;
  z-index: 2;
  flex-shrink: 0;
  max-width: 440px;
  margin-top: clamp(20px, 3vh, 32px);
}

.hero-copy__title {
  margin: 0;
  font-size: clamp(24px, 2.6vw, 32px);
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.03em;
  color: rgba(248, 250, 252, 0.96);
}

.hero-copy__accent {
  background: linear-gradient(120deg, #a5b4fc 0%, #67e8f9 55%, #c4b5fd 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-copy__desc {
  margin: 10px 0 0;
  font-size: 13px;
  line-height: 1.5;
  letter-spacing: 0.04em;
  color: rgba(226, 232, 240, 0.55);
}

.hero-stage {
  position: relative;
  z-index: 1;
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  min-height: 0;
  margin-top: clamp(8px, 1.5vh, 16px);
}

.hero-stage :deep(.auth-scene) {
  width: min(340px, 88%);
  max-width: 340px;
  height: min(360px, 46vh);
}

.hero-stage :deep(.mascot-svg) {
  width: min(280px, 72vw);
}

.hero-stage :deep(.auth-scene__name) {
  margin-top: 6px;
  font-size: 13px;
  letter-spacing: 0.14em;
}

.auth-split__main {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  padding: clamp(32px, 5vh, 56px) clamp(28px, 4vw, 56px);
  overflow-y: auto;
  background:
    radial-gradient(circle at 100% 0%, rgba(99, 102, 241, 0.08) 0%, transparent 42%),
    linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
}

.auth-panel {
  width: 100%;
  max-width: 420px;
}

@keyframes ring-pulse {
  0%,
  100% {
    opacity: 0.55;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1.03);
  }
}

@media (max-width: 1080px) {
  .auth-split {
    grid-template-columns: 1fr;
    overflow-y: auto;
  }

  .auth-split__hero {
    min-height: auto;
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  }

  .hero-copy {
    margin-top: 20px;
  }

  .hero-stage {
    min-height: 280px;
    margin-top: 12px;
  }

  .hero-stage :deep(.auth-scene) {
    height: min(300px, 38vh);
  }

  .hero-bg__ring--3 {
    display: none;
  }
}

@media (max-width: 640px) {
  .auth-split__main {
    padding: 28px 20px 36px;
  }

  .hero-copy__title {
    font-size: 22px;
  }

  .hero-stage :deep(.mascot-svg) {
    width: 220px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero-bg__ring--1,
  .hero-bg__ring--2 {
    animation: none;
  }
}
</style>
