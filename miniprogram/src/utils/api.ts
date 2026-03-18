type EnvRecord = Record<string, string | undefined>

const normalizeBaseUrl = (value: string) => {
  const trimmed = value.trim()
  if (!trimmed) {
    return ''
  }
  return trimmed.replace(/\/+$/, '')
}

const env = (import.meta as { env?: EnvRecord }).env || {}
const configuredApiBaseUrl = normalizeBaseUrl(env.VITE_API_BASE_URL || '')

export const API_BASE_URL = configuredApiBaseUrl || 'https://api.shxiejinf.cn'

export const buildApiUrl = (path: string) => {
  const value = (path || '').trim()
  if (!value) {
    return API_BASE_URL
  }
  if (/^https?:\/\//.test(value)) {
    return value
  }
  if (value.startsWith('//')) {
    return `https:${value}`
  }
  if (value.startsWith('/')) {
    return `${API_BASE_URL}${value}`
  }
  return `${API_BASE_URL}/${value}`
}

export const normalizeApiAssetUrl = (url: string) => {
  const value = (url || '').trim()
  if (!value) {
    return ''
  }
  if (value.startsWith('//')) {
    return `https:${value}`
  }
  if (value.startsWith('/')) {
    return `${API_BASE_URL}${value}`
  }
  const localhostMatch = value.match(/^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?(\/.*)?$/i)
  if (localhostMatch) {
    return `${API_BASE_URL}${localhostMatch[3] || ''}`
  }
  return value
}
