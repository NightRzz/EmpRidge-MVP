import { apiRequest } from './apiClient'

export type Category = {
  id: number
  name: string
}

export async function listCategories(): Promise<Category[]> {
  return apiRequest<Category[]>('/categories')
}
