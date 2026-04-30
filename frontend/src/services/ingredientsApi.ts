import { apiRequest } from './apiClient'
import type { Ingredient } from '../types/ingredient'

export async function listIngredients(skip = 0, limit = 100): Promise<Ingredient[]> {
  return apiRequest<Ingredient[]>(`/ingredients?skip=${skip}&limit=${limit}`)
}

export async function suggestIngredients(query: string, limit = 10): Promise<Ingredient[]> {
  return apiRequest<Ingredient[]>(
    `/ingredients/suggestions?query=${encodeURIComponent(query)}&limit=${limit}`,
  )
}
