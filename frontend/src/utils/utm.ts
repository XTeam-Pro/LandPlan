/**
 * UTM tracking utilities.
 * Captures UTM parameters from URL on entry and stores them in sessionStorage.
 * Attaches them to API requests when needed.
 */

const UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'] as const

export interface UtmParams {
  utm_source?: string
  utm_medium?: string
  utm_campaign?: string
  utm_term?: string
  utm_content?: string
}

export function captureUtmParams(): void {
  const params = new URLSearchParams(window.location.search)
  const utm: UtmParams = {}
  let hasUtm = false

  for (const key of UTM_KEYS) {
    const value = params.get(key)
    if (value) {
      utm[key] = value
      hasUtm = true
    }
  }

  if (hasUtm) {
    sessionStorage.setItem('utm_params', JSON.stringify(utm))
  }
}

export function getUtmParams(): UtmParams {
  try {
    const stored = sessionStorage.getItem('utm_params')
    return stored ? JSON.parse(stored) : {}
  } catch {
    return {}
  }
}

export function appendUtmToUrl(url: string): string {
  const utm = getUtmParams()
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(utm)) {
    if (value) params.set(key, value)
  }
  const utmString = params.toString()
  if (!utmString) return url
  return url + (url.includes('?') ? '&' : '?') + utmString
}
