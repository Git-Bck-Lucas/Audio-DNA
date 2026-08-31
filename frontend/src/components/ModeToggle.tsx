import type { Mode } from '../api/client'
import freudLucas from '../assets/freud-lucas.png'
import './ModeToggle.css'

type Props = {
  onSelect: (mode: Mode) => void
}

export function ModeToggle({ onSelect }: Props) {
  return (
    <div className="mode-toggle">
      <img src={freudLucas} alt="Sigmund Freud und Lucas nebeneinander, beide mit Zigarre" />

      <button
        type="button"
        className="mode-toggle__half mode-toggle__half--left"
        onClick={() => onSelect('science')}
        aria-label="Wissenschaftlicher Modus: Analyse mit Fachvokabular und Literaturbezug"
      >
        <span>Wissenschaftlich</span>
      </button>

      <button
        type="button"
        className="mode-toggle__half mode-toggle__half--right"
        onClick={() => onSelect('lucas')}
        aria-label="Lockerer Modus: Analyse in Alltagssprache"
      >
        <span>Locker</span>
      </button>
    </div>
  )
}
