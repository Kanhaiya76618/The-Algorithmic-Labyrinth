import { useCallback, useEffect, useState } from 'react'
import Frame from '../components/Frame.jsx'
import { getMemoryReport, forget, PLAYER_NAME_KEY } from '../api/client.js'

function threatTier(level) {
  if (level >= 70) return 'danger'
  if (level >= 35) return 'warn'
  return 'ok'
}

export default function MemoryView({ playerName: playerNameProp, embedded = false }) {
  const [playerName, setPlayerName] = useState(
    playerNameProp || (typeof window !== 'undefined' ? window.localStorage.getItem(PLAYER_NAME_KEY) : '') || '',
  )
  const [nameDraft, setNameDraft] = useState('')
  const [report, setReport] = useState(null)
  const [status, setStatus] = useState('idle') // idle | loading | error | ready
  const [forgetting, setForgetting] = useState(false)

  useEffect(() => {
    if (playerNameProp) setPlayerName(playerNameProp)
  }, [playerNameProp])

  const load = useCallback((name) => {
    setStatus('loading')
    return getMemoryReport(name)
      .then((data) => {
        setReport(data)
        setStatus('ready')
      })
      .catch(() => setStatus('error'))
  }, [])

  useEffect(() => {
    if (playerName) load(playerName)
  }, [playerName, load])

  async function handleForget() {
    if (!playerName) return
    setForgetting(true)
    try {
      await forget(playerName, report?.difficulty_spike?.topic)
      await load(playerName)
    } finally {
      setForgetting(false)
    }
  }

  function handleNameSubmit(e) {
    e.preventDefault()
    const name = nameDraft.trim()
    if (!name) return
    window.localStorage.setItem(PLAYER_NAME_KEY, name)
    setPlayerName(name)
  }

  let body
  if (!playerName) {
    body = (
      <form className="boot-form" onSubmit={handleNameSubmit}>
        <input
          className="boot-input"
          placeholder="player name"
          value={nameDraft}
          onChange={(e) => setNameDraft(e.target.value)}
        />
        <button className="btn btn--primary" type="submit">
          View Report
        </button>
      </form>
    )
  } else if (status === 'loading') {
    body = <p className="memory-view__hint">Reading the boss's memory...</p>
  } else if (status === 'error') {
    body = <p className="memory-view__hint memory-view__hint--danger">Could not reach the memory service.</p>
  } else if (report) {
    body = (
      <>
        <div className="threat-gauge">
          <div className="threat-gauge__track">
            <div
              className={`threat-gauge__fill threat-gauge__fill--${threatTier(report.threat_level)}`}
              style={{ width: `${report.threat_level}%` }}
            />
          </div>
          <span className="threat-gauge__label">Threat level: {report.threat_level}%</span>
        </div>

        <p className="memory-view__summary">{report.executive_summary}</p>

        <div className="memory-view__stat">
          <span className="memory-view__stat-label">Difficulty spike</span>
          {report.difficulty_spike ? (
            <span className="status-pill status-pill--danger">
              <span className="status-dot" />
              {report.difficulty_spike.topic} +{report.difficulty_spike.delta}
            </span>
          ) : (
            <span className="status-pill status-pill--idle">none detected</span>
          )}
        </div>

        <button className="btn btn--danger" onClick={handleForget} disabled={forgetting}>
          {forgetting ? 'Brewing…' : 'Potion of Forgetting'}
        </button>
      </>
    )
  }

  const content = (
    <Frame label="Boss Memory Report" className="memory-view">
      {body}
    </Frame>
  )

  return embedded ? content : <div className="app-shell">{content}</div>
}
