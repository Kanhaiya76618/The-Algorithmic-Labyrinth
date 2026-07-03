import React from "react";
import { motion } from "framer-motion";
import { Brain } from "lucide-react";

// Small segmented brain-rune gauge. Each answered boss question fills 1 segment.
// Variants: empty (0), partial (1..segments-1), full (=segments).
// Props: filled, segments, className
export const MemoryGauge = ({ filled = 0, segments = 5, className = "" }) => {
  const isFull = filled >= segments;

  return (
    <div
      className={`inline-flex items-center gap-2 ${className}`}
      data-testid="memory-gauge"
      data-filled={filled}
      data-full={isFull ? "true" : "false"}
    >
      {/* Brain icon disc */}
      <motion.div
        animate={
          isFull
            ? {
                boxShadow: [
                  "0 0 6px rgba(0,229,255,0.6)",
                  "0 0 22px rgba(0,229,255,0.95)",
                  "0 0 6px rgba(0,229,255,0.6)",
                ],
              }
            : {}
        }
        transition={{ duration: 1.6, repeat: Infinity }}
        className="w-7 h-7 rounded-md flex items-center justify-center border"
        style={{
          background: isFull
            ? "linear-gradient(180deg, #00E5FF33 0%, #0B1F24 100%)"
            : "linear-gradient(180deg, #2A3F2D 0%, #131A14 100%)",
          borderColor: isFull ? "#00E5FF" : "rgba(0,229,255,0.35)",
        }}
        data-testid="memory-gauge-icon"
      >
        <Brain
          className="w-3.5 h-3.5"
          style={{
            color: isFull ? "#E8EDE6" : "#00E5FF",
            filter: isFull ? "drop-shadow(0 0 6px #00E5FF)" : "none",
          }}
          strokeWidth={2.5}
        />
      </motion.div>

      {/* Rune segments */}
      <div
        className="flex gap-1 p-1 rounded-md"
        style={{
          background: "#0B120C",
          border: "1px solid rgba(0,229,255,0.25)",
          boxShadow: "inset 0 2px 4px rgba(0,0,0,0.8)",
        }}
      >
        {Array.from({ length: segments }).map((_, i) => {
          const on = i < filled;
          return (
            <div
              key={i}
              className="w-3 h-4 rounded-[2px] relative overflow-hidden"
              style={{
                background: on
                  ? "linear-gradient(180deg, #7EF6FF 0%, #00E5FF 55%, #0891A0 100%)"
                  : "#1E201E",
                boxShadow: on
                  ? "inset 0 1px 0 rgba(255,255,255,0.4), inset 0 -1px 0 rgba(0,0,0,0.5), 0 0 6px rgba(0,229,255,0.65)"
                  : "inset 0 2px 3px rgba(0,0,0,0.7)",
              }}
              data-testid={`memory-gauge-seg-${i + 1}`}
              data-on={on ? "true" : "false"}
            >
              {/* rune slash */}
              <svg
                viewBox="0 0 12 16"
                className="absolute inset-0 w-full h-full opacity-70"
              >
                <path
                  d="M2 3 L10 8 M2 13 L10 8"
                  stroke={on ? "#0B120C" : "#363A36"}
                  strokeWidth="1"
                  fill="none"
                />
              </svg>
            </div>
          );
        })}
      </div>

      {/* Empowered label (only when full) */}
      {isFull && (
        <motion.span
          initial={{ opacity: 0, x: -6 }}
          animate={{ opacity: 1, x: 0 }}
          className="font-heading text-[10px] font-bold tracking-[0.22em] uppercase text-cyan-mist text-shadow-glow"
          data-testid="memory-gauge-empowered"
        >
          EMPOWERED
        </motion.span>
      )}
    </div>
  );
};
