import React from "react";
import { motion } from "framer-motion";

// Ember particle drift (used inside dark backgrounds)
export const EmberParticles = ({ count = 14, className = "" }) => (
  <div className={`pointer-events-none absolute inset-0 overflow-hidden ${className}`}>
    {Array.from({ length: count }).map((_, i) => {
      const left = (i * 37) % 100;
      const delay = (i * 0.4) % 3.6;
      const size = 3 + (i % 3);
      return (
        <span
          key={i}
          className="absolute rounded-full bg-ember-orange animate-ember-drift"
          style={{
            left: `${left}%`,
            bottom: "-10px",
            width: size,
            height: size,
            boxShadow: "0 0 8px #FF6B35, 0 0 14px rgba(255,107,53,0.6)",
            animationDelay: `${delay}s`,
          }}
        />
      );
    })}
  </div>
);

// Slow horizontal cyan mist band
export const CyanMist = ({ className = "" }) => (
  <div
    className={`pointer-events-none absolute inset-0 animate-cyan-pan ${className}`}
    style={{
      backgroundImage:
        "linear-gradient(90deg, transparent 0%, rgba(0,229,255,0.10) 45%, rgba(0,229,255,0.18) 50%, rgba(0,229,255,0.10) 55%, transparent 100%)",
      backgroundSize: "200% 100%",
      mixBlendMode: "screen",
    }}
  />
);

// Volumetric light shaft (diagonal)
export const LightShaft = ({ style = {}, opacity = 0.18 }) => (
  <div
    className="pointer-events-none absolute"
    style={{
      background:
        "linear-gradient(180deg, rgba(0,229,255,0.35) 0%, rgba(0,229,255,0) 100%)",
      filter: "blur(24px)",
      opacity,
      transform: "skewX(-14deg)",
      ...style,
    }}
  />
);

// Rune-etched section divider with cyan mark
export const RuneDivider = ({ label }) => (
  <div className="flex items-center gap-3 my-4">
    <div className="flex-1 rune-divider" />
    {label && (
      <span className="font-mono text-[10px] tracking-[0.3em] uppercase text-cyan-mist/80">
        {label}
      </span>
    )}
    <div className="flex-1 rune-divider" />
  </div>
);

// Corner rune ornament (SVG)
export const CornerRune = ({ className = "", flip = false }) => (
  <svg
    viewBox="0 0 40 40"
    className={`${className} ${flip ? "scale-x-[-1]" : ""}`}
    style={{ overflow: "visible" }}
  >
    <path
      d="M2 2 L18 2 M2 2 L2 18 M2 10 L10 10 L10 2"
      stroke="#00E5FF"
      strokeWidth="1.5"
      fill="none"
      opacity="0.75"
    />
    <circle cx="10" cy="10" r="1.5" fill="#00E5FF" />
  </svg>
);

// Framed screen container (mobile device shell for desktop)
export const DeviceFrame = ({ children, testid }) => (
  <div className="device-frame" data-testid={testid}>{children}</div>
);

// Screen transitions
export const screenTransition = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -12 },
  transition: { duration: 0.35, ease: [0.22, 1, 0.36, 1] },
};

export const MotionScreen = ({ children, className = "", ...props }) => (
  <motion.div
    {...screenTransition}
    className={`relative w-full h-full ${className}`}
    {...props}
  >
    {children}
  </motion.div>
);
