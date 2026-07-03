import React from "react";
import { motion } from "framer-motion";
import { Lock, Skull } from "lucide-react";

// A single glassmorphism level node
export const LevelNode = ({ level, onClick, isPreview = false }) => {
  const { num, status, isBoss } = level;
  const disabled = status === "locked";

  const label = isBoss ? "BOSS" : num;

  const classes = isBoss
    ? "node-boss"
    : status === "locked"
      ? "node-locked"
      : status === "completed"
        ? "node-completed"
        : status === "current"
          ? "node-current"
          : "node-unlocked";

  const testid = `level-node-${num}${isBoss ? "-boss" : ""}`;

  return (
    <motion.button
      type="button"
      whileHover={disabled ? {} : { scale: 1.08 }}
      whileTap={disabled ? {} : { scale: 0.94 }}
      initial={{ scale: 0.7, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: "spring", stiffness: 260, damping: 22 }}
      className={`node-base ${classes} ${status === "current" ? "animate-ember-pulse" : ""} ${status === "unlocked" && !isBoss ? "animate-glow-pulse" : ""}`}
      onClick={() => !disabled && onClick && onClick(level)}
      disabled={disabled}
      data-testid={testid}
      aria-label={`Level ${num}${isBoss ? " boss" : ""} — ${status}`}
    >
      {status === "locked" && !isBoss && (
        <Lock className="w-5 h-5 opacity-70" strokeWidth={2.5} />
      )}
      {isBoss && (
        <div className="flex flex-col items-center leading-none">
          <Skull className="w-6 h-6 mb-0.5" strokeWidth={2.5} />
          <span className="text-[9px] tracking-widest">{label}</span>
        </div>
      )}
      {!isBoss && status !== "locked" && (
        <span className="font-heading text-shadow-stone">{label}</span>
      )}

      {/* Current level ping */}
      {status === "current" && !isPreview && (
        <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-ember-orange animate-ping" />
      )}
    </motion.button>
  );
};

// Zone banner (5 zones)
export const ZoneBanner = ({ zone, index }) => (
  <div className="relative flex items-center gap-3 py-3 w-full max-w-[320px] mx-auto" data-testid={`zone-banner-${zone.id}`}>
    <div className="flex-1 h-px bg-gradient-to-r from-transparent to-cyan-mist/40" />
    <div
      className="carved-stone px-4 py-1.5 relative"
      style={{ backgroundImage: `linear-gradient(180deg, ${zone.color} 0%, #1E201E 100%)` }}
    >
      <div className="flex items-center gap-2">
        <span className="font-mono text-[9px] tracking-[0.3em] text-cyan-mist">
          ZONE {String(zone.id).padStart(2, "0")}
        </span>
      </div>
      <div className="font-display text-sm font-bold tracking-wider text-bone whitespace-nowrap">
        {zone.name}
      </div>
    </div>
    <div className="flex-1 h-px bg-gradient-to-l from-transparent to-cyan-mist/40" />
  </div>
);
