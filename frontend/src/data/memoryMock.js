// ============================================================================
// THE single mock Cognee memory response. Everything the memory UI renders
// (shards, journal, recalled lines, gauge level) comes from THIS ONE OBJECT.
//
// Swap plan: replace `memoryMock` with the JSON returned by the FastAPI
// backend proxying Cognee, e.g.
//   const res = await fetch(`/api/memory/${playerId}`);
//   const memory = await res.json();   // same shape as below
// Nothing else in the UI changes.
// ============================================================================

export const memoryMock = {
  // What the boss remembers about the player — one card per fact.
  // type: "weakness" | "behavior" | "strength" | "event"
  shards: [
    {
      id: "shd-01",
      type: "weakness",
      title: "Weak topic: Arrays",
      detail: "3 past failures",
      source: "Zone 2, Level 14",
      weight: 0.82,
    },
    {
      id: "shd-02",
      type: "behavior",
      title: "Hesitates on timed questions",
      detail: "avg 9.2s per answer",
      source: "Zone 3, Level 22",
      weight: 0.71,
    },
    {
      id: "shd-03",
      type: "event",
      title: "Last encounter: fled at 20 HP",
      detail: "abandoned trial mid-fight",
      source: "Zone 4, Level 30",
      weight: 0.66,
    },
    {
      id: "shd-04",
      type: "strength",
      title: "Strong topic: Recursion",
      detail: "90% accuracy",
      source: "Zone 3, Level 27",
      weight: 0.93,
    },
  ],

  // The ECHOES journal — topic mastery + per-zone accuracy (0..1)
  journal: {
    mastered: [
      { topic: "Recursion", accuracy: 0.90 },
      { topic: "Loops", accuracy: 0.85 },
      { topic: "Strings", accuracy: 0.78 },
      { topic: "Hashmaps", accuracy: 0.74 },
    ],
    haunting: [
      { topic: "Arrays", accuracy: 0.40 },
      { topic: "Pointers", accuracy: 0.52 },
      { topic: "Trees", accuracy: 0.55 },
      { topic: "Graphs", accuracy: 0.58 },
    ],
    zoneAccuracy: [
      { id: 1, name: "Verdant Threshold", accuracy: 0.88 },
      { id: 2, name: "Whispering Vines", accuracy: 0.72 },
      { id: 3, name: "Sunken Cloister", accuracy: 0.61 },
      { id: 4, name: "Ember Chasm", accuracy: 0.44 },
      { id: 5, name: "Deity's Vault", accuracy: 0.0 },
    ],
  },

  // Boss lines generated from player history (memory_ref -> shard id)
  recalledLines: [
    {
      id: "rd-01",
      speaker: "boss",
      name: "Vashkar",
      text: "Arrays again, little flame? I remember every time they burned you.",
      memory_ref: "shd-01",
    },
    {
      id: "rd-02",
      speaker: "boss",
      name: "Vashkar",
      text: "You hesitate. Nine seconds, ten... the ruins have counted them all.",
      memory_ref: "shd-02",
    },
  ],

  // How much the boss has "learned" this fight (0..gaugeSegments)
  gaugeLevel: 2,
  gaugeSegments: 5,
};

export default memoryMock;
