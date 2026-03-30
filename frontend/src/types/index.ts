// Estos tipos espejo los schemas Pydantic del backend
// Si el backend cambia, actualizas aquí y TypeScript
// te avisa en todos los sitios donde se usan

export interface User {
  id: string
  email: string
  full_name: string
  currency: string
  is_active: boolean
  created_at: string
}

export interface Portfolio {
  id: string
  user_id: string
  name: string
  description: string | null
  benchmark_ticker: string
  created_at: string
  updated_at: string
}

export interface Position {
  id: string
  portfolio_id: string
  ticker: string
  asset_type: string
  quantity: string
  avg_cost: string
  created_at: string
}

export interface Transaction {
  id: string
  position_id: string
  type: 'buy' | 'sell'
  quantity: string
  price: string
  total_value: string
  notes: string | null
  executed_at: string
}

export interface ChatMessage {
  role: 'human' | 'assistant'
  content: string
}

export interface ChatResponse {
  response: string
  thread_id: string
}

export interface Token {
  access_token: string
  token_type: string
}