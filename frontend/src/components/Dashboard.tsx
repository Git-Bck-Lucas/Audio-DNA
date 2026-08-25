import { useState } from 'react'
import { fetchAnalysis, RateLimitError, type AnalysisResult, type Mode } from '../api/client'
import { ModeToggle } from './ModeToggle'
import { ResultView } from './ResultView'
import { SourceList } from './SourceList'

type AnalysisFlowState =
  | { phase: 'idle' }
  | { phase: 'loading' }
  | { phase: 'success'; result: AnalysisResult }
  | { phase: 'error'; message: string }

type Props = {
  userId: string
  onLogout: () => void
}

export function Dashboard({ userId, onLogout }: Props) {
  const [flow, setFlow] = useState<AnalysisFlowState>({ phase: 'idle' })

  async function handleModeSelect(mode: Mode) {
    setFlow({ phase: 'loading' })
    try {
      const result = await fetchAnalysis(mode)
      setFlow({ phase: 'success', result })
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
          <ResultView personality={flow.result.result.personality} />
          <SourceList sources={flow.result.result.sources} />
        </>
      )}

      <p className="account-line">
        Eingeloggt als {userId} · <button onClick={onLogout}>Logout</button>
      </p>
    </main>
  )
}
