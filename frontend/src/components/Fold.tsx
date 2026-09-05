import { useState, type ReactNode } from 'react'
import './Fold.css'

const STORAGE_PREFIX = 'audiodna.fold.'

/**
 * Der Zustand wird pro Browser gemerkt: Abschnitte, die beim ersten Report noetig sind,
 * soll man beim zweiten nicht wieder wegklicken muessen. localStorage kann in privaten
 * Fenstern oder bei blockierten Site-Daten werfen, deshalb ueberall abgesichert.
 */
function readStored(id: string, fallback: boolean): boolean {
  try {
    const stored = localStorage.getItem(STORAGE_PREFIX + id)
    return stored === null ? fallback : stored === 'open'
  } catch {
    return fallback
  }
}

function writeStored(id: string, open: boolean): void {
  try {
    localStorage.setItem(STORAGE_PREFIX + id, open ? 'open' : 'closed')
  } catch {
    // Kein Zustand gemerkt, mehr passiert nicht.
  }
}

type Props = {
  id: string
  label: string
  defaultOpen: boolean
  /** 'section' ist eine ganze Report-Sektion, 'inline' ein Block innerhalb einer. */
  variant?: 'section' | 'inline'
  children: ReactNode
}

export function Fold({ id, label, defaultOpen, variant = 'section', children }: Props) {
  const [open, setOpen] = useState(() => readStored(id, defaultOpen))

  function toggle() {
    const next = !open
    setOpen(next)
    writeStored(id, next)
  }

  return (
    <section className={`fold fold--${variant} ${open ? 'is-open' : ''} appear`}>
      <button type="button" className="fold__summary" aria-expanded={open} onClick={toggle}>
        <span className={variant === 'section' ? 'label' : 'fold__title'}>{label}</span>
        <span className="fold__hint">{open ? 'Einklappen' : 'Ausklappen'}</span>
      </button>

      {open && <div className="fold__body">{children}</div>}
    </section>
  )
}
