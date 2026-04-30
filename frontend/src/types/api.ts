export type ApiResponse<T> = {
  success: boolean
  data: T | null
  error?: string | null
  message?: string | null
}

export class ApiClientError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiClientError'
    this.status = status
  }
}
