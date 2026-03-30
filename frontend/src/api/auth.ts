import { apiClient } from './client'
import type { Token, User } from '../types'

export const authApi = {
  login: async (email: string, password: string): Promise<Token> => {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)
    const response = await apiClient.post<Token>('/api/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return response.data
  },

  register: async (data: {
    email: string
    password: string
    full_name: string
    currency?: string
  }): Promise<User> => {
    const response = await apiClient.post<User>('/api/auth/register', data)
    return response.data
  },

  getMe: async (): Promise<User> => {
    const response = await apiClient.get<User>('/api/auth/me')
    return response.data
  },
}