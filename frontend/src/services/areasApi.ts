import { apiRequest } from './apiClient'

export type Area = {
  id: number
  name: string
}

export async function listAreas(): Promise<Area[]> {
  return apiRequest<Area[]>('/areas')
}
