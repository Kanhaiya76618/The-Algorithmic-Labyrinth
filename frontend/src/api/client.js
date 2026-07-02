// No backend contract exists yet (contracts/ and backend/ are still skeletons), so this
// file defines the shapes the frontend expects. Coordinate with backend owners before
// changing these paths/payloads.

export const PLAYER_NAME_KEY = 'dungeon-of-recall:player-name'
export const RUN_ID_KEY = 'dungeon-of-recall:run-id'

async function request(path, options = {}) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.text().catch(() => '')
    throw new Error(`${options.method || 'GET'} ${path} failed: ${res.status} ${body}`)
  }
  return res.json()
}

// POST /game/start { player_name } -> RunState
// RunState: { run_id, player_name, current_floor_index,
//   floors: [{ index, name, status: 'cleared'|'current'|'locked', difficulty }],
//   boss: { name, hp, max_hp } | null }
export function startGame(playerName) {
  return request('/game/start', {
    method: 'POST',
    body: JSON.stringify({ player_name: playerName }),
  })
}

// POST /game/next { run_id } -> Challenge
// Challenge: { id, floor_index, topic, type: 'mcq'|'input', prompt, choices: string[] | null }
export function nextChallenge(runId) {
  return request('/game/next', {
    method: 'POST',
    body: JSON.stringify({ run_id: runId }),
  })
}

// POST /game/answer { run_id, challenge_id, answer } -> AnswerResult
// AnswerResult: { correct, floor_cleared, run_complete, boss_triggered,
//   next_floor_index, message }
export function submitAnswer(runId, challengeId, answer) {
  return request('/game/answer', {
    method: 'POST',
    body: JSON.stringify({ run_id: runId, challenge_id: challengeId, answer }),
  })
}

// GET /memory/report/:playerName -> MemoryReport
// MemoryReport: { player_name, threat_level (0-100), executive_summary,
//   difficulty_spike: { topic, delta } | null,
//   topics: [{ id, name, weight (0-1), reinforced_recently }] }
export function getMemoryReport(playerName) {
  return request(`/memory/report/${encodeURIComponent(playerName)}`)
}

// POST /memory/forget { player_name, topic? } -> { ok }
export function forget(playerName, topic) {
  return request('/memory/forget', {
    method: 'POST',
    body: JSON.stringify({ player_name: playerName, topic }),
  })
}
