// Role D — renders one challenge.
import { useState } from "react";
export default function QuestionModal({ challenge, onAnswer }) {
  const [value, setValue] = useState("");
  const [started] = useState(Date.now());
  return (
    <div className="modal">
      <span className="floor">Floor {challenge.floor} · {challenge.difficulty}</span>
      {challenge.boss_dialogue && <p className="boss">{challenge.boss_dialogue}</p>}
      <p>{challenge.prompt}</p>
      <input value={value} onChange={(e) => setValue(e.target.value)} />
      <button onClick={() => onAnswer(value, started)}>Answer</button>
    </div>
  );
}
