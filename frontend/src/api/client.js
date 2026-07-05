const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export const PLAYER_NAME_KEY = "dungeon-of-recall:player-name";
export const RUN_ID_KEY = "dungeon-of-recall:run-id";

export const LANGUAGES = ["python3", "java", "c++", "c"];

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`${options.method || "GET"} ${url} failed: ${res.status} ${body}`);
  }
  return res.json();
}

function post(path, payload) {
  return request(path, { method: "POST", body: JSON.stringify(payload) });
}

// -> { run_id, player_id, level, discovery: {revealed, via, whispers} }
export function startGame(playerName) {
  return post("/game/start", { player_name: playerName });
}

// -> { challenge, level, in_hidden, hidden_level }
export function nextChallenge(runId) {
  return post("/game/next", { run_id: runId });
}

// payload: { answer } for short_answer, { code, language } for code.
// -> { result: AnswerResult, level, in_hidden, hidden_level, discovery, new_whisper }
export function submitAnswer(runId, questionId, payload) {
  return post("/game/answer", {
    run_id: runId,
    question_id: questionId,
    answer: payload.answer ?? null,
    code: payload.code ?? null,
    language: payload.language ?? "python3",
  });
}

// action: revisit_floor | inspect | idle_linger | off_path_move -> { recorded }
export function explore(runId, action, target) {
  return post("/game/explore", { run_id: runId, action, target: target ?? null });
}

// -> StartResponse shape, 403 while the entrance is sealed
export function enterHidden(runId) {
  return post("/game/hidden/enter", { run_id: runId });
}

// -> { player_id, threat_level, executive_summary, difficulty_spike,
//      topics: [{id, name, weight, reinforced_recently}], profile, graph }
export function getMemoryReport(playerId) {
  return request(`/memory/report/${encodeURIComponent(playerId)}`);
}

// -> { forgotten: player_id }
export function forget(playerId) {
  return post(`/memory/forget/${encodeURIComponent(playerId)}`, {});
}

// -> [{ player_id, max_level, explorer_score, threat_level, correct_attempts, total_attempts, last_updated }]
export function getLeaderboard() {
  return request("/game/leaderboard");
}

