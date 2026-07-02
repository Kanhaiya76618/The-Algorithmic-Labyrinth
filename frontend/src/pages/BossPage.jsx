import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import Frame from '../components/Frame.jsx'
import QuestionModal from '../components/QuestionModal.jsx'
import { nextChallenge, submitAnswer, PLAYER_NAME_KEY, RUN_ID_KEY } from '../api/client.js'

export default function BossPage() {
  const location = useLocation()
  const navigate = useNavigate()

  const runId = location.state?.runId ?? window.localStorage.getItem(RUN_ID_KEY)
  const playerName = location.state?.playerName ?? window.localStorage.getItem(PLAYER_NAME_KEY)
  const bossName = location.state?.boss?.name ?? 'The Recollector'

  const [challenge, setChallenge] = useState(null)
  const [result, setResult] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [victory, setVictory] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    if (!runId) {
      navigate('/')
      return
    }
    nextChallenge(runId)
      .then(setChallenge)
      .catch((err) => setErrorMessage(err.message || 'Could not summon the boss.'))
  }, [runId, navigate])

  async function handleAnswer(answer) {
    setSubmitting(true)
    try {
      const outcome = await submitAnswer(runId, challenge.id, answer)
      setResult(outcome)
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
    if (outcome?.run_complete) {
      setVictory(true)
      return
    }
    try {
      const next = await nextChallenge(runId)
      setChallenge(next)
    } catch (err) {
      setErrorMessage(err.message || 'Could not summon the next question.')
    }
  }

  return (
    <div className="app-shell">
      <div className="boot-screen">
        <Frame label="Boss Encounter" className="boss-panel">
          <span className="status-pill status-pill--danger status-pill--live">
            <span className="status-dot" />
            boss encounter
          </span>
          <h2 className="boss-panel__name">{bossName}</h2>
          <p className="boss-panel__flavor">
            {playerName ? `${playerName}, it` : 'It'} remembers every floor you struggled on.
          </p>

          {victory && (
            <button className="btn btn--primary" onClick={() => navigate('/')}>
              Return to Surface
            </button>
          )}

          {errorMessage && <p className="memory-view__hint memory-view__hint--danger">{errorMessage}</p>}
        </Frame>
      </div>

      {!victory && (
        <QuestionModal
          challenge={challenge}
          onSubmit={handleAnswer}
          onDismiss={handleContinue}
          submitting={submitting}
          result={result}
        />
      )}
    </div>
  )
}
