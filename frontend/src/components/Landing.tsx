import heroLarge from '../assets/hero.webp'
import heroSmall from '../assets/hero-750.webp'
import { DemoVideo } from './DemoVideo'
import './Landing.css'

const STEPS = [
  { n: '01', text: 'Mit Spotify einloggen' },
  { n: '02', text: 'Erklärstil wählen' },
  { n: '03', text: 'Report lesen, mit Quellen' },
]

type Props = {
  onLogin: () => void
}

/**
 * Der Hero fuellt die linke Seitenhaelfte ueber die volle Viewport-Hoehe und stoesst
 * an drei Seitenkanten an. Das hat zwei Gruende: ein Bild mit Rand ringsum bleibt eine
 * eingefuegte Kachel, und das Foto ist nur 1086px breit -- ein Full-bleed ueber die
 * ganze Seite muesste es hochskalieren, wodurch das eingebrannte Zitat schmiert. Im
 * hochformatigen Container wird es stattdessen verkleinert und bleibt scharf.
 */
export function Landing({ onLogin }: Props) {
  return (
    <>
      <div className="wordmark">Audio DNA</div>

      <div className="hero">
        <figure className="hero__fig">
          <img
            src={heroLarge}
            srcSet={`${heroSmall} 750w, ${heroLarge} 1086w`}
            /* Desktop: linke Seitenhaelfte (46vw). Handy: volle Breite. */
            sizes="(max-width: 900px) 100vw, 46vw"
            alt="Sigmund Freud und Lucas nebeneinander in einem Musikstudio"
          />
        </figure>

        <div className="hero__copy appear">
          <p className="label">Persönlichkeitsanalyse aus Spotify-Daten</p>
          <h1>Was deine Musik über dich verrät</h1>
          <p>
            Audio DNA liest deine Spotify-Historie und schätzt daraus deine
            Big-Five-Persönlichkeit — jede Aussage belegt mit Forschung aus der
            Musikpsychologie.
          </p>
          <button className="btn btn--primary" onClick={onLogin}>
            Login mit Spotify
          </button>
        </div>
      </div>

      <div className="steps-head wide">
        <p className="label">So läuft es ab</p>
      </div>
      <div className="steps">
        {STEPS.map((step) => (
          <div className="step" key={step.n}>
            <span className="step__n">{step.n}</span>
            <div className="step__t">{step.text}</div>
          </div>
        ))}
      </div>

      <div className="demo">
        <p className="label demo__label">Demo</p>
        <DemoVideo />
        <p className="small demo__note">
          Die App läuft im Spotify Development Mode, nur eingetragene Test-Accounts können sich
          einloggen. Willst du deine eigene Analyse sehen? Schick mir kurz deinen Namen und deine
          Spotify-E-Mail an <a href="mailto:kontakt@lucas-beck.de">kontakt@lucas-beck.de</a>, dann
          trage ich dich ein.
        </p>
      </div>
    </>
  )
}
