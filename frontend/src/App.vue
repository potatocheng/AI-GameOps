<template>
  <div id="app">
    <Navigation />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import Navigation from './components/Navigation.vue'
</script>

<style>
#app {
  min-height: 100vh;
  background: #f5f7fa;
}

.main-content {
  padding-top: 64px;
  min-height: calc(100vh - 64px);
}
</style>