import { useEffect, useReducer } from 'react'
import { authReducer, initialAuthState } from './state/authMachine'
import { fetchLoginUrl, fetchMe, logout } from './api/client'
import { Dashboard } from './components/Dashboard'
import { Footer } from './components/Footer'
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
          dispatch({ type: 'ME_OK', requestId })
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
        return <p>Lade …</p>

      case 'anonymous':
        return (
          <main>
            <img src={heroImage} alt="Sigmund Freud und Lucas nebeneinander in einem Musikstudio" className="hero-image" />
            <h1>Audio DNA</h1>
            <button onClick={handleLogin}>Login mit Spotify</button>
            <p className="access-note">
              Die App läuft aktuell im Spotify Development Mode, nur eingetragene Test-Accounts können sich
              einloggen. Willst du deine eigene Analyse sehen? Schick mir kurz deinen Namen und deine
              Spotify-E-Mail an <a href="mailto:kontakt@lucas-beck.de">kontakt@lucas-beck.de</a>, dann trage ich
              dich ein.
            </p>
            <h2>Demo</h2>
            <video className="demo-video" controls preload="metadata">
              <source
                src="https://github.com/Git-Bck-Lucas/Audio-DNA/releases/download/v1.0.0/audio_dna_demo.mp4"
                type="video/mp4"
              />
              Dein Browser kann das Video leider nicht abspielen,{' '}
              <a href="https://github.com/Git-Bck-Lucas/Audio-DNA/releases/download/v1.0.0/audio_dna_demo.mp4">
                direkt herunterladen
              </a>
              .
            </video>
          </main>
        )

      case 'redirecting':
        return <p>Weiterleitung zu Spotify …</p>

      case 'authenticated':
        return <Dashboard onLogout={handleLogout} />

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

  return (
    <>
      {renderContent()}
      <Footer />
    </>
  )
}

export default App
