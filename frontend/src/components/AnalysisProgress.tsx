import { useEffect, useState } from 'react'
import './AnalysisProgress.css'

const STEPS = [
  'Hole deine meistgehörten Artists',
  'Ordne sie Genres und Stilwelten zu',
  'Suche passende Stellen in der Fachliteratur',
  'Schreibe deine Auswertung',
]

const STEP_MS = 5000

/**
 * Der Analyse-Call ist synchron und meldet keinen Fortschritt, die Stufen laufen also
 * rein zeitgesteuert. Deshalb bewusst keine Prozentzahl: die waere gelogen. Die letzte
 * Stufe bleibt stehen, bis die Antwort da ist -- lieber zu lange auf "Schreibe deine
 * Auswertung" als eine Anzeige, die vor dem Ergebnis fertig ist.
 */
export function AnalysisProgress() {
  const [active, setActive] = useState(0)

  useEffect(() => {
    if (active >= STEPS.length - 1) return

    const timer = setTimeout(() => setActive((step) => step + 1), STEP_MS)
    return () => clearTimeout(timer)
  }, [active])

  return (
    <div className="load">
      <div className="load__in appear">
        <p className="label">Einen Moment</p>
        <h2 className="load__title">Ich lese deine Musik</h2>

        <ol className="load__steps">
          {STEPS.map((step, index) => (
            <li key={step} data-state={index < active ? 'done' : index === active ? 'active' : 'todo'}>
              <span className="load__dot" />
              {step}
            </li>
          ))}
        </ol>

        <p className="small load__note">
          Dauert etwa 20 Sekunden. Die Schritte zeigen, was gerade grob passiert.
        </p>
      </div>
    </div>
  )
}
