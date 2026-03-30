import { apiClient } from './client'
import type { Portfolio, Position } from '../types'

export const portfoliosApi = {
  getAll: async (): Promise<Portfolio[]> => {
    const response = await apiClient.get<Portfolio[]>('/api/portfolios')
    return response.data
  },

  getById: async (id: string): Promise<Portfolio> => {
    const response = await apiClient.get<Portfolio>(`/api/portfolios/${id}`)
    return response.data
  },

  create: async (data: {
    name: string
    description?: string
    benchmark_ticker?: string
  }): Promise<Portfolio> => {
    const response = await apiClient.post<Portfolio>('/api/portfolios', data)
    return response.data
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/portfolios/${id}`)
  },

  getPositions: async (portfolioId: string): Promise<Position[]> => {
    const response = await apiClient.get<Position[]>(
      `/api/portfolios/${portfolioId}/positions`
    )
    return response.data
  },

  createPosition: async (
    portfolioId: string,
    data: {
      ticker: string
      asset_type: string
      quantity: string
      avg_cost: string
    }
  ): Promise<Position> => {
    const response = await apiClient.post<Position>(
      `/api/portfolios/${portfolioId}/positions`,
      data
    )
    return response.data
  },
}