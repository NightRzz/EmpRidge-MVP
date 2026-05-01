import { apiRequest } from './apiClient'
import type { Ingredient } from '../types/ingredient'

export async function listIngredients(skip = 0, limit = 100): Promise<Ingredient[]> {
  return apiRequest<Ingredient[]>(`/ingredients?skip=${skip}&limit=${limit}`)
}

/** Pełny katalog składników — agregacja stron po stronie klienta. */
export async function fetchAllIngredients(pageSize = 250): Promise<Ingredient[]> {
  const merged: Ingredient[] = []
  let skip = 0
  while (true) {
    const batch = await listIngredients(skip, pageSize)
    merged.push(...batch)
    if (batch.length < pageSize) break
    skip += pageSize
  }
  return merged
}

export async function suggestIngredients(query: string, limit = 10): Promise<Ingredient[]> {
  return apiRequest<Ingredient[]>(
    `/ingredients/suggestions?query=${encodeURIComponent(query)}&limit=${limit}`,
  )
}

export async function createIngredient(data: { name: string; image_url: string }): Promise<Ingredient> {
  return apiRequest<Ingredient>('/ingredients', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateIngredient(
  id: number,
  data: { name?: string; image_url?: string },
): Promise<Ingredient> {
  return apiRequest<Ingredient>(`/ingredients/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteIngredient(id: number): Promise<void> {
  await apiRequest<{ deleted: boolean }>(`/ingredients/${id}`, { method: 'DELETE' })
}

