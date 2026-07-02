import { useEffect, useState } from 'react'
import Frame from './Frame.jsx'

export default function QuestionModal({ challenge, onSubmit, onDismiss, submitting = false, result = null }) {
  const [answer, setAnswer] = useState('')
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    setAnswer('')
    setSelected(null)
  }, [challenge?.id])

  if (!challenge) return null

  const value = challenge.type === 'mcq' ? selected : answer
  const canSubmit = challenge.type === 'mcq' ? value !== null : value.trim().length > 0

  function handleSubmit(e) {
    e.preventDefault()
    if (!canSubmit) return
    onSubmit(value)
  }

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true">
      <Frame label={`Floor ${challenge.floor_index + 1} · ${challenge.topic}`} className="question-modal">
        <p className="question-modal__prompt">{challenge.prompt}</p>

        {!result ? (
          <form onSubmit={handleSubmit}>
            {challenge.type === 'mcq' ? (
              <div className="question-modal__choices">
                {challenge.choices.map((choice) => (
                  <button
                    key={choice}
                    type="button"
                    className={`question-modal__choice${selected === choice ? ' question-modal__choice--selected' : ''}`}
                    onClick={() => setSelected(choice)}
                    disabled={submitting}
                  >
                    {choice}
                  </button>
                ))}
              </div>
            ) : (
              <input
                className="boot-input question-modal__input"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="your answer"
                disabled={submitting}
                autoFocus
              />
            )}

            <div className="question-modal__actions">
              <button className="btn btn--primary" type="submit" disabled={submitting || !canSubmit}>
                {submitting ? 'Casting…' : 'Submit'}
              </button>
            </div>
          </form>
        ) : (
          <div className="question-modal__result">
            <span className={`status-pill ${result.correct ? 'status-pill--ok' : 'status-pill--danger'}`}>
              <span className="status-dot" />
              {result.correct ? 'correct' : 'incorrect'}
            </span>
            {result.message && <p className="question-modal__message">{result.message}</p>}
            <button className="btn btn--ghost" onClick={onDismiss}>
              Continue
            </button>
          </div>
        )}
      </Frame>
    </div>
  )
}
