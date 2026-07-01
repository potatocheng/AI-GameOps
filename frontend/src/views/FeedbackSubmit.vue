<template>
  <div class="feedback-submit">
    <div class="page-header">
      <h1 class="page-title">提交反馈</h1>
      <p class="page-description">我们重视您的每一条反馈意见</p>
    </div>

    <form @submit.prevent="handleSubmit" class="feedback-form">
      <div class="form-group">
        <label for="userId" class="form-label">
          <span class="label-text">用户ID</span>
          <span class="required">*</span>
        </label>
        <input
          id="userId"
          v-model="formData.user_id"
          type="text"
          class="form-input"
          placeholder="请输入您的用户ID"
          required
        />
      </div>

      <div class="form-group">
        <label for="category" class="form-label">
          <span class="label-text">反馈类别</span>
          <span class="required">*</span>
        </label>
        <select
          id="category"
          v-model="formData.category"
          class="form-select"
          required
        >
          <option value="">请选择类别</option>
          <option value="bug">Bug反馈</option>
          <option value="feature">功能建议</option>
          <option value="improvement">改进建议</option>
          <option value="question">问题咨询</option>
          <option value="complaint">投诉</option>
          <option value="other">其他</option>
        </select>
      </div>

      <div class="form-group">
        <label for="priority" class="form-label">
          <span class="label-text">优先级</span>
        </label>
        <select
          id="priority"
          v-model="formData.priority"
          class="form-select"
        >
          <option value="low">低</option>
          <option value="medium">中</option>
          <option value="high">高</option>
          <option value="urgent">紧急</option>
        </select>
      </div>

      <div class="form-group">
        <label for="content" class="form-label">
          <span class="label-text">反馈内容</span>
          <span class="required">*</span>
        </label>
        <textarea
          id="content"
          v-model="formData.content"
          class="form-textarea"
          placeholder="请详细描述您的反馈内容..."
          rows="6"
          required
        ></textarea>
      </div>

      <div class="form-group">
        <label class="form-label">
          <span class="label-text">标签（可选）</span>
        </label>
        <div class="tags-input">
          <div class="tags-container">
            <span 
              v-for="(tag, index) in formData.tags" 
              :key="index" 
              class="tag"
            >
              {{ tag }}
              <button 
                type="button" 
                class="tag-remove"
                @click="removeTag(index)"
              >
                ×
              </button>
            </span>
          </div>
          <input
            v-model="tagInput"
            type="text"
            class="tag-input"
            placeholder="输入标签后按回车添加"
            @keydown.enter.prevent="addTag"
          />
        </div>
      </div>

      <div class="form-actions">
        <button type="button" class="btn btn-secondary" @click="resetForm">
          重置
        </button>
        <button 
          type="submit" 
          class="btn btn-primary"
          :disabled="isSubmitting"
        >
          {{ isSubmitting ? '提交中...' : '提交反馈' }}
        </button>
      </div>
    </form>

    <div v-if="message.text" :class="['message', message.type]">
      {{ message.text }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { createFeedback } from '@/api'
import type { FeedbackCreate } from '@/types'

const formData = reactive<FeedbackCreate>({
  user_id: '',
  content: '',
  category: '',
  priority: 'medium',
  tags: []
})

const tagInput = ref('')
const isSubmitting = ref(false)
const message = ref<{ text: string; type: 'success' | 'error' }>({
  text: '',
  type: 'success'
})

function addTag() {
  const tag = tagInput.value.trim()
  if (tag && !formData.tags?.includes(tag)) {
    if (!formData.tags) {
      formData.tags = []
    }
    formData.tags.push(tag)
    tagInput.value = ''
  }
}

function removeTag(index: number) {
  formData.tags?.splice(index, 1)
}

async function handleSubmit() {
  if (!formData.user_id || !formData.content || !formData.category) {
    message.value = {
      text: '请填写所有必填项',
      type: 'error'
    }
    return
  }

  isSubmitting.value = true
  message.value.text = ''

  try {
    const result = await createFeedback(formData)
    
    if (result) {
      message.value = {
        text: '反馈提交成功！我们会尽快处理您的反馈。',
        type: 'success'
      }
      resetForm()
    } else {
      message.value = {
        text: '提交失败，请稍后重试。',
        type: 'error'
      }
    }
  } catch (error) {
    message.value = {
      text: '提交失败，请检查网络连接。',
      type: 'error'
    }
  } finally {
    isSubmitting.value = false
  }
}

function resetForm() {
  formData.user_id = ''
  formData.content = ''
  formData.category = ''
  formData.priority = 'medium'
  formData.tags = []
  tagInput.value = ''
}
</script>

<style scoped>
.feedback-submit {
  max-width: 800px;
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

.feedback-form {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.label-text {
  margin-right: 4px;
}

.required {
  color: #e74c3c;
}

.form-input,
.form-select,
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
.form-select:focus,
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

.tags-input {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 8px;
  transition: all 0.3s;
}

.tags-input:focus-within {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px;
  font-size: 13px;
}

.tag-remove {
  background: none;
  border: none;
  color: white;
  font-size: 16px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  opacity: 0.8;
  transition: opacity 0.3s;
}

.tag-remove:hover {
  opacity: 1;
}

.tag-input {
  border: none;
  outline: none;
  font-size: 14px;
  width: 100%;
  padding: 4px;
}

.form-actions {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  margin-top: 32px;
}

.btn {
  padding: 12px 32px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f5f5f5;
  color: #666;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.message {
  margin-top: 24px;
  padding: 16px;
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

@media (max-width: 768px) {
  .feedback-submit {
    padding: 24px 16px;
  }
  
  .feedback-form {
    padding: 24px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>