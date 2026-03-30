import { apiClient } from './client'
import type { ChatResponse, ChatMessage } from '../types'

export const agentApi = {
  chat: async (message: string, threadId: string): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>('/api/agent/chat', {
      message,
      thread_id: threadId,
    })
    return response.data
  },

  getHistory: async (threadId: string): Promise<ChatMessage[]> => {
    const response = await apiClient.get<{ messages: ChatMessage[] }>(
      `/api/agent/threads/${threadId}/history`
    )
    return response.data.messages
  },
}