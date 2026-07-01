import { get, post, put, del } from './request'
import type { Announcement, AnnouncementCreate, PaginatedResponse } from '@/types'

// 获取公告列表
export async function getAnnouncements(params?: {
  page?: number
  per_page?: number
  is_active?: boolean
}): Promise<PaginatedResponse<Announcement>> {
  const queryParams = new URLSearchParams()
  
  if (params?.page) queryParams.append('page', params.page.toString())
  if (params?.per_page) queryParams.append('per_page', params.per_page.toString())
  if (params?.is_active !== undefined) queryParams.append('is_active', params.is_active.toString())
  
  const response = await get<PaginatedResponse<Announcement>>(`/api/announcements?${queryParams.toString()}`)
  
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

// 获取单个公告
export async function getAnnouncement(id: number): Promise<Announcement | null> {
  const response = await get<Announcement>(`/api/announcements/${id}`)
  return response.success ? response.data || null : null
}

// 创建公告
export async function createAnnouncement(data: AnnouncementCreate): Promise<Announcement | null> {
  const response = await post<Announcement>('/api/announcements', data)
  return response.success ? response.data || null : null
}

// 更新公告
export async function updateAnnouncement(id: number, data: Partial<AnnouncementCreate>): Promise<Announcement | null> {
  const response = await put<Announcement>(`/api/announcements/${id}`, data)
  return response.success ? response.data || null : null
}

// 删除公告
export async function deleteAnnouncement(id: number): Promise<boolean> {
  const response = await del<{ message: string }>(`/api/announcements/${id}`)
  return response.success
}

// 切换公告状态
export async function toggleAnnouncementStatus(id: number): Promise<Announcement | null> {
  const response = await put<Announcement>(`/api/announcements/${id}/toggle-status`)
  return response.success ? response.data || null : null
}