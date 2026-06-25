<template>
  <div class="auth-shell">
    <div class="auth-bg" aria-hidden="true">
      <div class="auth-bg__gradient" />
      <div class="auth-bg__grid" />
      <div class="auth-bg__orb auth-bg__orb--1" />
      <div class="auth-bg__orb auth-bg__orb--2" />
      <div class="auth-bg__orb auth-bg__orb--3" />
      <div class="auth-bg__shine" />
    </div>
    <div class="auth-content">
      <router-view />
    </div>
  </div>
</template>

<style scoped>
.auth-shell {
  position: relative;
  height: 100%;
  overflow: hidden;
  background: #030712;
}

.auth-content {
  position: relative;
  z-index: 1;
  height: 100%;
}

.auth-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.auth-bg__gradient {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 60% at 20% 20%, rgba(79, 70, 229, 0.22) 0%, transparent 55%),
    radial-gradient(ellipse 70% 50% at 85% 75%, rgba(14, 165, 233, 0.15) 0%, transparent 50%),
    linear-gradient(165deg, #030712 0%, #0f172a 45%, #020617 100%);
}

.auth-bg__grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 64px 64px;
  mask-image: radial-gradient(ellipse 90% 80% at 50% 40%, black 20%, transparent 75%);
}

.auth-bg__orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
}

.auth-bg__orb--1 {
  top: -8%;
  left: -4%;
  width: 520px;
  height: 520px;
  background: #4338ca;
  opacity: 0.45;
}

.auth-bg__orb--2 {
  right: -6%;
  bottom: -12%;
  width: 480px;
  height: 480px;
  background: #0369a1;
  opacity: 0.35;
}

.auth-bg__orb--3 {
  top: 55%;
  left: 38%;
  width: 280px;
  height: 280px;
  background: #7c3aed;
  opacity: 0.25;
}

.auth-bg__shine {
  position: absolute;
  top: 0;
  left: 50%;
  width: 1px;
  height: 100%;
  background: linear-gradient(
    180deg,
    transparent 0%,
    rgba(255, 255, 255, 0.06) 35%,
    rgba(255, 255, 255, 0.02) 65%,
    transparent 100%
  );
  transform: translateX(-50%);
}
</style>
