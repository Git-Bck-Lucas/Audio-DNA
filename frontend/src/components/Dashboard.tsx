import { useState } from 'react'
import { fetchAnalysis, RateLimitError, type AnalysisResult, type Mode } from '../api/client'
import { AnalysisProgress } from './AnalysisProgress'
import { ModeToggle } from './ModeToggle'
import { Notice } from './Notice'
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

      {flow.phase === 'loading' && <AnalysisProgress />}

      {flow.phase === 'error' && (
        <Notice text={flow.message}>
          <button className="btn btn--ghost" onClick={() => setFlow({ phase: 'idle' })}>
            Erneut versuchen
          </button>
        </Notice>
      )}

      {flow.phase === 'success' && <ResultView
          result={flow.result.result}
          mode={flow.mode}
          onRestart={() => setFlow({ phase: 'idle' })}
        />}

      <p className="account-line col">
        {displayName ? (
          <>
            Eingeloggt als <strong>{displayName}</strong>
          </>
        ) : (
          'Eingeloggt'
        )}
        {' · '}
        <button className="btn btn--text" onClick={onLogout}>
          Logout
        </button>
      </p>
    </main>
  )
}
