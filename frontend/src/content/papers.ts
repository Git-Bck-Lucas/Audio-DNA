/**
 * Titel, Fundstelle und DOI der Arbeiten im RAG-Korpus. Ohne das wirken die zitierten
 * Passagen zusammenhangslos: man liest ein englisches Textfragment ohne zu wissen, woher
 * es stammt oder wie man es nachschlagen wuerde.
 *
 * Alle Angaben stammen von Seite 1 der jeweiligen Arbeit in `backend/rag/documents`.
 *
 * Bewusst statisch im Frontend: der Korpus besteht aus genau diesen sechs Dokumenten.
 * Sobald er waechst, gehoert das als Spalte an die Chunks und wird beim Ingest befuellt.
 * Der Schluessel ist das `source`-Feld, das das Backend mitliefert.
 */
export type Paper = {
  title: string
  publication: string
  doi: string
}

export const PAPERS: Record<string, Paper> = {
  Schaefer_Mehlhorn_2017: {
    title: 'Can Personality Traits Predict Musical Style Preferences? A Meta-Analysis',
    publication: 'Personality and Individual Differences, 2017',
    doi: '10.1016/j.paid.2017.04.061',
  },
  Sust_2023: {
    title:
      'Personality Computing With Naturalistic Music Listening Behavior: Comparing Audio and Lyrics Preferences',
    publication: 'Collabra: Psychology, 2023',
    doi: '10.1525/collabra.75214',
  },
  Anderson_2021: {
    title: '“Just the Way You Are”: Linking Music Listening on Spotify and Personality',
    publication: 'Social Psychological and Personality Science, 2021',
    doi: '10.1177/1948550620923228',
  },
  Langmeyer_2012: {
    title:
      'What Do Music Preferences Reveal About Personality? A Cross-Cultural Replication Using Self-Ratings and Ratings of Music Samples',
    publication: 'Journal of Individual Differences, 2012',
    doi: '10.1027/1614-0001/a000082',
  },
  Rentfrow_Goldberg_Levitin_2011: {
    title: 'The Structure of Musical Preferences: A Five-Factor Model',
    publication: 'Journal of Personality and Social Psychology, 2011',
    doi: '10.1037/a0022406',
  },
  Rentfrow_Gosling_2003: {
    title:
      'The Do Re Mi’s of Everyday Life: The Structure and Personality Correlates of Music Preferences',
    publication: 'Journal of Personality and Social Psychology, 2003',
    doi: '10.1037/0022-3514.84.6.1236',
  },
}
