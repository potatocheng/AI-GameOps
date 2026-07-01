<template>
  <div class="stats-dashboard">
    <div class="page-header">
      <h1 class="page-title">数据看板</h1>
      <p class="page-description">实时统计与数据可视化</p>
    </div>

    <div class="stats-overview" v-if="overview">
      <div class="stat-card">
        <div class="stat-icon feedbacks">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ overview.total_feedbacks }}</div>
          <div class="stat-label">总反馈数</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon pending">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ overview.pending_feedbacks }}</div>
          <div class="stat-label">待处理</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon resolved">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ overview.resolved_feedbacks }}</div>
          <div class="stat-label">已解决</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon announcements">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
          </svg>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ overview.total_announcements }}</div>
          <div class="stat-label">公告数</div>
        </div>
      </div>
    </div>

    <div class="charts-section">
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">反馈趋势</h3>
          <select v-model="trendDays" @change="loadTrendData" class="chart-select">
            <option :value="7">近7天</option>
            <option :value="30">近30天</option>
            <option :value="90">近90天</option>
          </select>
        </div>
        <div class="chart-container">
          <Line :data="trendChartData" :options="trendChartOptions" v-if="trendData.length > 0" />
          <div v-else class="chart-empty">暂无数据</div>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">分类分布</h3>
        </div>
        <div class="chart-container">
          <Doughnut :data="categoryChartData" :options="categoryChartOptions" v-if="categoryData.length > 0" />
          <div v-else class="chart-empty">暂无数据</div>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">优先级分布</h3>
        </div>
        <div class="chart-container">
          <Bar :data="priorityChartData" :options="priorityChartOptions" v-if="priorityData.length > 0" />
          <div v-else class="chart-empty">暂无数据</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
} from 'chart.js'
import { Line, Doughnut, Bar } from 'vue-chartjs'
import { getOverviewStats, getTrendData, getCategoryDistribution, getPriorityDistribution } from '@/api'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
)

const overview = ref<{
  total_feedbacks: number
  pending_feedbacks: number
  resolved_feedbacks: number
  total_announcements: number
  active_announcements: number
} | null>(null)

const trendData = ref<{ date: string; count: number }[]>([])
const categoryData = ref<{ category: string; count: number }[]>([])
const priorityData = ref<{ priority: string; count: number }[]>([])
const trendDays = ref(7)

const trendChartData = computed(() => ({
  labels: trendData.value.map(item => item.date),
  datasets: [
    {
      label: '反馈数量',
      data: trendData.value.map(item => item.count),
      borderColor: '#667eea',
      backgroundColor: 'rgba(102, 126, 234, 0.1)',
      tension: 0.4,
      fill: true
    }
  ]
}))

const trendChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        stepSize: 1
      }
    }
  }
}

const categoryChartData = computed(() => ({
  labels: categoryData.value.map(item => getCategoryLabel(item.category)),
  datasets: [
    {
      data: categoryData.value.map(item => item.count),
      backgroundColor: [
        '#667eea',
        '#764ba2',
        '#f093fb',
        '#f5576c',
        '#4facfe',
        '#00f2fe'
      ]
    }
  ]
}))

const categoryChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const
    }
  }
}

const priorityChartData = computed(() => ({
  labels: priorityData.value.map(item => getPriorityLabel(item.priority)),
  datasets: [
    {
      label: '反馈数量',
      data: priorityData.value.map(item => item.count),
      backgroundColor: [
        '#10b981',
        '#f59e0b',
        '#ef4444',
        '#8b5cf6'
      ]
    }
  ]
}))

const priorityChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        stepSize: 1
      }
    }
  }
}

function getCategoryLabel(category: string): string {
  const labels: Record<string, string> = {
    bug: 'Bug反馈',
    feature: '功能建议',
    improvement: '改进建议',
    question: '问题咨询',
    complaint: '投诉',
    other: '其他'
  }
  return labels[category] || category
}

function getPriorityLabel(priority: string): string {
  const labels: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高',
    urgent: '紧急'
  }
  return labels[priority] || priority
}

async function loadOverview() {
  overview.value = await getOverviewStats()
}

async function loadTrendData() {
  const data = await getTrendData(trendDays.value)
  if (data) {
    trendData.value = data
  }
}

async function loadCategoryData() {
  const data = await getCategoryDistribution()
  if (data) {
    categoryData.value = data
  }
}

async function loadPriorityData() {
  const data = await getPriorityDistribution()
  if (data) {
    priorityData.value = data
  }
}

onMounted(() => {
  loadOverview()
  loadTrendData()
  loadCategoryData()
  loadPriorityData()
})
</script>

<style scoped>
.stats-dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 24px;
}

.page-header {
  margin-bottom: 40px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin-bottom: 12px;
}

.page-description {
  font-size: 16px;
  color: #666;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon svg {
  width: 28px;
  height: 28px;
  color: white;
}

.stat-icon.feedbacks {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.pending {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
}

.stat-icon.resolved {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
}

.stat-icon.announcements {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.chart-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.chart-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.chart-select {
  padding: 6px 12px;
  font-size: 13px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  cursor: pointer;
}

.chart-container {
  height: 300px;
  position: relative;
}

.chart-empty {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #999;
  font-size: 14px;
}

@media (max-width: 768px) {
  .stats-dashboard {
    padding: 24px 16px;
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .chart-card {
    min-width: 0;
  }
}
</style>