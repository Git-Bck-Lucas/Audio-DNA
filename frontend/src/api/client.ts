const API_BASE_URL = import.meta.env.VITE_API_URL

export type MeResponse = {
  created_at: string
  // Kommt live von Spotify, wird serverseitig nicht gespeichert. null, wenn die
  // Spotify-API beim /me-Aufruf nicht erreichbar war.
  display_name: string | null
}

export async function fetchMe(): Promise<MeResponse | null> {
  const response = await fetch(`${API_BASE_URL}/spotify/me`, {
    credentials: 'include',
  })

  if (response.status === 401) return null
  if (!response.ok) throw new Error(`GET /spotify/me failed: ${response.status}`)

  return response.json()
}

export async function fetchLoginUrl(): Promise<string> {
  // credentials: 'include' ist Pflicht, sonst verwirft der Browser das Set-Cookie
  // der Response (Cross-Origin-Request) -- der oauth_state fuer den CSRF-Check
  // im Callback wuerde dann nie in der Session ankommen.
  const response = await fetch(`${API_BASE_URL}/spotify/login`, {
    credentials: 'include',
  })
  if (!response.ok) throw new Error(`GET /spotify/login failed: ${response.status}`)

  const data: { auth_url: string } = await response.json()
  return data.auth_url
}

export type Mode = 'science' | 'lucas'

export type TraitScore = {
  score: number
  confidence: 'high' | 'medium' | 'low'
  reasoning: string
}

export type PersonalityScores = {
  openness: TraitScore
  conscientiousness: TraitScore
  extraversion: TraitScore
  agreeableness: TraitScore
  neuroticism: TraitScore
}

export type Source = {
  author: string
  source: string
  text: string
  score: number
}

export type AnalysisResult = {
  id: number
  user_id: number
  created_at: string
  result: {
    personality: PersonalityScores
    sources: Source[]
    analysis_details: {
      top_artists: string[]
      genres_found: string[]
      artists_analyzed: number
      mainstream_score: number
    }
  }
}

export class RateLimitError extends Error {
  retryAfterSeconds: number | null

  constructor(retryAfterSeconds: number | null) {
    super('Rate limit exceeded')
    this.retryAfterSeconds = retryAfterSeconds
  }
}

export async function fetchAnalysis(mode: Mode): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE_URL}/analysis/get_personality?mode=${mode}`, {
    credentials: 'include',
  })

  if (response.status === 429) {
    const retryAfter = response.headers.get('Retry-After')
    throw new RateLimitError(retryAfter ? Number(retryAfter) : null)
  }
  if (!response.ok) throw new Error(`GET /analysis/get_personality failed: ${response.status}`)

  return response.json()
}

export async function logout(): Promise<void> {
  // redirect: 'manual', weil /spotify/logout selbst ein Redirect-Endpoint ist.
  // Wuerde fetch dem Redirect folgen, greift fuer den zweiten Hop (zurueck zum
  // eigenen Frontend-Origin) nochmal eine CORS-Pruefung, die der Vite-Dev-Server
  // fuer normale Seitenaufrufe nicht erfuellt -> fetch bricht mit CORS-Fehler ab.
  // Das Redirect-Ziel interessiert uns eh nicht, nur der Seiteneffekt (Cookie clearen).
  await fetch(`${API_BASE_URL}/spotify/logout`, {
    credentials: 'include',
    redirect: 'manual',
  })
}
