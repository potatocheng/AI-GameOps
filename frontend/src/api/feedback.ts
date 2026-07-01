import { get, post, put } from './request'
import type { Feedback, FeedbackCreate, FeedbackUpdate, PaginatedResponse } from '@/types'

// 获取反馈列表
export async function getFeedbacks(params?: {
  page?: number
  per_page?: number
  status?: string
  category?: string
  priority?: string
  search?: string
}): Promise<PaginatedResponse<Feedback>> {
  const queryParams = new URLSearchParams()
  
  if (params?.page) queryParams.append('page', params.page.toString())
  if (params?.per_page) queryParams.append('per_page', params.per_page.toString())
  if (params?.status) queryParams.append('status', params.status)
  if (params?.category) queryParams.append('category', params.category)
  if (params?.priority) queryParams.append('priority', params.priority)
  if (params?.search) queryParams.append('search', params.search)
  
  const response = await get<PaginatedResponse<Feedback>>(`/api/feedbacks?${queryParams.toString()}`)
  
  if (response.success && response.data) {
    return response.data
  }
  
  return {
    items: [],
    pagination: {
      page: 1,
      per_page: 10,
      total: 0,
      total_pages: 0
    }
  }
}

// 获取单个反馈
export async function getFeedback(id: number): Promise<Feedback | null> {
  const response = await get<Feedback>(`/api/feedbacks/${id}`)
  return response.success ? response.data || null : null
}

// 创建反馈
export async function createFeedback(data: FeedbackCreate): Promise<Feedback | null> {
  const response = await post<Feedback>('/api/feedbacks', data)
  return response.success ? response.data || null : null
}

// 更新反馈
export async function updateFeedback(id: number, data: FeedbackUpdate): Promise<Feedback | null> {
  const response = await put<Feedback>(`/api/feedbacks/${id}`, data)
  return response.success ? response.data || null : null
}

// 删除反馈
export async function deleteFeedback(id: number): Promise<boolean> {
  const response = await get<{ message: string }>(`/api/feedbacks/${id}/delete`)
  return response.success
}

// 获取反馈统计
export async function getFeedbackStats(): Promise<{
  total: number
  pending: number
  processing: number
  resolved: number
  closed: number
}> {
  const response = await get<{
    total: number
    pending: number
    processing: number
    resolved: number
    closed: number
  }>('/api/feedbacks/stats')
  
  if (response.success && response.data) {
    return response.data
  }
  
  return {
    total: 0,
    pending: 0,
    processing: 0,
    resolved: 0,
    closed: 0
  }
}