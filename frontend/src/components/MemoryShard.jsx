import React from "react";
import { motion } from "framer-motion";
import { Target, Activity, Shield, History, Brain } from "lucide-react";
import { MEMORY_SHARD_TYPES } from "../data/memory";

const ICON_MAP = { target: Target, activity: Activity, shield: Shield, history: History };

// Stone-tablet styled glass card — one per remembered fact.
// Data-driven from a `shard` object: { id, type, title, detail, source, weight }
export const MemoryShard = ({ shard, index = 0 }) => {
  const type = MEMORY_SHARD_TYPES[shard.type] || MEMORY_SHARD_TYPES.behavior;
  const Icon = ICON_MAP[type.icon] || Brain;
  const weightPct = Math.round((shard.weight ?? 0.5) * 100);

  return (
    <motion.div
      initial={{ opacity: 0, x: 24 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.05 * index, duration: 0.32, ease: [0.22, 1, 0.36, 1] }}
      className="relative"
      data-testid={`memory-shard-${shard.id}`}
      data-shard-type={shard.type}
    >
      {/* Stone tablet card */}
      <div
        className="relative overflow-hidden rounded-lg pl-11 pr-3 py-2.5"
        style={{
          background:
            "linear-gradient(135deg, rgba(28,42,30,0.68) 0%, rgba(19,26,20,0.85) 100%)",
          border: `1px solid ${type.ring}`,
          borderLeft: `3px solid ${type.accent}`,
          boxShadow: `0 4px 18px ${type.glow}, inset 0 1px 0 rgba(232,237,230,0.05)`,
          backdropFilter: "blur(10px)",
        }}
      >
        {/* faint ember edge stroke (top+bottom) */}
        <div
          className="absolute inset-x-0 top-0 h-px opacity-60"
          style={{ background: `linear-gradient(90deg, transparent, ${type.accent}, transparent)` }}
        />
        <div
          className="absolute inset-x-0 bottom-0 h-px opacity-30"
          style={{ background: `linear-gradient(90deg, transparent, ${type.accent}, transparent)` }}
        />

        {/* Rune icon disc */}
        <div
          className="absolute left-2 top-1/2 -translate-y-1/2 w-7 h-7 rounded-md flex items-center justify-center border"
          style={{
            background: "linear-gradient(180deg, #2A3F2D 0%, #131A14 100%)",
            borderColor: type.ring,
            boxShadow: `inset 0 0 8px rgba(0,0,0,0.6), 0 0 10px ${type.glow}`,
          }}
        >
          <Icon className="w-3.5 h-3.5" style={{ color: type.accent }} strokeWidth={2.5} />
        </div>

        {/* Type + weight header row */}
        <div className="flex items-baseline justify-between gap-2 mb-0.5">
          <span
            className="font-mono text-[9px] tracking-[0.28em] uppercase"
            style={{ color: type.accent }}
          >
            {type.label}
          </span>
          <span className="font-mono text-[9px] text-stone-pale/80 tabular-nums">
            w:{weightPct}
          </span>
        </div>

        {/* Title */}
        <p
          className="font-heading text-[13px] font-bold text-bone leading-tight"
          data-testid={`memory-shard-title-${shard.id}`}
        >
          {shard.title}
        </p>

        {/* Detail */}
        {shard.detail && (
          <p className="font-body text-[11px] text-stone-pale leading-snug mt-0.5">
            {shard.detail}
          </p>
        )}

        {/* Source timestamp */}
        {shard.source && (
          <div className="flex items-center gap-1.5 mt-1.5">
            <span
              className="w-1 h-1 rounded-full"
              style={{ background: type.accent, boxShadow: `0 0 6px ${type.accent}` }}
            />
            <span className="font-mono text-[9px] tracking-[0.18em] uppercase text-stone-pale/70">
              {shard.source}
            </span>
          </div>
        )}
      </div>
    </motion.div>
  );
};

// Empty-state variant
export const MemoryShardEmpty = ({ message }) => (
  <div
    className="rounded-lg border border-stone-mid/60 bg-stone-dark/40 py-6 px-4 text-center"
    data-testid="memory-shard-empty"
  >
    <div className="w-10 h-10 mx-auto rounded-full border border-stone-mid/70 flex items-center justify-center mb-2 bg-stone-darkest">
      <Brain className="w-5 h-5 text-stone-light" strokeWidth={2} />
    </div>
    <p className="font-body italic text-xs text-stone-pale">{message}</p>
  </div>
);
