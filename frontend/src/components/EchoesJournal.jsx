import React from "react";
import { AnimatePresence, motion } from "framer-motion";
import { BookOpen, X, Sparkles, Skull } from "lucide-react";
import { CornerRune } from "./Atmosphere";

// Single accuracy row for both pages (mastered / haunting)
const AccuracyRow = ({ topic, accuracy, tone = "cyan", index = 0 }) => {
  const isWeak = tone === "ember";
  const color = isWeak ? "#FF6B35" : "#7CE38B";
  const bg = isWeak ? "rgba(255,107,53,0.12)" : "rgba(124,227,139,0.10)";
  const testType = isWeak ? "haunting" : "mastered";
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.08 + index * 0.06 }}
      className="py-1.5"
      data-testid={`echoes-row-${testType}-${topic.toLowerCase()}`}
    >
      {/* Line 1: rune icon + topic + accuracy number */}
      <div className="flex items-center gap-2">
        <div
          className="w-6 h-6 shrink-0 rounded flex items-center justify-center border"
          style={{
            borderColor: color,
            background: bg,
            boxShadow: `0 0 8px ${color}55`,
          }}
        >
          {isWeak ? (
            <Skull className="w-3 h-3" style={{ color }} strokeWidth={2.5} />
          ) : (
            <Sparkles className="w-3 h-3" style={{ color }} strokeWidth={2.5} />
          )}
        </div>
        <span className="flex-1 min-w-0 font-heading text-[13px] font-bold text-bone truncate">
          {topic}
        </span>
        <span
          className="font-mono text-[10px] tabular-nums text-right shrink-0"
          style={{ color }}
        >
          {Math.round(accuracy * 100)}%
        </span>
      </div>
      {/* Line 2: full-width accuracy bar (static width — content must never
          depend on a JS animation frame to become visible) */}
      <div className="mt-1 h-1.5 rounded-full bg-stone-darkest overflow-hidden border border-stone-mid/60">
        <div
          className="h-full"
          style={{
            width: `${Math.round(accuracy * 100)}%`,
            background: `linear-gradient(90deg, ${color}66, ${color})`,
            boxShadow: `0 0 6px ${color}`,
          }}
        />
      </div>
    </motion.div>
  );
};

// Per-zone accuracy pill for the bottom strip
const ZonePill = ({ zone, index = 0 }) => {
  const pct = Math.round(zone.accuracy * 100);
  const color =
    zone.accuracy === 0 ? "#4F554F" : zone.accuracy < 0.5 ? "#FF6B35" : zone.accuracy < 0.75 ? "#F5B942" : "#7CE38B";
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.35 + index * 0.05 }}
      className="flex-1 min-w-0 flex flex-col items-center gap-1"
      data-testid={`echoes-zone-${zone.id}`}
    >
      <div className="w-full h-1 rounded-full bg-stone-darkest overflow-hidden border border-stone-mid/50">
        <div
          className="h-full"
          style={{
            width: `${pct}%`,
            background: `linear-gradient(90deg, ${color}66, ${color})`,
            boxShadow: `0 0 4px ${color}`,
          }}
        />
      </div>
      <span className="font-mono text-[8px] tracking-[0.15em] uppercase text-stone-pale truncate w-full text-center">
        {zone.name.split(" ")[0]}
      </span>
      <span
        className="font-mono text-[9px] tabular-nums"
        style={{ color: zone.accuracy === 0 ? "#4F554F" : color }}
      >
        {pct}%
      </span>
    </motion.div>
  );
};

