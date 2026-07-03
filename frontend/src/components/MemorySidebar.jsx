import React from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Brain, X } from "lucide-react";
import { MemoryShard, MemoryShardEmpty } from "./MemoryShard";
import { CornerRune } from "./Atmosphere";
import { BOSS_IDENTITY, EMPTY_MEMORY_MESSAGE } from "../data/memory";
import MemoryGraph from "./MemoryGraph";

// Slide-out glassmorphism sidebar rendered on the boss screen.
// Props: open (bool), onClose (fn), shards (array), bossName (str), source (str)
export const MemorySidebar = ({
  open,
  onClose,
  shards = [],
  bossName = BOSS_IDENTITY.name,
  source = BOSS_IDENTITY.memory_source,
  onForget,
  graph,
  profile,
  playerName,
}) => (
  <AnimatePresence>
    {open && (
      <>
        {/* Dim backdrop */}
        <motion.div
          key="memory-backdrop"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.25 }}
          className="absolute inset-0 bg-stone-darkest/70 backdrop-blur-[2px] z-40"
          onClick={onClose}
          data-testid="memory-sidebar-backdrop"
        />

        {/* Sidebar panel — 82% width, right-anchored */}
        <motion.aside
          key="memory-sidebar"
          initial={{ x: "100%" }}
          animate={{ x: 0 }}
          exit={{ x: "100%" }}
          transition={{ type: "spring", damping: 26, stiffness: 260 }}
          className="absolute right-0 top-0 bottom-0 z-50 w-[82%] max-w-[340px] flex flex-col"
          data-testid="memory-sidebar"
        >
          <div className="glass-panel rounded-none rounded-l-2xl flex-1 flex flex-col overflow-hidden border-r-0 relative">
            <CornerRune className="absolute -top-2 -left-2 w-6 h-6" />
            <CornerRune className="absolute -bottom-2 -left-2 w-6 h-6 rotate-[-90deg]" />

            {/* Header */}
            <header className="relative px-4 pt-4 pb-3">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <p className="font-mono text-[10px] tracking-[0.32em] text-cyan-mist/80 uppercase">
                    Cognee · Memory Recall
                  </p>
                  <h2
                    className="font-display text-xl font-black leading-none mt-1 text-bone text-shadow-stone animate-glow-pulse"
                    style={{
                      background:
                        "linear-gradient(180deg, #E8EDE6 0%, #00E5FF 100%)",
                      WebkitBackgroundClip: "text",
                      WebkitTextFillColor: "transparent",
                    }}
                    data-testid="memory-sidebar-title"
                  >
                    {bossName.toUpperCase()} REMEMBERS…
                  </h2>
                </div>
                <button
                  onClick={onClose}
                  data-testid="memory-sidebar-close"
                  aria-label="Close memory sidebar"
                  className="shrink-0 w-8 h-8 rounded-full bg-stone-darkest/70 border border-cyan-mist/40 flex items-center justify-center hover:border-cyan-mist"
                >
                  <X className="w-4 h-4 text-bone" />
                </button>
              </div>

              <div className="rune-divider mt-3" />

              <div className="flex items-center gap-1.5 mt-2">
                <Brain className="w-3 h-3 text-cyan-mist" strokeWidth={2.5} />
                <span className="font-mono text-[9px] tracking-[0.22em] text-cyan-mist/70 uppercase truncate">
                  {source} · {shards.length} shard{shards.length === 1 ? "" : "s"}
                </span>
              </div>
            </header>

            {/* Shards list */}
            <div
              className="flex-1 overflow-y-auto px-4 pb-4 space-y-3"
              data-testid="memory-sidebar-list"
            >
              <MemoryGraph graph={graph} profile={profile} playerName={playerName} />

              <div className="rune-divider opacity-40 my-2" />

              {shards.length === 0 ? (
                <MemoryShardEmpty message={EMPTY_MEMORY_MESSAGE} />
              ) : (
                shards.map((s, i) => <MemoryShard key={s.id} shard={s} index={i} />)
              )}
            </div>

            {/* Footer */}
            <footer className="px-4 py-3 border-t border-cyan-mist/15 bg-stone-darkest/50 space-y-2">
              <button
                onClick={onClose}
                className="btn-cyan w-full !py-2"
                data-testid="memory-sidebar-continue"
              >
                Let It Begin
              </button>
              {onForget && (
                <button
                  onClick={() => {
                    onForget();
                    onClose();
                  }}
                  className="btn-ember w-full !py-1 text-[9px] font-mono tracking-widest"
                  data-testid="btn-forget"
                >
                  POTION OF FORGETTING
                </button>
              )}
              <p className="font-mono text-[9px] tracking-[0.22em] text-stone-pale/60 uppercase text-center">
                Closing seals the memory
              </p>
            </footer>
          </div>
        </motion.aside>
      </>
    )}
  </AnimatePresence>
);

// The trigger button (brain-rune icon) rendered in the boss HUD.
export const MemoryTrigger = ({ onClick, active = false, count = 0 }) => (
  <motion.button
    onClick={onClick}
    whileHover={{ scale: 1.06 }}
    whileTap={{ scale: 0.94 }}
    animate={active ? {} : { boxShadow: [
      "0 0 0px rgba(0,229,255,0.0)",
      "0 0 22px rgba(0,229,255,0.7)",
      "0 0 0px rgba(0,229,255,0.0)",
    ] }}
    transition={active ? {} : { duration: 2.6, repeat: Infinity, ease: "easeInOut" }}
    className="relative w-10 h-10 rounded-full carved-stone flex items-center justify-center"
    style={{
      borderColor: active ? "#00E5FF" : undefined,
      background: active
        ? "linear-gradient(180deg, #143A44 0%, #0B1F24 100%)"
        : undefined,
    }}
    data-testid="btn-open-memory"
    aria-label="Open memory sidebar"
  >
    <Brain className="w-5 h-5 text-cyan-mist" strokeWidth={2.5} />
    {count > 0 && (
      <span
        className="absolute -top-1 -right-1 min-w-[16px] h-[16px] px-1 rounded-full flex items-center justify-center border border-stone-darkest font-mono text-[9px] font-bold text-bone"
        style={{ background: "#FF6B35", boxShadow: "0 0 6px rgba(255,107,53,0.7)" }}
      >
        {count}
      </span>
    )}
  </motion.button>
);
