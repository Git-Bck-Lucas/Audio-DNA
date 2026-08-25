import { useEffect, useReducer } from 'react'
import { authReducer, initialAuthState } from './state/authMachine'
import { fetchLoginUrl, fetchMe, logout } from './api/client'
import { Dashboard } from './components/Dashboard'
import heroImage from './assets/freud-lucas.png'

function App() {
  const [state, dispatch] = useReducer(authReducer, initialAuthState)

  useEffect(() => {
    dispatch({ type: 'MOUNT' })
  }, [])

  useEffect(() => {
    if (state.status !== 'checking') return

    const requestId = state.requestId

    fetchMe()
      .then((me) => {
        if (me) {
          dispatch({ type: 'ME_OK', requestId, userId: me.spotify_user_id })
        } else {
          dispatch({ type: 'ME_UNAUTHENTICATED', requestId })
        }
      })
      .catch(() => dispatch({ type: 'ME_NETWORK_ERROR', requestId }))
  }, [state.status, state.requestId])

  async function handleLogin() {
    dispatch({ type: 'LOGIN_CLICKED' })
    const authUrl = await fetchLoginUrl()
    window.location.href = authUrl
  }

  async function handleLogout() {
    dispatch({ type: 'LOGOUT_CLICKED' })
    try {
      await logout()
      dispatch({ type: 'LOGOUT_DONE' })
    } catch {
      dispatch({ type: 'LOGOUT_ERROR' })
    }
  }

  switch (state.status) {
    case 'checking':
      return <p>Lade …</p>

    case 'anonymous':
      return (
        <main>
          <img src={heroImage} alt="Sigmund Freud und Lucas nebeneinander in einem Musikstudio" className="hero-image" />
          <h1>Audio DNA</h1>
          <button onClick={handleLogin}>Login mit Spotify</button>
        </main>
      )

    case 'redirecting':
      return <p>Weiterleitung zu Spotify …</p>

    case 'authenticated':
      return <Dashboard userId={state.userId} onLogout={handleLogout} />

    case 'loggingOut':
      return <p>Wird ausgeloggt …</p>

    case 'error':
      return (
        <main>
          <p>{state.message}</p>
          <button onClick={() => dispatch({ type: 'RETRY' })}>Erneut versuchen</button>
        </main>
      )
  }
}

export default App
