import React, { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

export default function MemoryGraph({ graph, profile, playerName = "You" }) {
  const prevWeights = useRef({});
  const [reinforced, setReinforced] = useState(new Set());

  const edges = graph?.edges || [];
  const nodes = graph?.nodes || [];

  // Identify weak/strong topics for styling
  const weakTopics = new Set((profile?.weak_topics || []).map((t) => t.toLowerCase()));
  const strongTopics = new Set((profile?.strong_topics || []).map((t) => t.toLowerCase()));

  useEffect(() => {
    const grown = new Set();
    edges.forEach((edge) => {
      const edgeId = `${edge.from}->${edge.to}`;
      const prev = prevWeights.current[edgeId];
      // Check if weight grew or if the target topic is reinforced recently
      const isWeak = weakTopics.has(edge.to.toLowerCase());
      if (isWeak || (prev !== undefined && edge.weight > prev)) {
        grown.add(edgeId);
      }
      prevWeights.current[edgeId] = edge.weight;
    });

    if (grown.size === 0) return;
    setReinforced(grown);
    const timer = setTimeout(() => setReinforced(new Set()), 1500);
    return () => clearTimeout(timer);
  }, [edges, weakTopics]);

  if (edges.length === 0) {
    return (
      <div 
        className="glass-panel p-4 text-center border border-cyan-mist/20"
        style={{ background: "rgba(19, 26, 20, 0.45)" }}
        data-testid="memory-graph-empty"
      >
        <p className="font-body text-xs text-stone-pale italic">
          No memory connections mapped yet — the dungeon has not yet spun its neural web of you.
        </p>
      </div>
    );
  }

  const height = Math.max(160, edges.length * 44);
  const centerY = height / 2;
  const playerX = 35;
  const topicX = 210;
  const step = edges.length > 0 ? (height - 30) / edges.length : 0;

  return (
    <div
      className="glass-panel p-3 border border-cyan-mist/25 relative overflow-hidden"
      style={{
        background: "linear-gradient(135deg, rgba(20, 30, 22, 0.7) 0%, rgba(11, 18, 12, 0.9) 100%)",
      }}
      data-testid="memory-graph"
    >
      <div className="absolute top-2 left-3 flex items-center gap-1">
        <span className="w-1.5 h-1.5 rounded-full bg-cyan-mist animate-ping" />
        <span className="font-mono text-[9px] tracking-wider text-cyan-mist/80 uppercase">
          Neural Web
        </span>
      </div>

      <svg
        className="w-full h-auto mt-4"
        viewBox={`0 0 280 ${height}`}
        preserveAspectRatio="xMidYMid meet"
        role="img"
        aria-label="Cognitive Memory Graph"
      >
        <defs>
          <radialGradient id="playerGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#00E5FF" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#0891A0" stopOpacity="0.1" />
          </radialGradient>
        </defs>

        {/* Draw Edges */}
        {edges.map((edge, i) => {
          const y = step * i + 15;
          const edgeId = `${edge.from}->${edge.to}`;
          const isReinforced = reinforced.has(edgeId);

          return (
            <line
              key={`edge-${edgeId}`}
              x1={playerX}
              y1={centerY}
              x2={topicX}
              y2={y}
              stroke="#00E5FF"
              strokeWidth={1.5 + edge.weight * 5.5}
              strokeOpacity={isReinforced ? 0.95 : 0.25 + edge.weight * 0.45}
              style={{
                filter: isReinforced ? "drop-shadow(0 0 6px #00E5FF)" : "none",
                transition: "stroke-width 0.4s ease, stroke-opacity 0.4s ease",
              }}
              className={isReinforced ? "animate-pulse" : ""}
            />
          );
        })}

        {/* Draw Player Node */}
        <circle
          cx={playerX}
          cy={centerY}
          r={10}
          fill="#0B120C"
          stroke="#00E5FF"
          strokeWidth="2"
          style={{ filter: "drop-shadow(0 0 8px #00E5FF)" }}
        />
        <text
          x={playerX}
          y={centerY - 14}
          textAnchor="middle"
          fill="#E8EDE6"
          className="font-heading font-bold text-[9px] uppercase tracking-widest"
        >
          {playerName.substring(0, 8)}
        </text>

        {/* Draw Topic Nodes */}
        {edges.map((edge, i) => {
          const y = step * i + 15;
          const isWeak = weakTopics.has(edge.to.toLowerCase());
          const isStrong = strongTopics.has(edge.to.toLowerCase());

          // Colors based on design tokens
          const nodeColor = isWeak ? "#FF6B35" : isStrong ? "#7CE38B" : "#8A928A";
          const glowShadow = isWeak
            ? "rgba(255,107,53,0.6)"
            : isStrong
            ? "rgba(124,227,139,0.5)"
            : "rgba(0,229,255,0.2)";

          return (
            <g key={`node-${edge.to}`}>
              <circle
                cx={topicX}
                cy={y}
                r={4.5 + edge.weight * 4.5}
                fill="#0B120C"
                stroke={nodeColor}
                strokeWidth="1.8"
                style={{ filter: `drop-shadow(0 0 5px ${glowShadow})` }}
              />
              <text
                x={topicX + 12}
                y={y + 3}
                fill="#E8EDE6"
                className="font-mono text-[9px] tracking-wide"
              >
                {edge.to}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
