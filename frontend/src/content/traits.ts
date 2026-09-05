import type { PersonalityScores, TraitScore } from '../api/client'

export type TraitKey = Exclude<keyof PersonalityScores, 'summary'>

export const TRAIT_ORDER: TraitKey[] = [
  'openness',
  'conscientiousness',
  'extraversion',
  'agreeableness',
  'neuroticism',
]

type TraitMeta = {
  /** Deutscher Name des Merkmals. */
  name: string
  /** Ein Halbsatz, der erklaert was das Merkmal ueberhaupt meint. */
  what: string
  /** Beschriftung der Skalenenden in Alltagssprache, statt einer nackten Zahl. */
  low: string
  high: string
}

export const TRAIT_META: Record<TraitKey, TraitMeta> = {
  openness: {
    name: 'Offenheit',
    what: 'wie stark dich Neues, Ungewohntes und Komplexes anzieht',
    low: 'bleibt beim Vertrauten',
    high: 'sucht ständig Neues',
  },
  conscientiousness: {
    name: 'Gewissenhaftigkeit',
    what: 'wie sehr du planst, ordnest und Dinge zu Ende bringst',
    low: 'spontan, aus dem Bauch',
    high: 'planvoll, strukturiert',
  },
  extraversion: {
    name: 'Extraversion',
    what: 'wie sehr du Energie aus Menschen und Trubel ziehst',
    low: 'still, gern für sich',
    high: 'gesellig, mitten drin',
  },
  agreeableness: {
    name: 'Verträglichkeit',
    what: 'wie sehr du auf andere zugehst statt zu widersprechen',
    low: 'direkt, streitbar',
    high: 'warm, entgegenkommend',
  },
  neuroticism: {
    name: 'Neurotizismus',
    what: 'wie leicht dich Stress und trübe Stimmungen mitnehmen',
    low: 'ruht in sich',
    high: 'schnell aufgewühlt',
  },
}

/** Der Score als Wort. Die Zahl allein sagt niemandem etwas, der sie nicht einordnen kann. */
export function levelWord(score: number): string {
  if (score < 0.35) return 'gering ausgeprägt'
  if (score < 0.45) return 'eher gering'
  if (score <= 0.55) return 'genau in der Mitte'
  if (score < 0.65) return 'leicht erhöht'
  if (score < 0.8) return 'ausgeprägt'
  return 'stark ausgeprägt'
}

/**
 * Confidence als Aussage statt als Etikett. "niedrige Konfidenz" ist eine Bewertung,
 * die niemand einordnen kann; der Satz sagt, woran es liegt.
 */
export function evidenceSentence(confidence: TraitScore['confidence']): string {
  switch (confidence) {
    case 'high':
      return 'Dafür gibt die Forschung viel her.'
    case 'medium':
      return 'Die Forschung stützt das teilweise.'
    case 'low':
      return 'Dazu gibt die Forschung wenig her.'
  }
}

export const BIG_FIVE_INTRO =
  'Die Big Five sind das gängigste Persönlichkeitsmodell der Psychologie. Es beschreibt Menschen nicht in ' +
  'Typen, sondern über fünf Eigenschaften, bei denen jeder irgendwo zwischen zwei Polen liegt. Was du hier ' +
  'siehst, ist kein Test: es ist eine Schätzung, die allein aus deinen Spotify-Daten abgeleitet wurde.'

export const BIG_FIVE_HONESTY =
  'Wie belastbar das ist, hängt stark vom Merkmal ab. Für Offenheit gibt die Forschung viel her, für drei der ' +
  'fünf Merkmale fast nichts. Wo wenig da ist, steht das auch so da, statt eine Zahl zu erfinden.'
