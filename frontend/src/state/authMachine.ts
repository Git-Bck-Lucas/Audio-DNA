export type AuthState =
  | { status: 'checking'; requestId: number }
  | { status: 'anonymous'; requestId: number }
  | { status: 'redirecting'; requestId: number }
  | { status: 'authenticated'; requestId: number; displayName: string | null }
  | { status: 'loggingOut'; requestId: number }
  | { status: 'error'; requestId: number; message: string }

export type AuthEvent =
  | { type: 'MOUNT' }
  | { type: 'REMOUNT' }
  | { type: 'ME_OK'; requestId: number; displayName: string | null }
  | { type: 'ME_UNAUTHENTICATED'; requestId: number }
  | { type: 'ME_NETWORK_ERROR'; requestId: number }
  | { type: 'LOGIN_CLICKED' }
  | { type: 'LOGOUT_CLICKED' }
  | { type: 'LOGOUT_DONE' }
  | { type: 'LOGOUT_ERROR' }
  | { type: 'RETRY' }

export const initialAuthState: AuthState = { status: 'checking', requestId: 1 }

export function authReducer(state: AuthState, event: AuthEvent): AuthState {
  switch (event.type) {
    case 'MOUNT':
    case 'REMOUNT':
      return { status: 'checking', requestId: state.requestId + 1 }

    // requestId-Check schuetzt vor Race Conditions: eine verspaetete Antwort auf
    // eine veraltete Anfrage (z.B. durch StrictMode-Doppel-Mount oder den
    // Spotify-Redirect-Kreislauf) darf den Zustand einer neueren Anfrage nicht
    // ueberschreiben. Validiert im Prototyp unter prototypes/auth-state-machine.prototype.html
    case 'ME_OK':
      if (state.status !== 'checking' || event.requestId !== state.requestId) return state
      return { status: 'authenticated', requestId: state.requestId, displayName: event.displayName }

    case 'ME_UNAUTHENTICATED':
      if (state.status !== 'checking' || event.requestId !== state.requestId) return state
      return { status: 'anonymous', requestId: state.requestId }

    case 'ME_NETWORK_ERROR':
      if (state.status !== 'checking' || event.requestId !== state.requestId) return state
      return { status: 'error', requestId: state.requestId, message: 'Netzwerkfehler bei /spotify/me' }

    case 'LOGIN_CLICKED':
      if (state.status !== 'anonymous') return state
      return { status: 'redirecting', requestId: state.requestId }

    case 'LOGOUT_CLICKED':
      if (state.status !== 'authenticated') return state
      return { status: 'loggingOut', requestId: state.requestId }

    // /spotify/logout ist im Backend ein RedirectResponse, kein JSON-Endpoint.
    // Der Browser navigiert bei einem fetch()-Aufruf nicht automatisch mit,
    // deshalb dispatched die Seite LOGOUT_DONE explizit nach Abschluss des fetch.
    case 'LOGOUT_DONE':
      if (state.status !== 'loggingOut') return state
      return { status: 'anonymous', requestId: state.requestId }

    case 'LOGOUT_ERROR':
      if (state.status !== 'loggingOut') return state
      return { status: 'error', requestId: state.requestId, message: 'Netzwerkfehler bei /spotify/logout' }

    case 'RETRY':
      if (state.status !== 'error') return state
      return { status: 'checking', requestId: state.requestId + 1 }

    default:
      return state
  }
}
