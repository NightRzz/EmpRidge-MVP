import { apiRequest } from './apiClient'
import type { Recipe } from '../types/recipe'

export async function listRecipes(skip = 0, limit = 24): Promise<Recipe[]> {
  return apiRequest<Recipe[]>(`/recipes?skip=${skip}&limit=${limit}`)
}

export async function getRecipeById(recipeId: number): Promise<Recipe> {
  return apiRequest<Recipe>(`/recipes/${recipeId}`)
}
