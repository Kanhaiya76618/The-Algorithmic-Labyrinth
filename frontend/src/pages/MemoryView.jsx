// Role D — the player-facing "what the Boss remembers" graph + live forget.
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { memoryGraph, forget } from "../api/client.js";
import MemoryGraph from "../components/MemoryGraph.jsx";

export default function MemoryView() {
  const { playerId } = useParams();
  const [graph, setGraph] = useState({ nodes: [], edges: [] });
  const refresh = () => memoryGraph(playerId).then(setGraph);
  useEffect(() => { refresh(); }, [playerId]);
  return (
    <div>
      <MemoryGraph data={graph} />
      <button onClick={() => forget(playerId).then(refresh)}>
        🧪 Potion of Forgetting
      </button>
    </div>
  );
}
