const API_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

export async function apiRequest(path, { token, body, ...options } = {}) {
  const headers = new Headers(options.headers || {})
  if (body !== undefined) headers.set('Content-Type', 'application/json')
  if (token) headers.set('Authorization', `Bearer ${token}`)

  let response
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new Error('Cannot reach StudentAI. Check that the backend is running.')
  }

  const data = await response.json().catch(() => null)
  if (!response.ok) {
    const detail = data?.detail
    const message = Array.isArray(detail)
      ? detail.map(item => item.msg).join(' ')
      : detail || 'The request could not be completed.'
    const error = new Error(message)
    error.status = response.status
    throw error
  }

  return data
}
