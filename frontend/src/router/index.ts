import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/feedback/submit',
    name: 'FeedbackSubmit',
    component: () => import('@/views/FeedbackSubmit.vue'),
    meta: { title: '提交反馈' }
  },
  {
    path: '/feedback/manage',
    name: 'FeedbackManage',
    component: () => import('@/views/FeedbackManage.vue'),
    meta: { title: '反馈管理' }
  },
  {
    path: '/agent/chat',
    name: 'AgentChat',
    component: () => import('@/views/AgentChat.vue'),
    meta: { title: 'AI助手' }
  },
  {
    path: '/stats/dashboard',
    name: 'StatsDashboard',
    component: () => import('@/views/StatsDashboard.vue'),
    meta: { title: '数据看板' }
  },
  {
    path: '/announcement/manage',
    name: 'AnnouncementManage',
    component: () => import('@/views/AnnouncementManage.vue'),
    meta: { title: '公告管理' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 设置页面标题
router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || '页面'} - AI Operator`
  next()
})

export default router