<template>
  <nav class="navigation">
    <div class="nav-brand">
      <router-link to="/" class="brand-link">
        <svg class="brand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <span class="brand-text">AI Operator</span>
      </router-link>
    </div>
    
    <div class="nav-menu" :class="{ active: isMenuOpen }">
      <router-link 
        v-for="item in menuItems" 
        :key="item.path" 
        :to="item.path"
        class="nav-item"
        :class="{ active: isActive(item.path) }"
        @click="closeMenu"
      >
        <component :is="item.icon" class="nav-icon" />
        <span>{{ item.title }}</span>
      </router-link>
    </div>

    <button class="menu-toggle" @click="toggleMenu">
      <svg class="menu-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path v-if="!isMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </nav>
</template>

<script setup lang="ts">
import { ref, h } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isMenuOpen = ref(false)

// 图标组件
const HomeIcon = () => h('svg', { 
  viewBox: '0 0 24 24', 
  fill: 'none', 
  stroke: 'currentColor',
  class: 'icon'
}, [
  h('path', { 
    'stroke-linecap': 'round', 
    'stroke-linejoin': 'round', 
    'stroke-width': '2', 
    d: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' 
  })
])

const FeedbackIcon = () => h('svg', { 
  viewBox: '0 0 24 24', 
  fill: 'none', 
  stroke: 'currentColor',
  class: 'icon'
}, [
  h('path', { 
    'stroke-linecap': 'round', 
    'stroke-linejoin': 'round', 
    'stroke-width': '2', 
    d: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z' 
  })
])

const ManageIcon = () => h('svg', { 
  viewBox: '0 0 24 24', 
  fill: 'none', 
  stroke: 'currentColor',
  class: 'icon'
}, [
  h('path', { 
    'stroke-linecap': 'round', 
    'stroke-linejoin': 'round', 
    'stroke-width': '2', 
    d: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01' 
  })
])

const AgentIcon = () => h('svg', { 
  viewBox: '0 0 24 24', 
  fill: 'none', 
  stroke: 'currentColor',
  class: 'icon'
}, [
  h('path', { 
    'stroke-linecap': 'round', 
    'stroke-linejoin': 'round', 
    'stroke-width': '2', 
    d: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' 
  })
])

const ChartIcon = () => h('svg', { 
  viewBox: '0 0 24 24', 
  fill: 'none', 
  stroke: 'currentColor',
  class: 'icon'
}, [
  h('path', { 
    'stroke-linecap': 'round', 
    'stroke-linejoin': 'round', 
    'stroke-width': '2', 
    d: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' 
  })
])

const AnnouncementIcon = () => h('svg', { 
  viewBox: '0 0 24 24', 
  fill: 'none', 
  stroke: 'currentColor',
  class: 'icon'
}, [
  h('path', { 
    'stroke-linecap': 'round', 
    'stroke-linejoin': 'round', 
    'stroke-width': '2', 
    d: 'M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z' 
  })
])

const menuItems = [
  { path: '/', title: '首页', icon: HomeIcon },
  { path: '/feedback/submit', title: '提交反馈', icon: FeedbackIcon },
  { path: '/feedback/manage', title: '反馈管理', icon: ManageIcon },
  { path: '/agent/chat', title: 'AI助手', icon: AgentIcon },
  { path: '/stats/dashboard', title: '数据看板', icon: ChartIcon },
  { path: '/announcement/manage', title: '公告管理', icon: AnnouncementIcon }
]

function isActive(path: string): boolean {
  return route.path === path
}

function toggleMenu() {
  isMenuOpen.value = !isMenuOpen.value
}

function closeMenu() {
  isMenuOpen.value = false
}
</script>

<style scoped>
.navigation {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  padding: 0 24px;
  z-index: 1000;
}

.nav-brand {
  flex-shrink: 0;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
  text-decoration: none;
  font-size: 20px;
  font-weight: 600;
  transition: opacity 0.3s;
}

.brand-link:hover {
  opacity: 0.9;
}

.brand-icon {
  width: 28px;
  height: 28px;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 48px;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s;
  font-size: 14px;
  font-weight: 500;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.nav-icon {
  width: 18px;
  height: 18px;
}

.menu-toggle {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  color: white;
}

.menu-icon {
  width: 24px;
  height: 24px;
}

@media (max-width: 1024px) {
  .nav-menu {
    position: fixed;
    top: 64px;
    left: 0;
    right: 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    flex-direction: column;
    padding: 16px;
    gap: 8px;
    transform: translateY(-100%);
    opacity: 0;
    transition: all 0.3s ease;
    pointer-events: none;
  }

  .nav-menu.active {
    transform: translateY(0);
    opacity: 1;
    pointer-events: auto;
  }

  .nav-item {
    width: 100%;
    justify-content: flex-start;
    padding: 12px 16px;
    font-size: 16px;
  }

  .menu-toggle {
    display: block;
    margin-left: auto;
  }
}
</style>