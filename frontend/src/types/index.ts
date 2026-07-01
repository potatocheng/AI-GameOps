// 反馈相关类型
export interface Feedback {
  id: number
  user_id: string
  content: string
  category: string
  status: 'pending' | 'processing' | 'resolved' | 'closed'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  created_at: string
  updated_at: string
  admin_reply?: string
  tags?: string[]
}

export interface FeedbackCreate {
  user_id: string
  content: string
  category: string
  priority?: 'low' | 'medium' | 'high' | 'urgent'
  tags?: string[]
}

export interface FeedbackUpdate {
  status?: 'pending' | 'processing' | 'resolved' | 'closed'
  admin_reply?: string
  priority?: 'low' | 'medium' | 'high' | 'urgent'
}

// 公告相关类型
export interface Announcement {
  id: number
  title: string
  content: string
  author: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface AnnouncementCreate {
  title: string
  content: string
  author: string
  is_active?: boolean
}

// AI Agent 相关类型
export interface ChatMessage {
  id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
}

export interface ChatRequest {
  message: string
  user_id?: string
  context?: string[]
}

export interface ChatResponse {
  response: string
  message_id: number
  timestamp: string
}

// 统计数据相关类型
export interface StatsOverview {
  total_feedbacks: number
  pending_feedbacks: number
  resolved_feedbacks: number
  total_announcements: number
  active_announcements: number
}

export interface CategoryStats {
  category: string
  count: number
  percentage: number
}

export interface TrendData {
  date: string
  count: number
}

export interface StatsData {
  overview: StatsOverview
  category_distribution: CategoryStats[]
  trend_data: TrendData[]
  priority_distribution: CategoryStats[]
}

// API 响应类型
export interface ApiResponse<T> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// 分页类型
export interface Pagination {
  page: number
  per_page: number
  total: number
  total_pages: number
}

export interface PaginatedResponse<T> {
  items: T[]
  pagination: Pagination
}