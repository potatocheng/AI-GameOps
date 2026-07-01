<template>
  <div class="announcement-manage">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">公告管理</h1>
        <p class="page-description">发布和管理系统公告</p>
      </div>
      <button class="btn btn-primary" @click="openCreateModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="btn-icon">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        发布公告
      </button>
    </div>

    <div class="filters-section">
      <select v-model="filters.is_active" class="filter-select" @change="loadAnnouncements">
        <option :value="undefined">全部公告</option>
        <option :value="true">已发布</option>
        <option :value="false">未发布</option>
      </select>
    </div>

    <div class="announcement-list" v-if="announcements.length > 0">
      <div 
        v-for="announcement in announcements" 
        :key="announcement.id" 
        class="announcement-card"
      >
        <div class="announcement-header">
          <div class="announcement-title-row">
            <h3 class="announcement-title">{{ announcement.title }}</h3>
            <span :class="['status-badge', announcement.is_active ? 'active' : 'inactive']">
              {{ announcement.is_active ? '已发布' : '未发布' }}
            </span>
          </div>
          <div class="announcement-meta">
            <span class="author">{{ announcement.author }}</span>
            <span class="separator">•</span>
            <span class="date">{{ formatDate(announcement.created_at) }}</span>
          </div>
        </div>
        
        <div class="announcement-content">
          {{ announcement.content }}
        </div>

        <div class="announcement-actions">
          <button 
            :class="['btn', 'btn-sm', announcement.is_active ? 'btn-secondary' : 'btn-success']"
            @click="toggleStatus(announcement.id)"
          >
            {{ announcement.is_active ? '取消发布' : '发布' }}
          </button>
          <button class="btn btn-sm btn-primary" @click="openEditModal(announcement)">
            编辑
          </button>
          <button class="btn btn-sm btn-danger" @click="handleDelete(announcement.id)">
            删除
          </button>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="empty-icon">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
      </svg>
      <p class="empty-text">暂无公告</p>
      <button class="btn btn-primary" @click="openCreateModal">发布公告</button>
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

    <!-- 创建/编辑模态框 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? '编辑公告' : '发布公告' }}</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        <form @submit.prevent="handleSubmit" class="modal-body">
          <div class="form-group">
            <label class="form-label">标题 *</label>
            <input
              v-model="formData.title"
              type="text"
              class="form-input"
              placeholder="请输入公告标题"
              required
            />
          </div>
          <div class="form-group">
            <label class="form-label">作者 *</label>
            <input
              v-model="formData.author"
              type="text"
              class="form-input"
              placeholder="请输入作者名称"
              required
            />
          </div>
          <div class="form-group">
            <label class="form-label">内容 *</label>
            <textarea
              v-model="formData.content"
              class="form-textarea"
              placeholder="请输入公告内容..."
              rows="6"
              required
            ></textarea>
          </div>
          <div class="form-group">
            <label class="form-checkbox">
              <input type="checkbox" v-model="formData.is_active" />
              <span>立即发布</span>
            </label>
          </div>
        </form>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeModal">取消</button>
          <button type="button" class="btn btn-primary" @click="handleSubmit">
            {{ isEditing ? '保存' : '发布' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getAnnouncements, createAnnouncement, updateAnnouncement, deleteAnnouncement, toggleAnnouncementStatus } from '@/api'
import type { Announcement, AnnouncementCreate } from '@/types'

const announcements = ref<Announcement[]>([])
const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)

const filters = reactive<{
  is_active: boolean | undefined
}>({
  is_active: undefined
})

const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0,
  total_pages: 0
})

const formData = reactive<AnnouncementCreate>({
  title: '',
  content: '',
  author: '',
  is_active: true
})

async function loadAnnouncements() {
  const result = await getAnnouncements({
    page: pagination.page,
    per_page: pagination.per_page,
    is_active: filters.is_active
  })
  
  announcements.value = result.items
  pagination.total = result.pagination.total
  pagination.total_pages = result.pagination.total_pages
}

function changePage(page: number) {
  pagination.page = page
  loadAnnouncements()
}

function openCreateModal() {
  isEditing.value = false
  editingId.value = null
  formData.title = ''
  formData.content = ''
  formData.author = ''
  formData.is_active = true
  showModal.value = true
}

function openEditModal(announcement: Announcement) {
  isEditing.value = true
  editingId.value = announcement.id
  formData.title = announcement.title
  formData.content = announcement.content
  formData.author = announcement.author
  formData.is_active = announcement.is_active
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  isEditing.value = false
  editingId.value = null
}

async function handleSubmit() {
  if (!formData.title || !formData.content || !formData.author) {
    alert('请填写所有必填项')
    return
  }

  if (isEditing.value && editingId.value) {
    await updateAnnouncement(editingId.value, formData)
  } else {
    await createAnnouncement(formData)
  }

  closeModal()
  loadAnnouncements()
}

async function toggleStatus(id: number) {
  await toggleAnnouncementStatus(id)
  loadAnnouncements()
}

async function handleDelete(id: number) {
  if (confirm('确定要删除这条公告吗？')) {
    await deleteAnnouncement(id)
    loadAnnouncements()
  }
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadAnnouncements()
})
</script>

<style scoped>
.announcement-manage {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.header-left {
  flex: 1;
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
  padding: 16px 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.filter-select {
  padding: 8px 16px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  cursor: pointer;
}

.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.announcement-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s;
}

.announcement-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.announcement-header {
  margin-bottom: 16px;
}

.announcement-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.announcement-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
  flex: 1;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background: #e2e3e5;
  color: #383d41;
}

.announcement-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #999;
}

.separator {
  color: #ddd;
}

.announcement-content {
  color: #555;
  line-height: 1.6;
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.announcement-actions {
  display: flex;
  gap: 12px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-icon {
  width: 16px;
  height: 16px;
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

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover {
  background: #059669;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn-sm {
  padding: 6px 16px;
  font-size: 13px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: white;
  border-radius: 12px;
}

.empty-icon {
  width: 64px;
  height: 64px;
  color: #ddd;
  margin-bottom: 16px;
}

.empty-text {
  color: #999;
  font-size: 16px;
  margin-bottom: 24px;
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

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  transition: all 0.3s;
  box-sizing: border-box;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
  font-family: inherit;
}

.form-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
}

.form-checkbox input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 16px 24px;
  border-top: 1px solid #eee;
}

@media (max-width: 768px) {
  .announcement-manage {
    padding: 24px 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .page-header .btn {
    width: 100%;
    justify-content: center;
  }
  
  .announcement-actions {
    flex-direction: column;
  }
  
  .announcement-actions .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>