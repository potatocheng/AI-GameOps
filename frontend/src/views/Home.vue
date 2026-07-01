<template>
  <div class="home">
    <div class="hero">
      <h1 class="title">欢迎使用 AI Operator</h1>
      <p class="subtitle">智能化的反馈管理与AI助手平台</p>
    </div>

    <div class="features">
      <div class="feature-card" v-for="feature in features" :key="feature.title">
        <div class="feature-icon">
          <component :is="feature.icon" />
        </div>
        <h3 class="feature-title">{{ feature.title }}</h3>
        <p class="feature-description">{{ feature.description }}</p>
        <router-link :to="feature.link" class="feature-link">
          前往使用 →
        </router-link>
      </div>
    </div>

    <div class="stats-overview" v-if="stats">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_feedbacks }}</div>
        <div class="stat-label">总反馈数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.pending_feedbacks }}</div>
        <div class="stat-label">待处理</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.resolved_feedbacks }}</div>
        <div class="stat-label">已解决</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_announcements }}</div>
        <div class="stat-label">公告数</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { getOverviewStats } from '@/api'

const stats = ref<{
  total_feedbacks: number
  pending_feedbacks: number
  resolved_feedbacks: number
  total_announcements: number
  active_announcements: number
} | null>(null)

// 图标组件
const FeedbackIcon = () => h('svg', { 
  viewBox: '0 0 24 24', 
  fill: 'none', 
  stroke: 'currentColor'
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
  stroke: 'currentColor'
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
  stroke: 'currentColor'
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
  stroke: 'currentColor'
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
  stroke: 'currentColor'
}, [
  h('path', { 
    'stroke-linecap': 'round', 
    'stroke-linejoin': 'round', 
    'stroke-width': '2', 
    d: 'M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z' 
  })
])

const features = [
  {
    title: '提交反馈',
    description: '快速提交您的反馈意见，我们会及时处理',
    icon: FeedbackIcon,
    link: '/feedback/submit'
  },
  {
    title: '反馈管理',
    description: '查看和管理所有反馈，跟踪处理状态',
    icon: ManageIcon,
    link: '/feedback/manage'
  },
  {
    title: 'AI助手',
    description: '与智能AI对话，获取即时帮助和建议',
    icon: AgentIcon,
    link: '/agent/chat'
  },
  {
    title: '数据看板',
    description: '可视化统计数据，掌握整体情况',
    icon: ChartIcon,
    link: '/stats/dashboard'
  },
  {
    title: '公告管理',
    description: '发布和管理系统公告信息',
    icon: AnnouncementIcon,
    link: '/announcement/manage'
  }
]

onMounted(async () => {
  stats.value = await getOverviewStats()
})
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px;
}

.hero {
  text-align: center;
  margin-bottom: 60px;
}

.title {
  font-size: 48px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 16px;
}

.subtitle {
  font-size: 20px;
  color: #666;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 60px;
}

.feature-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
}

.feature-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.feature-icon svg {
  width: 24px;
  height: 24px;
  color: white;
}

.feature-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #333;
}

.feature-description {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
}

.feature-link {
  display: inline-block;
  color: #667eea;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.3s;
}

.feature-link:hover {
  color: #764ba2;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

@media (max-width: 768px) {
  .title {
    font-size: 32px;
  }
  
  .subtitle {
    font-size: 16px;
  }
  
  .home {
    padding: 24px 16px;
  }
}
</style>