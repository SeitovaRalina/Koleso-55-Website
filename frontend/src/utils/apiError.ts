import axios from 'axios'

type ApiErrorBody = {
  detail?: string
  message?: string
  [key: string]: unknown
}

export function getApiErrorMessage(error: unknown, fallback: string) {
  if (!axios.isAxiosError<ApiErrorBody>(error)) return fallback

  const data = error.response?.data
  if (!data) return fallback
  if (typeof data === 'string') return data
  if (data.detail) return data.detail
  if (data.message) return data.message

  const firstValue = Object.values(data)[0]
  if (Array.isArray(firstValue) && typeof firstValue[0] === 'string') {
    return firstValue[0]
  }
  if (typeof firstValue === 'string') return firstValue

  return fallback
}

export function formatApiFieldErrors(error: unknown, fallback: string) {
  if (!axios.isAxiosError<ApiErrorBody>(error)) return fallback

  const data = error.response?.data
  if (!data) return fallback
  if (typeof data === 'string') return data
  if (data.detail) return data.detail

  const messages = Object.entries(data).flatMap(([field, value]) => {
    if (Array.isArray(value)) return value.map(item => `${field}: ${String(item)}`)
    if (typeof value === 'string') return [`${field}: ${value}`]
    return []
  })

  return messages.join(' | ') || fallback
}

export function getApiErrorData(error: unknown): ApiErrorBody | string | undefined {
  if (!axios.isAxiosError<ApiErrorBody>(error)) return undefined
  return error.response?.data
}
