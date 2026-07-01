import { get } from './request'
import type { StatsData } from '@/types'

// 获取统计数据
export async function getStats(): Promise<StatsData | null> {
  const response = await get<StatsData>('/api/stats')
  return response.success ? response.data || null : null
}

// 获取概览数据
export async function getOverviewStats(): Promise<{
  total_feedbacks: number
  pending_feedbacks: number
  resolved_feedbacks: number
  total_announcements: number
  active_announcements: number
} | null> {
  const response = await get<{
    total_feedbacks: number
    pending_feedbacks: number
    resolved_feedbacks: number
    total_announcements: number
    active_announcements: number
  }>('/api/stats/overview')
  return response.success ? response.data || null : null
}

// 获取趋势数据
export async function getTrendData(days: number = 7): Promise<{ date: string; count: number }[] | null> {
  const response = await get<{ date: string; count: number }[]>(`/api/stats/trend?days=${days}`)
  return response.success ? response.data || null : null
}

// 获取分类分布
export async function getCategoryDistribution(): Promise<{ category: string; count: number }[] | null> {
  const response = await get<{ category: string; count: number }[]>('/api/stats/categories')
  return response.success ? response.data || null : null
}

// 获取优先级分布
export async function getPriorityDistribution(): Promise<{ priority: string; count: number }[] | null> {
  const response = await get<{ priority: string; count: number }[]>('/api/stats/priorities')
  return response.success ? response.data || null : null
}