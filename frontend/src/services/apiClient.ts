import type { ApiResponse } from '../types/api'
import { ApiClientError } from '../types/api'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })

  const payload = (await response.json()) as ApiResponse<T> | { detail?: string }

  if (!response.ok) {
    const detail = 'detail' in payload && payload.detail ? payload.detail : 'Błąd żądania API.'
    throw new ApiClientError(detail, response.status)
  }

  if (!('success' in payload) || !payload.success) {
    const message = 'error' in payload && payload.error ? payload.error : 'Backend zwrócił błąd.'
    throw new ApiClientError(message, response.status)
  }

  if (payload.data === null) {
    throw new ApiClientError('Brak danych w odpowiedzi API.', response.status)
  }

  return payload.data
}
