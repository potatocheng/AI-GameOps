<template>
  <div class="feedback-manage">
    <div class="page-header">
      <h1 class="page-title">反馈管理</h1>
      <p class="page-description">管理和处理用户反馈</p>
    </div>

    <div class="filters-section">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="搜索反馈内容..."
          @input="handleSearch"
        />
      </div>

      <div class="filter-controls">
        <select v-model="filters.status" class="filter-select" @change="loadFeedbacks">
          <option value="">所有状态</option>
          <option value="pending">待处理</option>
          <option value="processing">处理中</option>
          <option value="resolved">已解决</option>
          <option value="closed">已关闭</option>
        </select>

        <select v-model="filters.category" class="filter-select" @change="loadFeedbacks">
          <option value="">所有类别</option>
          <option value="bug">Bug反馈</option>
          <option value="feature">功能建议</option>
          <option value="improvement">改进建议</option>
          <option value="question">问题咨询</option>
          <option value="complaint">投诉</option>
          <option value="other">其他</option>
        </select>

        <select v-model="filters.priority" class="filter-select" @change="loadFeedbacks">
          <option value="">所有优先级</option>
          <option value="low">低</option>
          <option value="medium">中</option>
          <option value="high">高</option>
          <option value="urgent">紧急</option>
        </select>
      </div>
    </div>

    <div class="feedback-list" v-if="feedbacks.length > 0">
      <div 
        v-for="feedback in feedbacks" 
        :key="feedback.id" 
        class="feedback-card"
      >
        <div class="feedback-header">
          <div class="feedback-meta">
            <span class="feedback-id">#{{ feedback.id }}</span>
            <span :class="['status-badge', `status-${feedback.status}`]">
              {{ getStatusText(feedback.status) }}
            </span>
            <span :class="['priority-badge', `priority-${feedback.priority}`]">
              {{ getPriorityText(feedback.priority) }}
            </span>
            <span class="category-badge">{{ getCategoryText(feedback.category) }}</span>
          </div>
          <div class="feedback-date">{{ formatDate(feedback.created_at) }}</div>
        </div>

        <div class="feedback-content">
          <div class="feedback-user">用户ID: {{ feedback.user_id }}</div>
          <p class="feedback-text">{{ feedback.content }}</p>
          <div v-if="feedback.tags && feedback.tags.length > 0" class="feedback-tags">
            <span v-for="tag in feedback.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </div>

        <div v-if="feedback.admin_reply" class="admin-reply">
          <div class="reply-header">管理员回复:</div>
          <p class="reply-text">{{ feedback.admin_reply }}</p>
        </div>

        <div class="feedback-actions">
          <button 
            class="btn btn-sm"
            @click="openReplyModal(feedback)"
          >
            回复
          </button>
          <select 
            :value="feedback.status"
            class="status-select"
            @change="(e) => updateStatus(feedback.id, (e.target as HTMLSelectElement).value)"
          >
            <option value="pending">待处理</option>
            <option value="processing">处理中</option>
            <option value="resolved">已解决</option>
            <option value="closed">已关闭</option>
          </select>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <p class="empty-text">暂无反馈数据</p>
    </div>

    <div v-if="pagination.total_pages > 1" class="pagination">
      <button 
        class="pagination-btn"
        :disabled="pagination.page === 1"
        @click="changePage(pagination.page - 1)"
      >
        上一页
      </button>
      <span class="pagination-info">
        第 {{ pagination.page }} / {{ pagination.total_pages }} 页
      </span>
      <button 
        class="pagination-btn"
        :disabled="pagination.page === pagination.total_pages"
        @click="changePage(pagination.page + 1)"
      >
        下一页
      </button>
    </div>

    <!-- 回复模态框 -->
    <div v-if="showReplyModal" class="modal-overlay" @click="closeReplyModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>回复反馈 #{{ selectedFeedback?.id }}</h3>
          <button class="modal-close" @click="closeReplyModal">×</button>
        </div>
        <div class="modal-body">
          <textarea
            v-model="replyContent"
            class="reply-textarea"
            placeholder="请输入回复内容..."
            rows="6"
          ></textarea>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeReplyModal">取消</button>
          <button class="btn btn-primary" @click="submitReply">提交回复</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getFeedbacks, updateFeedback } from '@/api'
import type { Feedback } from '@/types'

const feedbacks = ref<Feedback[]>([])
const searchQuery = ref('')
const showReplyModal = ref(false)
const selectedFeedback = ref<Feedback | null>(null)
const replyContent = ref('')

const filters = reactive({
  status: '',
  category: '',
  priority: ''
})

const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0,
  total_pages: 0
})

let searchTimeout: number | null = null

function handleSearch() {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = window.setTimeout(() => {
    loadFeedbacks()
  }, 300)
}

