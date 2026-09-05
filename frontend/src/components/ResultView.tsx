import type { AnalysisResult, Mode, TraitScore } from '../api/client'
import {
  BIG_FIVE_HONESTY,
  BIG_FIVE_INTRO,
  TRAIT_META,
  TRAIT_ORDER,
  evidenceSentence,
  levelWord,
} from '../content/traits'
import { Fold } from './Fold'
import { SourceList } from './SourceList'
import './ResultView.css'

const MODE_LABEL: Record<Mode, string> = {
  science: 'Literaturbasierte Analyse',
  lucas: 'Lucas-Analyse',
}

type Props = {
  result: AnalysisResult['result']
  mode: Mode
  onRestart: () => void
}

/**
 * Gefuehrter Report in vier Abschnitten: erst erklaeren worum es geht, dann was in den
 * Daten steht, dann die Einschaetzung, dann die Belege. Die Erklaerung ist der Rahmen,
 * kein Zusatz -- ohne sie war die Ausgabe fuer Testnutzer ohne Vorwissen bedeutungslos.
 *
 * Die Abschnitte sind bewusst nicht durchnummeriert: hier wird nichts abgearbeitet,
 * die Nummern lasen sich nur wie ein Formular.
 */
export function ResultView({ result, mode, onRestart }: Props) {
  const { personality, sources, analysis_details, diversity } = result

  return (
    <article className="report">
      <header className="report__head appear">
        <p className="label">{MODE_LABEL[mode]}</p>
        <h1 className="report__title">Deine Audio DNA</h1>
        <p className="report__summary">{personality.summary}</p>
      </header>

      {/* Der einzige Abschnitt, den man beim zweiten Report nicht mehr liest. */}
      <Fold id="intro" label="Worum es geht" defaultOpen>
        <div className="col">
          <p className="lead report__p">{BIG_FIVE_INTRO}</p>
          <p className="lead report__p">{BIG_FIVE_HONESTY}</p>
        </div>
      </Fold>

      <section className="report__section appear">
        <p className="label report__section-label">Was in deinen Daten steht</p>

        <div className="col">
          <p className="lead report__intro-line">
            Grundlage sind deine {analysis_details.artists_analyzed} meistgehörten Artists der
            letzten sechs Monate. Daraus kommen die Genres, und daraus die Einschätzung.
          </p>
        </div>

        <div className="stats">
          <Stat value={diversity.total_genre_count} label="Genres" />
          <Stat value={diversity.genre_clusters} label="Stilwelten" />
          <Stat value={analysis_details.artists_analyzed} label="Artists" />
        </div>

        <div className="wide">
          <p className="small report__chips-label">Deine wichtigsten zehn</p>
          <ul className="chips report__chips">
            {analysis_details.top_artists.slice(0, 10).map((artist) => (
              <li className="chip" key={artist}>
                {artist}
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="report__section appear">
        <p className="label report__section-label">Die Einschätzung</p>

        <div className="col">
          <p className="small report__legend">
            Der Punkt zeigt, wo du auf der Skala liegst. Je unschärfer er ist, desto dünner ist die
            Forschungslage zu diesem Merkmal — die Lage ist dann eine Richtung, keine Messung.
          </p>
        </div>

        {TRAIT_ORDER.map((trait) => {
          const { score, confidence, reasoning } = personality[trait]
          const meta = TRAIT_META[trait]

          return (
            <section className="trait" key={trait}>
              <div className="trait__in">
                <div className="trait__head">
                  <h2 className="trait__name">{meta.name}</h2>
                  <span className="trait__score">{score.toFixed(2)}</span>
                </div>
                <p className="trait__what">{meta.what}</p>

                <Scale score={score} confidence={confidence} low={meta.low} high={meta.high} />

                <p className="trait__why">
                  <strong>{levelWord(score)}.</strong> {evidenceSentence(confidence)} {reasoning}
                </p>
              </div>
            </section>
          )
        })}
      </section>

      <SourceList sources={sources} mode={mode} />

      <p className="report__restart">
        <button className="btn btn--ghost" onClick={onRestart}>
          Andere Erklärung wählen
        </button>
      </p>
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

/**
 * Unsicherheit liegt als Unschaerfe auf dem Punkt, nicht als Farbe oder Transparenz.
 * Farbe waere ein zweiter Kanal ohne Legende, Transparenz haette auf dunklem Grund
 * bloss den Text weggefressen. Die Unschaerfe zeigt, was gemeint ist: der Wert ist
 * eine Gegend, keine Stelle.
 */
function Scale({
  score,
  confidence,
  low,
  high,
}: {
  score: number
  confidence: TraitScore['confidence']
  low: string
  high: string
}) {
  const percent = score * 100
  const bandWidth = confidence === 'low' ? 34 : confidence === 'medium' ? 18 : 0

  return (
    <div className="scale" data-confidence={confidence}>
      <div className="scale__track">
        <span className="scale__mid" />
        {bandWidth > 0 && (
          <span className="scale__band" style={{ left: `${percent}%`, width: `${bandWidth}%` }} />
        )}
        <span className="scale__dot" style={{ left: `${percent}%` }} />
      </div>
      <p className="scale__poles">
        <span>{low}</span>
        <span>{high}</span>
      </p>
    </div>
  )
}
