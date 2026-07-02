import { useCallback, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import FloorMap from '../components/FloorMap.jsx'
import MemoryGraph from '../components/MemoryGraph.jsx'
import QuestionModal from '../components/QuestionModal.jsx'
import MemoryView from './MemoryView.jsx'
import { startGame, nextChallenge, submitAnswer, getMemoryReport, PLAYER_NAME_KEY, RUN_ID_KEY } from '../api/client.js'

export default function DungeonPage() {
  const navigate = useNavigate()
  const [phase, setPhase] = useState('boot') // boot | descending | active
  const [nameDraft, setNameDraft] = useState('')
  const [playerName, setPlayerName] = useState('')
  const [run, setRun] = useState(null)
  const [challenge, setChallenge] = useState(null)
  const [result, setResult] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [topics, setTopics] = useState([])
  const [errorMessage, setErrorMessage] = useState('')

  const refreshMemory = useCallback((name) => {
    getMemoryReport(name)
      .then((report) => setTopics(report.topics ?? []))
      .catch(() => {})
  }, [])

  async function handleDescend(e) {
    e.preventDefault()
    const name = nameDraft.trim()
    if (!name) return
    setPhase('descending')
    setErrorMessage('')
    try {
      const runState = await startGame(name)
      window.localStorage.setItem(PLAYER_NAME_KEY, name)
      window.localStorage.setItem(RUN_ID_KEY, runState.run_id)
      setPlayerName(name)
      setRun(runState)
      refreshMemory(name)
      const firstChallenge = await nextChallenge(runState.run_id)
      setChallenge(firstChallenge)
      setPhase('active')
    } catch (err) {
      setErrorMessage(err.message || 'Failed to start the run.')
      setPhase('boot')
    }
  }

  async function handleAnswer(answer) {
    if (!run || !challenge) return
    setSubmitting(true)
    try {
      const outcome = await submitAnswer(run.run_id, challenge.id, answer)
      setResult(outcome)
      refreshMemory(playerName)
      setRun((prev) =>
        prev && {
          ...prev,
          current_floor_index: outcome.next_floor_index ?? prev.current_floor_index,
          floors: prev.floors.map((floor) => {
            if (floor.index === challenge.floor_index && outcome.floor_cleared) return { ...floor, status: 'cleared' }
            if (floor.index === outcome.next_floor_index) return { ...floor, status: 'current' }
            return floor
          }),
        },
      )
    } catch (err) {
      setResult({ correct: false, message: err.message || 'Something went wrong.' })
    } finally {
      setSubmitting(false)
    }
  }

  async function handleContinue() {
    const outcome = result
    setResult(null)
    setChallenge(null)
    if (!run) return
    if (outcome?.boss_triggered) {
      navigate('/boss', { state: { runId: run.run_id, playerName, boss: run.boss } })
      return
    }
    if (outcome?.run_complete) {
      setPhase('boot')
      return
    }
    try {
      const next = await nextChallenge(run.run_id)
      setChallenge(next)
    } catch (err) {
      setErrorMessage(err.message || 'Failed to load the next challenge.')
    }
  }

  if (phase === 'boot' || phase === 'descending') {
    return (
      <div className="app-shell">
        <div className="boot-screen">
          <div>
            <h1 className="display-type boot-title">Dungeon of Recall</h1>
            <p className="boot-subtitle">a boss remembers every wrong answer</p>
          </div>
          <form className="boot-form" onSubmit={handleDescend}>
            <input
              className="boot-input"
              placeholder="enter your name"
              value={nameDraft}
              onChange={(e) => setNameDraft(e.target.value)}
              disabled={phase === 'descending'}
              autoFocus
            />
            <button className="btn btn--primary" type="submit" disabled={phase === 'descending' || !nameDraft.trim()}>
              {phase === 'descending' ? 'Descending…' : 'Descend'}
            </button>
          </form>
          {errorMessage && <p className="memory-view__hint memory-view__hint--danger">{errorMessage}</p>}
        </div>
      </div>
    )
  }

  return (
    <div className="app-shell">
      <div className="hud-grid">
        <FloorMap floors={run?.floors ?? []} currentFloorIndex={run?.current_floor_index ?? 0} />
        <MemoryGraph topics={topics} playerName={playerName} />
        <MemoryView playerName={playerName} embedded />
      </div>

      <QuestionModal
        challenge={challenge}
        onSubmit={handleAnswer}
        onDismiss={handleContinue}
        submitting={submitting}
        result={result}
      />
    </div>
  )
}