async function loadFeedbacks() {
  const result = await getFeedbacks({
    page: pagination.page,
    per_page: pagination.per_page,
    status: filters.status,
    category: filters.category,
    priority: filters.priority,
    search: searchQuery.value
  })
  
  feedbacks.value = result.items
  pagination.total = result.pagination.total
  pagination.total_pages = result.pagination.total_pages
}

function changePage(page: number) {
  pagination.page = page
  loadFeedbacks()
}

async function updateStatus(id: number, status: string) {
  await updateFeedback(id, { status: status as any })
  loadFeedbacks()
}

function openReplyModal(feedback: Feedback) {
  selectedFeedback.value = feedback
  replyContent.value = feedback.admin_reply || ''
  showReplyModal.value = true
}

function closeReplyModal() {
  showReplyModal.value = false
  selectedFeedback.value = null
  replyContent.value = ''
}

async function submitReply() {
  if (!selectedFeedback.value || !replyContent.value.trim()) return
  
  await updateFeedback(selectedFeedback.value.id, {
    admin_reply: replyContent.value.trim(),
    status: 'resolved'
  })
  
  closeReplyModal()
  loadFeedbacks()
}

function getStatusText(status: string): string {
  const statusMap: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    resolved: '已解决',
    closed: '已关闭'
  }
  return statusMap[status] || status
}

function getPriorityText(priority: string): string {
  const priorityMap: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高',
    urgent: '紧急'
  }
  return priorityMap[priority] || priority
}

function getCategoryText(category: string): string {
  const categoryMap: Record<string, string> = {
    bug: 'Bug反馈',
    feature: '功能建议',
    improvement: '改进建议',
    question: '问题咨询',
    complaint: '投诉',
    other: '其他'
  }
  return categoryMap[category] || category
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadFeedbacks()
})
</script>

<style scoped>
.feedback-manage {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px;
}

.page-header {
  margin-bottom: 32px;
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

.filters-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.search-box {
  margin-bottom: 16px;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  transition: all 0.3s;
  box-sizing: border-box;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.filter-controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-select {
  padding: 8px 12px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.filter-select:focus {
  outline: none;
  border-color: #667eea;
}

.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feedback-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s;
}

.feedback-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.feedback-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.feedback-id {
  font-weight: 600;
  color: #667eea;
}

.status-badge,
.priority-badge,
.category-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-pending {
  background: #fff3cd;
  color: #856404;
}

.status-processing {
  background: #cce5ff;
  color: #004085;
}

.status-resolved {
  background: #d4edda;
  color: #155724;
}

.status-closed {
  background: #e2e3e5;
  color: #383d41;
}

.priority-low {
  background: #e7f3ff;
  color: #0066cc;
}

.priority-medium {
  background: #fff3cd;
  color: #856404;
}

.priority-high {
  background: #ffe5e5;
  color: #cc0000;
}

.priority-urgent {
  background: #ff4444;
  color: white;
}

.category-badge {
  background: #f0f0f0;
  color: #666;
}

.feedback-date {
  font-size: 13px;
  color: #999;
}

.feedback-content {
  margin-bottom: 16px;
}

.feedback-user {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
}

.feedback-text {
  color: #333;
  line-height: 1.6;
  margin-bottom: 12px;
}

.feedback-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  padding: 2px 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  font-size: 12px;
}

.admin-reply {
  background: #f8f9fa;
  border-left: 4px solid #667eea;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.reply-header {
  font-weight: 600;
  color: #667eea;
  margin-bottom: 8px;
}

.reply-text {
  color: #333;
  line-height: 1.6;
}

.feedback-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.btn {
  padding: 8px 20px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-sm {
  padding: 6px 16px;
  font-size: 13px;
  background: #667eea;
  color: white;
}

.btn-sm:hover {
  background: #5568d3;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: #f5f5f5;
  color: #666;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.status-select {
  padding: 6px 12px;
  font-size: 13px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  cursor: pointer;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
}

.empty-text {
  color: #999;
  font-size: 16px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 32px;
}

.pagination-btn {
  padding: 8px 20px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.pagination-btn:hover:not(:disabled) {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 14px;
  color: #666;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s;
}

.modal-close:hover {
  background: #f5f5f5;
  color: #333;
}

.modal-body {
  padding: 24px;
  flex: 1;
  overflow-y: auto;
}

.reply-textarea {
  width: 100%;
  padding: 12px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: vertical;
  min-height: 150px;
  font-family: inherit;
  box-sizing: border-box;
}

.reply-textarea:focus {
  outline: none;
  border-color: #667eea;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 16px 24px;
  border-top: 1px solid #eee;
}

@media (max-width: 768px) {
  .feedback-manage {
    padding: 24px 16px;
  }
  
  .filter-controls {
    flex-direction: column;
  }
  
  .filter-select {
    width: 100%;
  }
  
  .feedback-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .feedback-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .status-select {
    width: 100%;
  }
}
</style>