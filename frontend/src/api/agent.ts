import { post } from './request'
import type { ChatRequest, ChatResponse } from '@/types'

// 发送消息给AI Agent
export async function sendMessage(data: ChatRequest): Promise<ChatResponse | null> {
  const response = await post<ChatResponse>('/api/agent/chat', data)
  return response.success ? response.data || null : null
}

// 获取对话历史
export async function getChatHistory(userId: string, limit: number = 50): Promise<ChatResponse[]> {
  const response = await post<ChatResponse[]>('/api/agent/history', { user_id: userId, limit })
  return response.success ? response.data || [] : []
}

// 清空对话历史
export async function clearChatHistory(userId: string): Promise<boolean> {
  const response = await post<{ message: string }>('/api/agent/clear-history', { user_id: userId })
  return response.success
}