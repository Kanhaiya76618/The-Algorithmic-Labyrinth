import React from "react";
import { motion } from "framer-motion";
import { Heart, Coins, Sparkles } from "lucide-react";

// Amber HP hearts row (5 hearts by default)
export const HeartsHUD = ({ hp = 3, max = 5, testid = "hud-hp" }) => (
  <div className="flex gap-1.5" data-testid={testid}>
    {Array.from({ length: max }).map((_, i) => (
      <motion.div
        key={i}
        initial={{ scale: 0.5, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: i * 0.05 }}
        className={`hp-gem ${i >= hp ? "hp-gem-empty" : ""}`}
        data-testid={`hud-hp-gem-${i + 1}`}
      />
    ))}
  </div>
);

// Vine XP bar with SVG twist
export const XPBar = ({ value = 60, level = 7, testid = "hud-xp" }) => (
  <div className="flex items-center gap-2 flex-1" data-testid={testid}>
    <div className="carved-stone px-1.5 py-0.5">
      <span className="font-heading text-[11px] font-bold text-ember-orange tracking-wider">
        Lv {level}
      </span>
    </div>
    <div className="vine-bar flex-1 h-3 relative">
      <div
        className="vine-bar-fill"
        style={{ width: `${value}%` }}
        data-testid="hud-xp-fill"
      />
      {/* twisting vine overlay */}
      <svg
        className="absolute inset-0 w-full h-full pointer-events-none"
        viewBox="0 0 100 12"
        preserveAspectRatio="none"
      >
        <path
          d="M0 6 Q 12 2, 25 6 T 50 6 T 75 6 T 100 6"
          fill="none"
          stroke="#0B120C"
          strokeWidth="0.8"
          opacity="0.6"
        />
      </svg>
    </div>
  </div>
);

// Relic coin counter
export const CoinCounter = ({ value = 128, testid = "hud-coins" }) => (
  <div
    className="carved-stone flex items-center gap-1.5 px-2.5 py-1"
    data-testid={testid}
  >
    <div className="relative">
      <Coins className="w-4 h-4 text-ember-gold drop-shadow-[0_0_6px_rgba(245,185,66,0.7)]" />
    </div>
    <span className="font-mono text-sm font-bold text-bone tabular-nums">
      {value}
    </span>
  </div>
);

// Star rating (used on victory + level completed)
export const StarRating = ({ stars = 3, max = 3, size = 24 }) => (
  <div className="flex gap-1.5">
    {Array.from({ length: max }).map((_, i) => (
      <motion.div
        key={i}
        initial={{ scale: 0, rotate: -180, opacity: 0 }}
        animate={{ scale: 1, rotate: 0, opacity: 1 }}
        transition={{ delay: i * 0.15, type: "spring", stiffness: 200 }}
        style={{ width: size, height: size }}
        data-testid={`star-${i + 1}`}
      >
        {i < stars ? (
          <svg viewBox="0 0 24 24" fill="#F5B942" stroke="#0B120C" strokeWidth="1.5"
            style={{ filter: "drop-shadow(0 0 8px rgba(245,185,66,0.85))" }}>
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
        ) : (
          <svg viewBox="0 0 24 24" fill="#1E201E" stroke="#4F554F" strokeWidth="1.5">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
        )}
      </motion.div>
    ))}
  </div>
);

// Full HUD strip for the level screen
export const HUD = ({ hp = 3, xp = 60, level = 7, coins = 128 }) => (
  <div
    className="glass-panel px-3 py-2 flex items-center gap-3"
    data-testid="hud-container"
  >
    <HeartsHUD hp={hp} />
    <XPBar value={xp} level={level} />
    <CoinCounter value={coins} />
  </div>
);
