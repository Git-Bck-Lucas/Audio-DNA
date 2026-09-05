import { useEffect, useReducer } from 'react'
import { authReducer, initialAuthState } from './state/authMachine'
import { fetchLoginUrl, fetchMe, logout } from './api/client'
import { Dashboard } from './components/Dashboard'
import { Footer } from './components/Footer'
import { Landing } from './components/Landing'
import { Notice } from './components/Notice'

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
          dispatch({ type: 'ME_OK', requestId, displayName: me.display_name })
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

  function renderContent() {
    switch (state.status) {
      case 'checking':
        return <Notice text="Lade …" />

      case 'anonymous':
        return <Landing onLogin={handleLogin} />

      case 'redirecting':
        return <Notice text="Weiterleitung zu Spotify …" />

      case 'authenticated':
        return <Dashboard onLogout={handleLogout} displayName={state.displayName} />

      case 'loggingOut':
        return <Notice text="Wird ausgeloggt …" />

      case 'error':
        return (
          <Notice text={state.message}>
            <button className="btn btn--ghost" onClick={() => dispatch({ type: 'RETRY' })}>
              Erneut versuchen
            </button>
          </Notice>
        )
    }
  }

  return (
    <>
      {renderContent()}
      <Footer />
    </>
  )
}

export default App
