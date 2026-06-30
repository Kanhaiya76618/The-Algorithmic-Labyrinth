// Role D — graph viz of the player's memory. Swap in react-force-graph later.
export default function MemoryGraph({ data }) {
  return (
    <ul className="memgraph">
      {data.edges.map((e, i) => (
        <li key={i} style={{ fontWeight: 400 + e.weight * 100 }}>
          {e.from} → {e.to} (weight {e.weight})
        </li>
      ))}
    </ul>
  );
}
