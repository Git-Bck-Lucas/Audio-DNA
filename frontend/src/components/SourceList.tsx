import type { Mode, Source } from '../api/client'
import { PAPERS } from '../content/papers'
import './SourceList.css'

const QUOTE_LENGTH = 240

type Props = {
  sources: Source[]
  mode: Mode
}

/**
 * Die Chunks kommen roh aus der Ingest-Pipeline: Markdown-Ueberschriften, Fettmarkierungen
 * und Zeilenumbrueche aus dem PDF-Text. Als Beleg zitiert wird nur der Anfang, geglaettet.
 */
function formatQuote(text: string): string {
  const clean = text
    .replace(/[#*_`]/g, '')
    .replace(/\s+/g, ' ')
    .trim()

  if (clean.length <= QUOTE_LENGTH) return clean

  const cut = clean.slice(0, QUOTE_LENGTH)
  const lastSpace = cut.lastIndexOf(' ')
  return `${cut.slice(0, lastSpace > 0 ? lastSpace : QUOTE_LENGTH)} …`
}

type Grouped = {
  key: string
  author: string
  quotes: string[]
}

/**
 * Mehrere Belegstellen stammen haeufig aus derselben Arbeit. Ohne Gruppierung stuende
 * derselbe Titel mehrfach untereinander.
 */
function groupByPaper(sources: Source[]): Grouped[] {
  const groups = new Map<string, Grouped>()

  for (const source of sources) {
    const existing = groups.get(source.source)
    if (existing) {
      existing.quotes.push(source.text)
    } else {
      groups.set(source.source, { key: source.source, author: source.author, quotes: [source.text] })
    }
  }

  return [...groups.values()]
}

/**
 * Im Literatur-Modus offen, sonst eingeklappt: fuer Testnutzer waren die woertlichen
 * Fachtext-Ausschnitte Laerm, fuer den Modus mit Belegen sind sie der Punkt.
 */
export function SourceList({ sources, mode }: Props) {
  if (sources.length === 0) return null

  const papers = groupByPaper(sources)

  return (
    <section className="report__step">
      <p className="report__step-label">Schritt 4 · Woher das kommt</p>
      <p className="report__lead">
        Die Einschätzung stützt sich auf {sources.length} Passagen aus {papers.length}{' '}
        musikpsychologischen Arbeiten, die zu deinem Profil gesucht wurden.
      </p>

      <details className="sources" open={mode === 'science'}>
        <summary className="sources__summary">Die zitierten Stellen im Wortlaut</summary>

        <div className="sources__list">
          {papers.map((paper) => {
            const meta = PAPERS[paper.key]

            return (
              <article className="source" key={paper.key}>
                {meta ? (
                  <>
                    <a
                      className="source__title"
                      href={`https://doi.org/${meta.doi}`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {meta.title}
                    </a>
                    <p className="source__meta">
                      {paper.author} · {meta.publication} · {paper.quotes.length}{' '}
                      {paper.quotes.length === 1 ? 'Stelle' : 'Stellen'}
                    </p>
                  </>
                ) : (
                  <p className="source__title">{paper.author}</p>
                )}

                {paper.quotes.slice(0, 2).map((quote, index) => (
                  <blockquote className="source__quote" key={index}>
                    „{formatQuote(quote)}“
                  </blockquote>
                ))}
              </article>
            )
          })}
        </div>
      </details>
    </section>
  )
}
