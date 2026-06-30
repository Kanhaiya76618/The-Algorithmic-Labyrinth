// Role D owns this, but it MIRRORS contracts/schemas.py exactly.
// If a contract field changes in the huddle, update it here in lockstep.
const j = (r) => r.json();

export const startGame = (playerId) =>
  fetch("/game/start", { method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ player_id: playerId }) }).then(j);

export const nextChallenge = (playerId) =>
  fetch(`/game/${playerId}/next`).then(j);

export const submitAnswer = (payload) =>
  fetch("/game/answer", { method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload) }).then(j);

export const memoryGraph = (playerId) =>
  fetch(`/memory/${playerId}/graph`).then(j);

export const forget = (playerId) =>
  fetch(`/memory/${playerId}/forget`, { method: "POST" }).then(j);
