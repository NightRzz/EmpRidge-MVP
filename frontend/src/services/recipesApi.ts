import { apiRequest } from './apiClient'
import type { Recipe } from '../types/recipe'

export type RecipeIngredientAssignment = {
  ingredient_id: number
  measure: string | null
}

export type RecipePayload = {
  title: string
  instructions?: string | null
  image_url?: string | null
  youtube_url?: string | null
  category_id?: number | null
  area_id?: number | null
}

export async function listRecipes(skip = 0, limit = 24): Promise<Recipe[]> {
  return apiRequest<Recipe[]>(`/recipes?skip=${skip}&limit=${limit}`)
}

export async function fetchAllRecipes(pageSize = 200): Promise<Recipe[]> {
  const merged: Recipe[] = []
  let skip = 0
  while (true) {
    const batch = await listRecipes(skip, pageSize)
    merged.push(...batch)
    if (batch.length < pageSize) break
    skip += pageSize
  }
  return merged
}

export async function getRecipeById(recipeId: number): Promise<Recipe> {
  return apiRequest<Recipe>(`/recipes/${recipeId}`)
}

export async function createRecipe(data: RecipePayload): Promise<Recipe> {
  return apiRequest<Recipe>('/recipes', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateRecipe(id: number, data: Partial<RecipePayload>): Promise<Recipe> {
  return apiRequest<Recipe>(`/recipes/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteRecipe(id: number): Promise<void> {
  await apiRequest<{ deleted: boolean }>(`/recipes/${id}`, { method: 'DELETE' })
}

export async function replaceRecipeIngredients(
  recipeId: number,
  ingredients: RecipeIngredientAssignment[],
): Promise<Recipe> {
  return apiRequest<Recipe>(`/recipes/${recipeId}/ingredients`, {
    method: 'PUT',
    body: JSON.stringify({ ingredients }),
  })
}

