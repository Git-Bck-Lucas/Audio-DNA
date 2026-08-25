import type { Source } from '../api/client'
import './SourceList.css'

type Props = {
  sources: Source[]
}

export function SourceList({ sources }: Props) {
  if (sources.length === 0) return null

  return (
    <div className="source-list">
      <h2 className="source-list__heading">Quellen</h2>
      {sources.map((entry, index) => (
        <blockquote className="source-list__entry" key={index}>
          <p>{entry.text}</p>
          <cite>
            {entry.author}, {entry.source}
          </cite>
        </blockquote>
      ))}
    </div>
  )
}
