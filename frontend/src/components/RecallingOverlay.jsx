import React from "react";
import { motion } from "framer-motion";

// Orbiting memory-rune glyph (SVG)
const OrbitRune = ({ angle, radius, size = 14 }) => {
  const x = Math.cos((angle * Math.PI) / 180) * radius;
  const y = Math.sin((angle * Math.PI) / 180) * radius;
  return (
    <svg
      className="absolute pointer-events-none"
      style={{
        left: `calc(50% + ${x}px - ${size / 2}px)`,
        top: `calc(50% + ${y}px - ${size / 2}px)`,
        width: size,
        height: size,
        filter: "drop-shadow(0 0 8px #00E5FF)",
      }}
      viewBox="0 0 16 16"
    >
      <circle cx="8" cy="8" r="6" stroke="#00E5FF" strokeWidth="1.2" fill="rgba(0,229,255,0.12)" />
      <path d="M8 2 L8 14 M2 8 L14 8 M4 4 L12 12 M12 4 L4 12" stroke="#00E5FF" strokeWidth="0.8" opacity="0.75" />
    </svg>
  );
};

// The RECALLING overlay — layered on top of the boss sprite.
// Provides: bright cyan pulse behind boss, inward mist rings, and 4 orbiting glyphs.
export const RecallingBossOverlay = ({ active = false }) => {
  if (!active) return null;
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="absolute inset-0 pointer-events-none"
      data-testid="boss-recalling-overlay"
    >
      {/* Inward-swirling cyan mist (behind boss) */}
      <motion.div
        animate={{ scale: [1.4, 1, 1.4], opacity: [0.3, 0.7, 0.3], rotate: [0, 90, 180] }}
        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 rounded-full"
        style={{
          background:
            "radial-gradient(circle, rgba(0,229,255,0.55) 0%, rgba(0,229,255,0.15) 50%, transparent 75%)",
          filter: "blur(20px)",
        }}
      />

      {/* Inner rune ring */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-40 h-40 rounded-full"
        style={{
          border: "1px solid rgba(0,229,255,0.6)",
          boxShadow: "0 0 24px rgba(0,229,255,0.55), inset 0 0 20px rgba(0,229,255,0.35)",
        }}
      />

      {/* 4 orbiting glyphs */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 6, repeat: Infinity, ease: "linear" }}
        className="absolute inset-0"
      >
        {[0, 90, 180, 270].map((a) => (
          <OrbitRune key={a} angle={a} radius={90} size={16} />
        ))}
      </motion.div>

      {/* Counter-rotating outer glyphs */}
      <motion.div
        animate={{ rotate: -360 }}
        transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
        className="absolute inset-0"
      >
        {[45, 135, 225, 315].map((a) => (
          <OrbitRune key={a} angle={a} radius={130} size={12} />
        ))}
      </motion.div>
    </motion.div>
  );
};

// Full-screen edge vignette pulse — dims edges to cyan while boss is RECALLING
export const RecallingVignette = ({ active = false }) => {
  if (!active) return null;
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: [0.3, 0.85, 0.3] }}
      exit={{ opacity: 0 }}
      transition={{ duration: 1.8, repeat: Infinity, ease: "easeInOut" }}
      className="absolute inset-0 pointer-events-none z-[45]"
      data-testid="recalling-vignette"
      style={{
        background:
          "radial-gradient(ellipse at center, transparent 45%, rgba(0,229,255,0.15) 75%, rgba(0,229,255,0.55) 100%)",
        mixBlendMode: "screen",
      }}
    />
  );
};
