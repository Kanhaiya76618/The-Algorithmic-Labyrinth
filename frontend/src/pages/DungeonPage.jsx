// Role D — main crawler screen. Calls Role B's /game API via client.js.
import { useEffect, useState } from "react";
import { startGame, nextChallenge, submitAnswer } from "../api/client.js";
import QuestionModal from "../components/QuestionModal.jsx";

export default function DungeonPage() {
  const playerId = "demo";
  const [challenge, setChallenge] = useState(null);

  useEffect(() => {
    startGame(playerId).then(() => nextChallenge(playerId).then(setChallenge));
  }, []);

  async function answer(value, started) {
    await submitAnswer({ player_id: playerId, question_id: challenge.question_id,
      answer: value, time_taken_s: (Date.now() - started) / 1000 });
    nextChallenge(playerId).then(setChallenge);
  }

  if (!challenge) return <p>Descending…</p>;
  return <QuestionModal challenge={challenge} onAnswer={answer} />;
}
