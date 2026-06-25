<script setup>
import AuthHeroIllustration from './AuthHeroIllustration.vue'
</script>

<template>
  <div class="auth-split">
    <aside class="auth-split__hero">
      <header class="hero-top">
        <div class="hero-brand">
          <div class="hero-brand__mark">CH</div>
          <span class="hero-brand__name">CrossHub</span>
        </div>
        <el-tag size="small" type="info" effect="plain" round>Demo</el-tag>
      </header>

      <div class="hero-copy">
        <h1 class="hero-copy__title">跨境运营指挥台</h1>
        <p class="hero-copy__desc">多平台数据整合 · 智能预警 · 分级权限管理</p>
        <ul class="hero-copy__features">
          <li>Temu / Amazon / 1688 全平台覆盖</li>
          <li>企业管理员与员工分级工作台</li>
          <li>运营问题实时追踪与协同</li>
        </ul>
      </div>

      <div class="hero-stage">
        <AuthHeroIllustration hero />
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
  grid-template-columns: minmax(0, 1.1fr) minmax(400px, 0.9fr);
  height: 100%;
  min-height: 100%;
  overflow: hidden;
}

.auth-split__hero {
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding: 32px 48px;
  background: var(--ch-surface);
  border-right: 1px solid var(--ch-border);
}

.hero-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.hero-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.hero-brand__mark {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: var(--ch-radius-sm);
  background: var(--ch-primary);
  font-size: 12px;
  font-weight: 700;
  color: #fff;
}

.hero-brand__name {
  font-size: 16px;
  font-weight: 600;
  color: var(--ch-text);
}

.hero-copy {
  max-width: 420px;
  margin-top: 40px;
}

.hero-copy__title {
  margin: 0;
  font-size: 32px;
  font-weight: 600;
  line-height: 1.25;
  letter-spacing: -0.02em;
  color: var(--ch-text);
}

.hero-copy__desc {
  margin: 12px 0 0;
  font-size: 15px;
  line-height: 1.6;
  color: var(--ch-text-secondary);
}

.hero-copy__features {
  margin: 20px 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 10px;
}

.hero-copy__features li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--ch-text-secondary);
}

.hero-copy__features li::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--ch-primary);
  flex-shrink: 0;
}

.hero-stage {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  min-height: 0;
  margin-top: 32px;
}

.auth-split__main {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  padding: 40px 48px;
  overflow-y: auto;
  background: var(--ch-layout-bg);
}

.auth-panel {
  width: 100%;
  max-width: 400px;
  padding: 36px 32px;
  border: 1px solid var(--ch-border);
  border-radius: var(--ch-radius-lg);
  background: var(--ch-surface);
  box-shadow: var(--ch-shadow-sm);
}

@media (max-width: 1080px) {
  .auth-split {
    grid-template-columns: 1fr;
    overflow-y: auto;
  }

  .auth-split__hero {
    border-right: none;
    border-bottom: 1px solid var(--ch-border);
    padding: 28px 24px;
  }

  .hero-copy { margin-top: 24px; }
  .hero-stage { min-height: 240px; margin-top: 24px; }
}

@media (max-width: 640px) {
  .auth-split__main { padding: 24px 16px; }
  .auth-panel { padding: 28px 20px; }
  .hero-copy__title { font-size: 24px; }
}
</style>
