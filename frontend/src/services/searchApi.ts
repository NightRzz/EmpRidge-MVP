import { apiRequest } from './apiClient'
import type { Recipe } from '../types/recipe'

export type SearchRecipesRequest = {
  ingredient_ids: number[]
  category_id?: number
  area_id?: number
  min_matching_ratio?: number
  max_total_ingredients?: number
}

export type SearchRecipeItem = Recipe & {
  matched_count: number
  total_count: number
  matching_ratio: number
}

export async function searchRecipes(payload: SearchRecipesRequest): Promise<SearchRecipeItem[]> {
  return apiRequest<SearchRecipeItem[]>('/search-recipes', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
