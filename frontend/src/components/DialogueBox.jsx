import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Brain, ChevronDown } from "lucide-react";
import { CornerRune } from "./Atmosphere";

// Small drifting memory-rune glyph used behind the RECALLED dialogue box
const RuneGlyph = ({ index, left, delay, size = 12 }) => (
  <motion.svg
    initial={{ opacity: 0, y: 0 }}
    animate={{ opacity: [0, 0.85, 0], y: -60 }}
    transition={{ duration: 4, repeat: Infinity, delay, ease: "easeOut" }}
    className="absolute pointer-events-none"
    style={{ left: `${left}%`, bottom: 0, width: size, height: size }}
    viewBox="0 0 12 12"
  >
    {index % 3 === 0 ? (
      <path d="M2 2 L10 2 L6 10 Z" stroke="#00E5FF" strokeWidth="1" fill="none" />
    ) : index % 3 === 1 ? (
      <>
        <circle cx="6" cy="6" r="4" stroke="#00E5FF" strokeWidth="1" fill="none" />
        <path d="M6 2 L6 10 M2 6 L10 6" stroke="#00E5FF" strokeWidth="0.8" />
      </>
    ) : (
      <path d="M2 6 Q6 2 10 6 Q6 10 2 6" stroke="#00E5FF" strokeWidth="1" fill="none" />
    )}
  </motion.svg>
);

// Dialogue box with typewriter reveal + optional RECALLED variant.
// Props:
//   entry: { speaker, name, text, memory_ref? }
//   onAdvance, index, total
//   recalled: bool — apply the "RECALLED" visual variant
export const DialogueBox = ({ entry, onAdvance, index = 0, total = 1, recalled = false }) => {
  const { speaker, name, text } = entry;
  const [shown, setShown] = useState("");
  const [done, setDone] = useState(false);

  useEffect(() => {
    setShown("");
    setDone(false);
    let i = 0;
    const id = setInterval(() => {
      i += 1;
      setShown(text.slice(0, i));
      if (i >= text.length) {
        clearInterval(id);
        setDone(true);
      }
    }, 22);
    return () => clearInterval(id);
  }, [text]);

  const handleClick = () => {
    if (!done) {
      setShown(text);
      setDone(true);
    } else {
      onAdvance && onAdvance();
    }
  };

  const isBoss = speaker === "boss";

  return (
    <motion.div
      initial={{ y: 30, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className={`carved-stone relative p-4 pt-5 w-full cursor-pointer select-none`}
      onClick={handleClick}
      data-testid="dialogue-box"
      data-recalled={recalled ? "true" : "false"}
      style={
        recalled
          ? {
              boxShadow:
                "inset 0 3px 0 rgba(255,255,255,0.08), inset 3px 0 0 rgba(255,255,255,0.04), inset -3px 0 0 rgba(0,0,0,0.5), inset 0 -4px 0 rgba(0,0,0,0.65), 0 0 32px rgba(0,229,255,0.35), 0 8px 22px rgba(0,0,0,0.55)",
              borderColor: "rgba(0,229,255,0.5)",
            }
          : undefined
      }
    >
      <CornerRune className="absolute -top-2.5 -left-2.5 w-6 h-6" />
      <CornerRune className="absolute -top-2.5 -right-2.5 w-6 h-6" flip />

      {/* Drifting memory-rune glyphs (only when recalled) */}
      {recalled && (
        <div
          className="absolute inset-0 overflow-hidden pointer-events-none rounded-xl"
          data-testid="dialogue-recalled-runes"
        >
          {[10, 28, 46, 64, 82].map((left, i) => (
            <RuneGlyph key={i} index={i} left={left} delay={i * 0.6} size={10 + (i % 3) * 3} />
          ))}
        </div>
      )}

      {/* Speaker plate */}
      <div className="absolute -top-3 left-4 flex items-center gap-1.5">
        <div
          className={`px-3 py-0.5 rounded-md border-2 border-stone-darkest ${
            isBoss ? "bg-ember-deep" : "bg-cyan-deep"
          }`}
          data-testid="dialogue-speaker"
        >
          <span className="font-heading text-[11px] font-bold tracking-[0.2em] uppercase text-bone">
            {name}
          </span>
        </div>

        {recalled && (
          <motion.div
            initial={{ scale: 0.6, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.15, type: "spring", stiffness: 260 }}
            className="flex items-center gap-1 px-2 py-0.5 rounded-md border-2 border-stone-darkest bg-moss-dark"
            style={{
              boxShadow: "0 0 12px rgba(0,229,255,0.55)",
              borderColor: "#00E5FF",
            }}
            data-testid="dialogue-recalled-tag"
          >
            <motion.div
              animate={{ rotate: [0, 8, -8, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <Brain className="w-3 h-3 text-cyan-mist" strokeWidth={2.5} />
            </motion.div>
            <span className="font-heading text-[9px] font-bold tracking-[0.28em] uppercase text-cyan-mist text-shadow-glow">
              RECALLED
            </span>
          </motion.div>
        )}
      </div>

      <p className="font-body text-[15px] leading-relaxed text-bone min-h-[60px] relative z-10">
        {shown}
        {!done && <span className="inline-block w-2 h-4 bg-cyan-mist ml-0.5 animate-pulse" />}
      </p>

      <div className="flex items-center justify-between mt-2 relative z-10">
        <span className="font-mono text-[10px] tracking-widest text-stone-pale">
          {index + 1} / {total}
        </span>
        {done && (
          <motion.div
            animate={{ y: [0, 3, 0] }}
            transition={{ duration: 1.2, repeat: Infinity }}
            data-testid="dialogue-next-button"
          >
            <ChevronDown className="w-5 h-5 text-cyan-mist" />
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};
