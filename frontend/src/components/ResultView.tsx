import type { AnalysisResult, Mode } from '../api/client'
import {
  BIG_FIVE_HONESTY,
  BIG_FIVE_INTRO,
  TRAIT_META,
  TRAIT_ORDER,
  evidenceSentence,
  levelWord,
} from '../content/traits'
import { SourceList } from './SourceList'
import './ResultView.css'

const MODE_LABEL: Record<Mode, string> = {
  science: 'Literaturbasierte Analyse',
  lucas: 'Lucas-Analyse',
}

type Props = {
  result: AnalysisResult['result']
  mode: Mode
}

/**
 * Gefuehrter Report in vier Schritten: erst erklaeren worum es geht, dann was in den
 * Daten steht, dann die Einschaetzung, dann die Belege. Die Erklaerung ist der Rahmen,
 * kein Zusatz -- ohne sie war die Ausgabe fuer Testnutzer ohne Vorwissen bedeutungslos.
 */
export function ResultView({ result, mode }: Props) {
  const { personality, sources, analysis_details, diversity } = result

  return (
    <article className="report">
      <section className="report__step">
        <p className="report__step-label">Schritt 1 · Worum es geht</p>
        <h1 className="report__title">Die Big Five</h1>
        <p className="report__lead">{BIG_FIVE_INTRO}</p>
        <p className="report__lead">{BIG_FIVE_HONESTY}</p>
      </section>

      <section className="report__step">
        <p className="report__step-label">Schritt 2 · Was in deinen Daten steht</p>
        <div className="panel">
          <div className="stats">
            <Stat value={diversity.total_genre_count} label="Genres" />
            <Stat value={diversity.genre_clusters} label="Stilwelten" />
            <Stat value={analysis_details.artists_analyzed} label="Artists" />
          </div>
          <ul className="chips">
            {analysis_details.top_artists.slice(0, 10).map((artist) => (
              <li className="chip" key={artist}>
                {artist}
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="report__step">
        <p className="report__step-label">Schritt 3 · Die Einschätzung</p>
        <p className="report__summary">{personality.summary}</p>
        <p className="report__mode-note">{MODE_LABEL[mode]}</p>

        <div className="traits">
          {TRAIT_ORDER.map((trait) => {
            const { score, confidence, reasoning } = personality[trait]
            const meta = TRAIT_META[trait]
            const weak = confidence === 'low'

            return (
              <section className={weak ? 'trait trait--weak' : 'trait'} key={trait}>
                <h2 className="trait__name">
                  {meta.name} <span className="trait__score">{score.toFixed(2)}</span>
                </h2>
                <p className="trait__what">{meta.what}</p>

                <div className="scale">
                  <div className="scale__track">
                    <div className="scale__fill" style={{ width: `${score * 100}%` }} />
                    <div className="scale__marker" style={{ left: `${score * 100}%` }} />
                  </div>
                  <p className="scale__poles">
                    <span>{meta.low}</span>
                    <span>{meta.high}</span>
                  </p>
                </div>

                <p className="trait__verdict">
                  <strong>{levelWord(score)}.</strong>{' '}
                  <span className="trait__evidence">{evidenceSentence(confidence)}</span>
                </p>
                <p className="trait__reasoning">{reasoning}</p>
              </section>
            )
          })}
        </div>
      </section>

      <SourceList sources={sources} mode={mode} />
    </article>
  )
}

function Stat({ value, label }: { value: number; label: string }) {
  return (
    <div className="stat">
      <span className="stat__value">{value}</span>
      <span className="stat__label">{label}</span>
    </div>
  )
}
