import type { ReactNode } from 'react'
import './Notice.css'

type Props = {
  text: string
  children?: ReactNode
}

/**
 * Kurzlebige Zwischenzustaende (pruefen, weiterleiten, ausloggen, Fehler). Vorher
 * war das ein nackter <p>-Tag oben links auf der Seite.
 */
export function Notice({ text, children }: Props) {
  return (
    <main className="notice">
      <div className="notice__in appear">
        <p className="notice__text">{text}</p>
        {children}
      </div>
    </main>
  )
}
