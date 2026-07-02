import { useEffect, useRef, useState } from 'react'
import Frame from './Frame.jsx'

export default function MemoryGraph({ topics = [], playerName = 'You' }) {
  const prevWeights = useRef({})
  const [reinforced, setReinforced] = useState(() => new Set())

  useEffect(() => {
    const grown = new Set()
    topics.forEach((t) => {
      const prev = prevWeights.current[t.id]
      if (t.reinforced_recently || (prev !== undefined && t.weight > prev)) grown.add(t.id)
      prevWeights.current[t.id] = t.weight
    })
    if (grown.size === 0) return
    setReinforced(grown)
    const timer = setTimeout(() => setReinforced(new Set()), 1400)
    return () => clearTimeout(timer)
  }, [topics])

  const height = Math.max(160, topics.length * 56)
  const centerY = height / 2
  const playerX = 30
  const topicX = 230
  const step = topics.length > 0 ? (height - 40) / topics.length : 0

  return (
    <Frame label="Memory Replay" className="memory-graph">
      {topics.length === 0 ? (
        <p className="memory-graph__empty">No memory recorded yet. Clear a floor to begin.</p>
      ) : (
        <svg
          className="memory-graph__svg"
          viewBox={`0 0 260 ${height}`}
          preserveAspectRatio="xMidYMid meet"
          role="img"
          aria-label="Player memory graph"
        >
          {topics.map((t, i) => {
            const y = step * i + step / 2 + 8
            const isReinforced = reinforced.has(t.id)
            return (
              <line
                key={`edge-${t.id}`}
                className={`memory-graph__edge${isReinforced ? ' memory-graph__edge--reinforced' : ''}`}
                x1={playerX}
                y1={centerY}
                x2={topicX}
                y2={y}
                strokeWidth={1 + t.weight * 5}
                strokeOpacity={0.3 + t.weight * 0.6}
              />
            )
          })}

          <circle className="memory-graph__player" cx={playerX} cy={centerY} r={12} />
          <text className="memory-graph__player-label" x={playerX} y={centerY + 26}>
            {playerName}
          </text>

          {topics.map((t, i) => {
            const y = step * i + step / 2 + 8
            const isReinforced = reinforced.has(t.id)
            return (
              <g key={`node-${t.id}`} className={`memory-graph__topic${isReinforced ? ' memory-graph__topic--reinforced' : ''}`}>
                <circle cx={topicX} cy={y} r={5 + t.weight * 5} />
                <text x={topicX + 14} y={y + 4}>
                  {t.name} · {Math.round(t.weight * 100)}%
                </text>
              </g>
            )
          })}
        </svg>
      )}
    </Frame>
  )
}
