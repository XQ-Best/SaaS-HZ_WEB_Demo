const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

export async function request(path, options = {}) {
  const { headers, body, ...rest } = options

  const response = await fetch(`${BASE_URL}${path}`, {
    ...rest,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  let data = {}
  try {
    data = await response.json()
  } catch {
    data = {}
  }

  if (!response.ok) {
    throw new Error(data.message || `请求失败 (${response.status})`)
  }

  return data
}
