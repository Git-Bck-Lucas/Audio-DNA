import type { PersonalityScores, TraitScore } from '../api/client'
import './ResultView.css'

const TRAIT_LABELS: Record<keyof PersonalityScores, string> = {
  openness: 'Offenheit',
  conscientiousness: 'Gewissenhaftigkeit',
  extraversion: 'Extraversion',
  agreeableness: 'Verträglichkeit',
  neuroticism: 'Neurotizismus',
}

const CONFIDENCE_LABELS: Record<TraitScore['confidence'], string> = {
  high: 'hohe Konfidenz',
  medium: 'mittlere Konfidenz',
  low: 'niedrige Konfidenz',
}

type Props = {
  personality: PersonalityScores
}

export function ResultView({ personality }: Props) {
  const traits = Object.keys(TRAIT_LABELS) as Array<keyof PersonalityScores>

  return (
    <div className="result-view">
      {traits.map((trait) => {
        const { score, confidence, reasoning } = personality[trait]
        return (
          <div className="trait" key={trait}>
            <div className="trait__header">
              <span className="trait__label">
                {TRAIT_LABELS[trait]} <span className="trait__score">{score.toFixed(2)}</span>
              </span>
              <span className="trait__confidence">{CONFIDENCE_LABELS[confidence]}</span>
            </div>
            <div className="trait__bar">
              <div className="trait__bar-fill" style={{ width: `${score * 100}%` }} />
            </div>
            <p className="trait__reasoning">{reasoning}</p>
          </div>
        )
      })}
    </div>
  )
}
