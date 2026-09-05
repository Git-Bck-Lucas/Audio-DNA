import { useState } from 'react'
import thumbnail from '../assets/hero-band.webp'
import './DemoVideo.css'

const VIDEO_ID = 'L6XVxHRaapA'

/**
 * Click-to-load statt eines direkt eingebetteten iframes: der YouTube-Player laedt
 * erst auf Klick. Spart beim ersten Seitenaufruf den Kontakt zu YouTube und laesst
 * die Flaeche gestaltet aussehen statt eingebettet.
 */
export function DemoVideo() {
  const [playing, setPlaying] = useState(false)

  if (playing) {
    return (
      <iframe
        className="video video--playing"
        src={`https://www.youtube-nocookie.com/embed/${VIDEO_ID}?autoplay=1`}
        title="Audio DNA Demo"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
      />
    )
  }

  return (
    <button type="button" className="video" onClick={() => setPlaying(true)}>
      <img src={thumbnail} alt="" />
      <span className="video__play">
        <span className="video__play-icon">▶</span>
      </span>
      <span className="video__cap">Demo ansehen · 2 Min</span>
    </button>
  )
}
