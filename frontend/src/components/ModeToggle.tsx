import { useState } from 'react'
import type { Mode } from '../api/client'
import freudLucas from '../assets/freud-lucas.png'
import './ModeToggle.css'

type ModeInfo = {
  name: string
  /** Steht fest sichtbar unter dem Namen. Vorher lag diese Erklaerung nur im aria-label,
   *  war also unsichtbar -- Testnutzer wussten nicht, wofuer sie sich entscheiden. */
  subtitle: string
  /** Das Lange, hinter dem Infobutton. */
  detail: string
}

const MODES: Record<Mode, ModeInfo> = {
  science: {
    name: 'Literaturbasierte Analyse',
    subtitle: 'Mit Belegen aus der Musikpsychologie, sachlich formuliert',
    detail:
      'Jede Einschätzung wird gegen Fachliteratur geprüft und nennt die Arbeit, auf der sie beruht. ' +
      'Nüchterner Ton, dafür nachvollziehbar. Wo die Forschung nichts hergibt, bleibt der Wert neutral.',
  },
  lucas: {
    name: 'Lucas-Analyse',
    subtitle: 'In meinen Worten, ohne Fachbegriffe',
    detail:
      'Ich bin Lucas und habe diese App gebaut. Hier erzähle ich dir, was mir an deinen Daten auffällt, ' +
      'so wie ich es einem Freund erzählen würde. Mit mehr Bauchgefühl, klar als Vermutung markiert.',
  },
}

type Props = {
  onSelect: (mode: Mode) => void
}

export function ModeToggle({ onSelect }: Props) {
  const [openDetail, setOpenDetail] = useState<Mode | null>(null)

  return (
    <div className="mode-choice">
      <img
        className="mode-choice__image"
        src={freudLucas}
        alt="Sigmund Freud und Lucas nebeneinander, beide mit Zigarre"
      />

      <h2 className="mode-choice__heading">Wie soll ich dir das erklären?</h2>
      <p className="mode-choice__note">Gleiche Analyse, gleiche Daten. Nur die Erklärung ist anders.</p>

      <div className="mode-choice__list">
        {(Object.keys(MODES) as Mode[]).map((mode) => (
          <div className="mode-card" key={mode}>
            <div className="mode-card__row">
              <button type="button" className="mode-card__main" onClick={() => onSelect(mode)}>
                <span className="mode-card__name">{MODES[mode].name}</span>
                <span className="mode-card__subtitle">{MODES[mode].subtitle}</span>
              </button>

              <button
                type="button"
                className="mode-card__info"
                aria-expanded={openDetail === mode}
                aria-label={`Mehr zur ${MODES[mode].name}`}
                onClick={() => setOpenDetail(openDetail === mode ? null : mode)}
              >
                i
              </button>
            </div>

            {openDetail === mode && <p className="mode-card__detail">{MODES[mode].detail}</p>}
          </div>
        ))}
      </div>
    </div>
  )
}
