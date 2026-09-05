import { useState } from 'react'
import { fetchAnalysis, RateLimitError, type AnalysisResult, type Mode } from '../api/client'
import { ModeToggle } from './ModeToggle'
import { ResultView } from './ResultView'

type AnalysisFlowState =
  | { phase: 'idle' }
  | { phase: 'loading' }
  | { phase: 'success'; result: AnalysisResult; mode: Mode }
  | { phase: 'error'; message: string }

type Props = {
  onLogout: () => void
  displayName: string | null
}

export function Dashboard({ onLogout, displayName }: Props) {
  const [flow, setFlow] = useState<AnalysisFlowState>({ phase: 'idle' })

  async function handleModeSelect(mode: Mode) {
    setFlow({ phase: 'loading' })
    try {
      const result = await fetchAnalysis(mode)
      setFlow({ phase: 'success', result, mode })
    } catch (err) {
      if (err instanceof RateLimitError) {
        const minutes = err.retryAfterSeconds ? Math.ceil(err.retryAfterSeconds / 60) : null
        setFlow({
          phase: 'error',
          message: minutes
            ? `Rate Limit erreicht. Versuch's in ${minutes} Minuten wieder.`
            : "Rate Limit erreicht. Versuch's später wieder.",
        })
      } else {
        setFlow({ phase: 'error', message: 'Analyse fehlgeschlagen. Versuch es später erneut.' })
      }
    }
  }

  return (
    <main>
      {flow.phase === 'idle' && <ModeToggle onSelect={handleModeSelect} />}

      {flow.phase === 'loading' && <p>Analysiere deine Spotify-Daten …</p>}

      {flow.phase === 'error' && (
        <div>
          <p>{flow.message}</p>
          <button onClick={() => setFlow({ phase: 'idle' })}>Erneut versuchen</button>
        </div>
      )}

      {flow.phase === 'success' && (
        <>
          <ResultView result={flow.result.result} mode={flow.mode} />
          <button onClick={() => setFlow({ phase: 'idle' })}>Zurück</button>
        </>
      )}

      <p className="account-line">
        {displayName ? <>Eingeloggt als <strong>{displayName}</strong></> : 'Eingeloggt'}
        {' · '}
        <button onClick={onLogout}>Logout</button>
      </p>
    </main>
  )
}
