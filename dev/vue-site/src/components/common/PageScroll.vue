<template>
  <div class="page-scroll">
    <div v-if="$slots.header" class="page-scroll-header">
      <slot name="header" />
    </div>
    <div class="page-scroll-body">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.page-scroll {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page-scroll-header {
  flex-shrink: 0;
}

.page-scroll-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
}
</style>
