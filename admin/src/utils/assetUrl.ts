const IP_HOST_PATTERN = /^(?:\d{1,3}\.){3}\d{1,3}$/

const toLocalAssetUrl = (path: string) => {
  if (!path) return ''
  if (path.startsWith('/')) return `${window.location.origin}${path}`
  return `${window.location.origin}/${path}`
}

export const normalizeAssetUrl = (url: string) => {
  const value = (url || '').trim()
  if (!value) return ''
  if (value.startsWith('blob:') || value.startsWith('data:') || value.startsWith('file:')) {
    return value
  }
  if (value.startsWith('/uploads/')) {
    return toLocalAssetUrl(value)
  }
  if (value.startsWith('//')) {
    return `https:${value}`
  }
  if (!/^https?:\/\//i.test(value)) {
    return value
  }
  try {
    const parsed = new URL(value)
    if (parsed.pathname.startsWith('/uploads/')) {
      return toLocalAssetUrl(`${parsed.pathname}${parsed.search}${parsed.hash}`)
    }
    if (parsed.protocol === 'http:' && window.location.protocol === 'https:') {
      if (parsed.hostname === window.location.hostname || IP_HOST_PATTERN.test(parsed.hostname) || parsed.hostname === 'localhost' || parsed.hostname === '127.0.0.1') {
        parsed.protocol = 'https:'
        return parsed.toString()
      }
    }
    return value
  } catch {
    return value
  }
}

export const normalizeHtmlAssetUrls = (html: string) => {
  const value = (html || '').trim()
  if (!value) return ''
  return value.replace(/src=(["'])([^"']+)\1/gi, (match, quote, url) => {
    const normalized = normalizeAssetUrl(url)
    return `src=${quote}${normalized || url}${quote}`
  })
}
