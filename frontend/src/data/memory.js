// Memory-system view layer: type styling + derived views over the ONE mock
// API object in ./memoryMock.js. Components import from here; the data itself
// lives in memoryMock.js and will be replaced by real Cognee fetches.

import memoryMock from "./memoryMock";

// Presentation config (NOT API data): rune icon + accent per shard type.
export const MEMORY_SHARD_TYPES = {
  weakness: {
    label: "Weakness",
    accent: "#FF6B35",
    ring: "rgba(255,107,53,0.55)",
    glow: "rgba(255,107,53,0.35)",
    icon: "target",
  },
  behavior: {
    label: "Behavior",
    accent: "#00E5FF",
    ring: "rgba(0,229,255,0.55)",
    glow: "rgba(0,229,255,0.35)",
    icon: "activity",
  },
  strength: {
    label: "Strength",
    accent: "#7CE38B",
    ring: "rgba(124,227,139,0.55)",
    glow: "rgba(124,227,139,0.35)",
    icon: "shield",
  },
  event: {
    label: "Event",
    accent: "#F5B942",
    ring: "rgba(245,185,66,0.55)",
    glow: "rgba(245,185,66,0.3)",
    icon: "history",
  },
};

// Boss identity — later populated by Cognee agent config
export const BOSS_IDENTITY = {
  name: "VASHKAR",
  title: "Stone Deity",
  memory_source: "cognee.memory.v1",
};

// ---- Derived views over the single mock response ----

export const MEMORY_SHARDS = memoryMock.shards;

export const RECALLED_DIALOGUE = memoryMock.recalledLines;

export const ECHOES_JOURNAL = {
  mastered: memoryMock.journal.mastered,
  haunting: memoryMock.journal.haunting,
  zones: memoryMock.journal.zoneAccuracy,
};

export const MEMORY_GAUGE = {
  segments: memoryMock.gaugeSegments,
  filled: memoryMock.gaugeLevel,
};

// Empty-state placeholder for a fresh player
export const EMPTY_MEMORY_MESSAGE = "No shards yet — the dungeon hasn't learned you.";