// Full-screen "ECHOES" journal overlay (two-page book).
// Props: open, onClose, data { mastered, haunting, zones }
export const EchoesJournal = ({ open, onClose, data }) => (
  <AnimatePresence>
    {open && (
      <>
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-moss-darkest/85 backdrop-blur-md z-40"
          onClick={onClose}
          data-testid="echoes-backdrop"
        />

        {/* Book overlay */}
        <motion.div
          initial={{ opacity: 0, rotateX: 60, y: 40 }}
          animate={{ opacity: 1, rotateX: 0, y: 0 }}
          exit={{ opacity: 0, rotateX: -30, y: 20 }}
          transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
          style={{ perspective: 1000, transformStyle: "preserve-3d" }}
          className="absolute inset-3 z-50 flex flex-col"
          data-testid="echoes-journal"
        >
          <div className="carved-stone flex-1 flex flex-col p-3 relative overflow-hidden">
            <CornerRune className="absolute -top-2 -left-2 w-6 h-6" />
            <CornerRune className="absolute -top-2 -right-2 w-6 h-6" flip />

            {/* Header strip */}
            <div className="flex items-center gap-2 pb-2">
              <div className="w-8 h-8 rounded-md border border-cyan-mist/60 flex items-center justify-center bg-moss-dark">
                <BookOpen className="w-4 h-4 text-cyan-mist" strokeWidth={2.5} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-mono text-[9px] tracking-[0.32em] uppercase text-cyan-mist/80">
                  Cognee · Journal
                </p>
                <h2 className="font-display text-xl font-black text-bone leading-none">
                  ECHOES
                </h2>
              </div>
              <button
                onClick={onClose}
                data-testid="echoes-close"
                aria-label="Close echoes journal"
                className="w-8 h-8 rounded-full bg-stone-darkest/70 border border-cyan-mist/40 flex items-center justify-center hover:border-cyan-mist"
              >
                <X className="w-4 h-4 text-bone" />
              </button>
            </div>

            <div className="rune-divider" />

            {/* Two facing pages */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.15 }}
              className="flex-1 grid grid-cols-2 gap-2 pt-3 min-h-0"
            >
              {/* MASTERED (green) */}
              <section
                className="relative rounded-lg p-3 overflow-y-auto"
                style={{
                  background:
                    "linear-gradient(180deg, rgba(124,227,139,0.06) 0%, rgba(19,26,20,0.4) 100%)",
                  border: "1px solid rgba(124,227,139,0.35)",
                  boxShadow: "inset 0 1px 0 rgba(232,237,230,0.05)",
                }}
                data-testid="echoes-page-mastered"
              >
                <p className="font-mono text-[9px] tracking-[0.32em] uppercase text-[#7CE38B]">
                  Left Page
                </p>
                <h3 className="font-display text-base font-bold text-bone leading-none mt-0.5 mb-2">
                  MASTERED
                </h3>
                <div className="space-y-0.5">
                  {data.mastered.map((row, i) => (
                    <AccuracyRow
                      key={row.topic}
                      topic={row.topic}
                      accuracy={row.accuracy}
                      tone="cyan"
                      index={i}
                    />
                  ))}
                </div>
              </section>

              {/* HAUNTING (ember) */}
              <section
                className="relative rounded-lg p-3 overflow-y-auto"
                style={{
                  background:
                    "linear-gradient(180deg, rgba(255,107,53,0.06) 0%, rgba(19,26,20,0.4) 100%)",
                  border: "1px solid rgba(255,107,53,0.35)",
                  boxShadow: "inset 0 1px 0 rgba(232,237,230,0.05)",
                }}
                data-testid="echoes-page-haunting"
              >
                <p className="font-mono text-[9px] tracking-[0.32em] uppercase text-ember-orange">
                  Right Page
                </p>
                <h3 className="font-display text-base font-bold text-bone leading-none mt-0.5 mb-2">
                  HAUNTING YOU
                </h3>
                <div className="space-y-0.5">
                  {data.haunting.map((row, i) => (
                    <AccuracyRow
                      key={row.topic}
                      topic={row.topic}
                      accuracy={row.accuracy}
                      tone="ember"
                      index={i}
                    />
                  ))}
                </div>
              </section>
            </motion.div>

            {/* Bottom per-zone accuracy strip */}
            <div className="mt-3 pt-2 border-t border-cyan-mist/15" data-testid="echoes-zone-strip">
              <p className="font-mono text-[9px] tracking-[0.32em] uppercase text-cyan-mist/80 mb-1.5">
                Zone Recall
              </p>
              <div className="flex items-start gap-2">
                {data.zones.map((z, i) => (
                  <ZonePill key={z.id} zone={z} index={i} />
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </>
    )}
  </AnimatePresence>
);

// Small journal-button trigger for the world map HUD
export const EchoesTrigger = ({ onClick }) => (
  <motion.button
    onClick={onClick}
    whileHover={{ scale: 1.06 }}
    whileTap={{ scale: 0.94 }}
    animate={{
      boxShadow: [
        "0 0 0 rgba(0,229,255,0)",
        "0 0 18px rgba(0,229,255,0.55)",
        "0 0 0 rgba(0,229,255,0)",
      ],
    }}
    transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
    className="relative w-10 h-10 rounded-full carved-stone flex items-center justify-center"
    data-testid="btn-open-echoes"
    aria-label="Open echoes journal"
  >
    <BookOpen className="w-5 h-5 text-cyan-mist" strokeWidth={2.5} />
    <span
      className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-cyan-mist"
      style={{ boxShadow: "0 0 8px #00E5FF" }}
    />
  </motion.button>
);
