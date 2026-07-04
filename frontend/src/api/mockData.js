// ============================================================
// DUNGEON OF RECALL — MOCK DATA LAYER
// src/api/mockData.js
// ============================================================
// ALL data-fetching is isolated here.
// To integrate real APIs, replace the function bodies below.
// UI components must NEVER hardcode mock values — always call
// these functions through the GameContext hook.
//
// TEAMMATE HANDOFF CONTRACT:
// ─────────────────────────────────────────────────────────────
//  getPlayerMemory(playerId)               → Promise<PlayerMemory>
//  getFloorState(playerId)                 → Promise<FloorState>
//  getQuestion(topic, difficulty)          → Promise<Question>
//  getBossDialogue(weakTopicId)            → Promise<string>
//  forgetMemory(playerId)                  → Promise<{ success: boolean }>
//  recordAttempt(playerId, topicId, result, timeSec) → Promise<PlayerMemory>
//
// PlayerMemory shape:
//   { topics: Topic[], frustration_level: 'low'|'medium'|'high' }
//
// Topic shape:
//   { id, name, weakness_score (0–1), attempts, avg_time_sec,
//     last_result: 'correct'|'incorrect'|'hint_used' }
//
// FloorState shape:
//   { currentFloor, totalFloors, clearedFloors[], lockedFloors[],
//     hasSecretPath, secretPathUnlocked }
//
// Question shape:
//   { id, topic, difficulty, title, body, type, placeholder,
//     answer, hint, time_limit_sec }
// ============================================================

// ──────────────────────────────────────────────────────────────
// Internal mutable state (simulates backend KV store / DB)
// SWAP: replace _playerMemory reads/writes with real API calls
// ──────────────────────────────────────────────────────────────
let _playerMemory = {
  topics: [
    // Simulated player: very weak on DP, strong on arrays/sorting
    {
      id: 'dp',
      name: 'Dynamic Programming',
      weakness_score: 0.88,
      attempts: 3,
      avg_time_sec: 87,
      last_result: 'incorrect',
    },
    {
      id: 'arrays',
      name: 'Arrays',
      weakness_score: 0.18,
      attempts: 8,
      avg_time_sec: 22,
      last_result: 'correct',
    },
    {
      id: 'graphs',
      name: 'Graphs',
      weakness_score: 0.72,
      attempts: 4,
      avg_time_sec: 61,
      last_result: 'hint_used',
    },
    {
      id: 'binary_search',
      name: 'Binary Search',
      weakness_score: 0.38,
      attempts: 6,
      avg_time_sec: 30,
      last_result: 'correct',
    },
    {
      id: 'trees',
      name: 'Trees',
      weakness_score: 0.62,
      attempts: 3,
      avg_time_sec: 55,
      last_result: 'hint_used',
    },
    {
      id: 'sorting',
      name: 'Sorting',
      weakness_score: 0.12,
      attempts: 11,
      avg_time_sec: 15,
      last_result: 'correct',
    },
    {
      id: 'math',
      name: 'Math / Logic',
      weakness_score: 0.55,
      attempts: 5,
      avg_time_sec: 48,
      last_result: 'incorrect',
    },
  ],
  frustration_level: 'medium',
};

// Snapshot for reset on forgetMemory()
const _initialMemorySnapshot = JSON.stringify(_playerMemory);

let _floorState = {
  currentFloor: 3,
  totalFloors: 6,
  clearedFloors: [1, 2],
  lockedFloors: [4, 5, 6],
  hasSecretPath: true,
  secretPathUnlocked: false,
};

// Simulate network latency (ms) — remove or reduce for real API
const MOCK_DELAY = 120;
const delay = (ms) => new Promise((res) => setTimeout(res, ms));

// ══════════════════════════════════════════════════════════════
// PUBLIC API FUNCTIONS — swap bodies for real HTTP calls
// ══════════════════════════════════════════════════════════════

/**
 * Returns the Boss's current memory graph of the player.
 * SWAP: GET /api/memory/{playerId}
 */
export async function getPlayerMemory(playerId) {
  await delay(MOCK_DELAY);
  console.log(`[MockAPI] getPlayerMemory(${playerId})`);
  return JSON.parse(JSON.stringify(_playerMemory)); // deep clone
}

/**
 * Returns current floor progression state.
 * SWAP: GET /api/floors/{playerId}
 */
export async function getFloorState(playerId) {
  await delay(MOCK_DELAY);
  console.log(`[MockAPI] getFloorState(${playerId})`);
  return { ..._floorState };
}

/**
 * Returns a question for the given topic and difficulty.
 * SWAP: GET /api/questions?topic=&difficulty=&player_id=
 */
export async function getQuestion(topic, difficulty = 'medium') {
  await delay(MOCK_DELAY);
  console.log(`[MockAPI] getQuestion(${topic}, ${difficulty})`);
  const topicBank = QUESTION_BANK[topic] ?? QUESTION_BANK['arrays'];
  const pool = topicBank[difficulty] ?? topicBank['medium'] ?? topicBank['easy'];
  if (!pool || pool.length === 0) return FALLBACK_QUESTION;
  return { ...pool[Math.floor(Math.random() * pool.length)] };
}

/**
 * Returns an adaptive boss taunt line based on the player's weakest topic.
 * SWAP: POST /api/boss/dialogue  body: { player_id, weak_topic_id }
 */
export async function getBossDialogue(weakTopicId) {
  await delay(MOCK_DELAY);
  console.log(`[MockAPI] getBossDialogue(${weakTopicId})`);
  const lines = BOSS_DIALOGUES[weakTopicId] ?? BOSS_DIALOGUES['default'];
  return lines[Math.floor(Math.random() * lines.length)];
}

let _potionUsesCount = 0;

/**
 * Wipes the Boss's memory of the player. Resets all weakness scores to initial.
 * SWAP: POST /api/memory/{playerId}/forget
 */
export async function forgetMemory(playerId) {
  await delay(300); // slightly longer for dramatic weight
  console.log(`[MockAPI] forgetMemory(${playerId}) — ALL MEMORY ERASED`);
  _playerMemory = JSON.parse(_initialMemorySnapshot);
  _potionUsesCount += 1;
  return { success: true };
}

/**
 * Returns the leaderboard containing players records.
 * SWAP: GET /api/leaderboard
 */
export async function getLeaderboard(currentPlayerId, currentPlayerStats) {
  await delay(MOCK_DELAY);
  console.log(`[MockAPI] getLeaderboard(${currentPlayerId})`);

  const mockRecords = [
    {
      playerId: 'Xardas_DSA',
      floorsCleared: 5,
      totalFloors: 6,
      currentFloor: 6,
      masteryPercent: 88,
      bossWins: 3,
      potionUses: 1
    },
    {
      playerId: 'ByteCorruptor',
      floorsCleared: 4,
      totalFloors: 6,
      currentFloor: 5,
      masteryPercent: 74,
      bossWins: 1,
      potionUses: 0
    },
    {
      playerId: 'RecursionQueen',
      floorsCleared: 3,
      totalFloors: 6,
      currentFloor: 4,
      masteryPercent: 62,
      bossWins: 0,
      potionUses: 2
    },
    {
      playerId: 'NullPointerKnight',
      floorsCleared: 1,
      totalFloors: 6,
      currentFloor: 2,
      masteryPercent: 41,
      bossWins: 0,
      potionUses: 4
    },
    {
      playerId: 'AlgorithmicAcolyte',
      floorsCleared: 0,
      totalFloors: 6,
      currentFloor: 1,
      masteryPercent: 15,
      bossWins: 0,
      potionUses: 0
    }
  ];

  // Merge the active player's record
  const activeRecord = {
    playerId: currentPlayerId,
    floorsCleared: currentPlayerStats?.floorsCleared ?? 0,
    totalFloors: 6,
    currentFloor: currentPlayerStats?.currentFloor ?? 1,
    masteryPercent: Math.round(currentPlayerStats?.overallMastery ?? 50),
    bossWins: currentPlayerStats?.bossWins ?? 0,
    potionUses: _potionUsesCount
  };

  const allRecords = [activeRecord, ...mockRecords];
  // Sort by floors cleared descending, then mastery % descending
  allRecords.sort((a, b) => {
    if (b.floorsCleared !== a.floorsCleared) {
      return b.floorsCleared - a.floorsCleared;
    }
    return b.masteryPercent - a.masteryPercent;
  });

  return allRecords;
}


/**
 * Records the result of a player's attempt and adjusts weakness scores.
 * Returns the updated PlayerMemory.
 * SWAP: POST /api/memory/{playerId}/record
 *       body: { topic_id, result, time_sec }
 */
export async function recordAttempt(playerId, topicId, result, timeSec) {
  await delay(MOCK_DELAY);
  console.log(`[MockAPI] recordAttempt(${playerId}, ${topicId}, ${result}, ${timeSec}s)`);

  const topic = _playerMemory.topics.find((t) => t.id === topicId);
  if (!topic) return JSON.parse(JSON.stringify(_playerMemory));

  // Reinforcement learning deltas for weakness_score
  const delta = { correct: -0.12, incorrect: +0.15, hint_used: +0.05 }[result] ?? 0;
  topic.weakness_score = Math.max(0, Math.min(1, topic.weakness_score + delta));
  topic.attempts += 1;
  topic.avg_time_sec = Math.round(
    (topic.avg_time_sec * (topic.attempts - 1) + timeSec) / topic.attempts,
  );
  topic.last_result = result;

  // Recompute frustration level
  const avgWeakness =
    _playerMemory.topics.reduce((s, t) => s + t.weakness_score, 0) /
    _playerMemory.topics.length;
  _playerMemory.frustration_level =
    avgWeakness > 0.65 ? 'high' : avgWeakness > 0.4 ? 'medium' : 'low';

  return JSON.parse(JSON.stringify(_playerMemory));
}

/**
 * Marks a floor as cleared and unlocks the next one.
 * SWAP: POST /api/floors/{playerId}/clear  body: { floor_id }
 */
export async function clearFloor(playerId, floorId) {
  await delay(MOCK_DELAY);
  console.log(`[MockAPI] clearFloor(${playerId}, ${floorId})`);
  if (!_floorState.clearedFloors.includes(floorId)) {
    _floorState.clearedFloors.push(floorId);
  }
  _floorState.lockedFloors = _floorState.lockedFloors.filter((f) => f !== floorId + 1);
  if (_floorState.currentFloor === floorId) {
    _floorState.currentFloor = floorId + 1;
  }
  // Unlock secret path after clearing floor 3
  if (floorId >= 3) _floorState.secretPathUnlocked = true;
  return { ..._floorState };
}

// ══════════════════════════════════════════════════════════════
// STATIC CONTENT — question bank and boss dialogues
// SWAP: serve from CMS / LLM generation
// ══════════════════════════════════════════════════════════════

const QUESTION_BANK = {
  dp: {
    easy: [
      {
        id: 'dp-e-1',
        topic: 'dp',
        difficulty: 'easy',
        title: 'Climbing Stairs',
        body: 'You are climbing a staircase. It takes n steps to reach the top.\nEach time you can either climb 1 or 2 steps.\nIn how many distinct ways can you climb n = 5 steps to the top?',
        type: 'numeric',
        placeholder: 'Enter a number…',
        answer: '8',
        hint: 'Think Fibonacci. f(n) = f(n-1) + f(n-2),  f(1)=1, f(2)=2',
        time_limit_sec: 90,
      },
    ],
    medium: [
      {
        id: 'dp-m-1',
        topic: 'dp',
        difficulty: 'medium',
        title: 'Coin Change',
        body: 'Given coins = [1, 5, 11] and amount = 15,\nfind the MINIMUM number of coins needed to reach the amount.\n\nReturn -1 if impossible.',
        type: 'numeric',
        placeholder: 'Minimum coins…',
        answer: '3',
        hint: 'Bottom-up DP: dp[i] = min(dp[i - coin] + 1) for each coin where coin ≤ i.',
        time_limit_sec: 120,
      },
      {
        id: 'dp-m-2',
        topic: 'dp',
        difficulty: 'medium',
        title: 'Longest Common Subsequence',
        body: 'What is the length of the longest common subsequence\nbetween s1 = "abcde" and s2 = "ace"?',
        type: 'numeric',
        placeholder: 'LCS length…',
        answer: '3',
        hint: 'Build a 2D DP table. dp[i][j] = dp[i-1][j-1]+1 if s1[i]==s2[j].',
        time_limit_sec: 120,
      },
    ],
    hard: [
      {
        id: 'dp-h-1',
        topic: 'dp',
        difficulty: 'hard',
        title: 'Edit Distance',
        body: 'What is the minimum edit distance (insert/delete/substitute)\nbetween "intention" and "execution"?',
        type: 'numeric',
        placeholder: 'Edit distance…',
        answer: '5',
        hint: 'Classic Levenshtein. Consider all 3 operations at each dp[i][j] cell.',
        time_limit_sec: 150,
      },
    ],
  },
  arrays: {
    easy: [
      {
        id: 'arr-e-1',
        topic: 'arrays',
        difficulty: 'easy',
        title: 'Maximum Subarray',
        body: 'Find the sum of the contiguous subarray with the largest sum:\n\nnums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]',
        type: 'numeric',
        placeholder: 'Maximum sum…',
        answer: '6',
        hint: 'Kadane\'s algorithm: track currentMax and globalMax as you iterate.',
        time_limit_sec: 90,
      },
    ],
    medium: [
      {
        id: 'arr-m-1',
        topic: 'arrays',
        difficulty: 'medium',
        title: 'Two Sum',
        body: 'Given nums = [2, 7, 11, 15] and target = 9,\nreturn the indices of the two numbers that add up to target.\n\nAnswer format: "i,j" (smaller index first, no spaces)',
        type: 'text',
        placeholder: 'e.g. 0,1',
        answer: '0,1',
        hint: 'Use a hash map to store each value → index as you iterate.',
        time_limit_sec: 90,
      },
    ],
  },
  graphs: {
    medium: [
      {
        id: 'gr-m-1',
        topic: 'graphs',
        difficulty: 'medium',
        title: 'Number of Islands',
        body: 'Count the number of islands in this grid\n(1 = land, 0 = water):\n\n  1 1 0 0 0\n  1 1 0 0 0\n  0 0 1 0 0\n  0 0 0 1 1',
        type: 'numeric',
        placeholder: 'Number of islands…',
        answer: '3',
        hint: 'BFS/DFS from each unvisited land cell, marking all connected land as visited.',
        time_limit_sec: 120,
      },
    ],
    hard: [
      {
        id: 'gr-h-1',
        topic: 'graphs',
        difficulty: 'hard',
        title: 'Shortest Path (Dijkstra)',
        body: 'In a weighted graph, edges:\n  A→B=4, A→C=2, B→D=3, C→B=1, C→D=5\n\nWhat is the shortest path cost from A to D?',
        type: 'numeric',
        placeholder: 'Shortest cost…',
        answer: '6',
        hint: 'Dijkstra: A→C(2)→B(3)→D(6). Check all paths.',
        time_limit_sec: 150,
      },
    ],
  },
  trees: {
    medium: [
      {
        id: 'tree-m-1',
        topic: 'trees',
        difficulty: 'medium',
        title: 'Max Depth of Binary Tree',
        body: 'What is the maximum depth of this binary tree?\n\n          3\n         / \\\n        9  20\n          /  \\\n         15   7',
        type: 'numeric',
        placeholder: 'Max depth…',
        answer: '3',
        hint: 'max_depth(node) = 1 + max(max_depth(left), max_depth(right))',
        time_limit_sec: 90,
      },
    ],
  },
  binary_search: {
    medium: [
      {
        id: 'bs-m-1',
        topic: 'binary_search',
        difficulty: 'medium',
        title: 'Search Insert Position',
        body: 'Given the sorted array [1, 3, 5, 6] and target = 5,\nreturn the index where target is found or would be inserted.',
        type: 'numeric',
        placeholder: 'Index…',
        answer: '2',
        hint: 'Standard binary search. If not found, low pointer is the insert position.',
        time_limit_sec: 90,
      },
    ],
  },
  sorting: {
    easy: [
      {
        id: 'sort-e-1',
        topic: 'sorting',
        difficulty: 'easy',
        title: 'Merge Sort Passes',
        body: 'How many comparison passes does merge sort make\nto sort an array of n = 8 elements?\n\n(Hint: think in terms of log₂)',
        type: 'numeric',
        placeholder: 'Number of passes…',
        answer: '3',
        hint: 'Merge sort has O(log n) levels. log₂(8) = 3.',
        time_limit_sec: 60,
      },
    ],
  },
  math: {
    medium: [
      {
        id: 'math-m-1',
        topic: 'math',
        difficulty: 'medium',
        title: 'GCD via Euclid',
        body: 'What is the GCD of 252 and 105?\n\nApply the Euclidean algorithm step-by-step.',
        type: 'numeric',
        placeholder: 'GCD…',
        answer: '21',
        hint: 'Euclid: gcd(252,105)=gcd(105,42)=gcd(42,21)=gcd(21,0)=21',
        time_limit_sec: 90,
      },
    ],
  },
};

const FALLBACK_QUESTION = {
  id: 'fallback-1',
  topic: 'math',
  difficulty: 'easy',
  title: 'The Dungeon Toll',
  body: 'The dungeon keeper charges a toll.\nIf you have 144 gold and must split it equally among 12 adventurers,\nhow much does each receive?',
  type: 'numeric',
  placeholder: 'Gold per adventurer…',
  answer: '12',
  hint: 'Simple division: 144 ÷ 12',
  time_limit_sec: 60,
};

const BOSS_DIALOGUES = {
  dp: [
    "Dynamic Programming again… you never learn from memoization, do you? I remember every failed recursion.",
    "Your subproblems cascade into chaos. Every failed table entry is etched in my memory.",
    "State transitions confuse you. I've watched you get lost in the same DP table three times now.",
    "Overlapping subproblems are your weakness. The dungeon remembers what you so desperately try to forget.",
  ],
  graphs: [
    "Your graph traversal leaves cycles in its wake. I've traced every dead end you've walked.",
    "BFS or DFS? You always hesitate at the choice. That hesitation is my weapon.",
    "The nodes remember where you've been… and so do I. Every wrong path is catalogued.",
    "Your path-finding algorithm is circular. Fitting, for a mind that keeps running in loops.",
  ],
  trees: [
    "You prune incorrectly. Every wrong recursion branch is etched in my memory graph.",
    "The root of your problems… is that you can never quite find the root.",
    "Binary trees haunt you. I have memorized every wrong branch you've ever taken.",
    "You confuse inorder with preorder. I haven't forgotten — even if you have.",
  ],
  math: [
    "Numbers betray you when you rush. I've timed every calculation, every stumble.",
    "Mathematics is cold and exact. Unlike your guesses, which are warm and wrong.",
    "Your logical leaps… land short. Every time. I know this pattern intimately now.",
    "You second-guess your arithmetic. I have never second-guessed a single thing about you.",
  ],
  arrays: [
    "Off-by-one errors. Predictable. Exploitable. Exactly as I predicted.",
    "Two pointers confuse you? Fascinating. Let's probe that weakness further.",
    "You've mastered this… but I've set a different kind of trap entirely.",
  ],
  binary_search: [
    "You forget to adjust the right boundary. I remember it happening twice.",
    "Logarithmic complexity should be your ally. Instead, it belongs to me.",
    "Your mid-point calculation overflows. Small mistake. Enormous consequence. Sound familiar?",
  ],
  sorting: [
    "Sorting is your strong suit. So I've laid an entirely different kind of trap.",
    "You think you're safe on this ground. Confidence is a vulnerability too.",
  ],
  default: [
    "I have studied your patterns. Every hesitation. Every hint. Every wrong answer. I remember them all.",
    "The dungeon never forgets. Neither do I. That is not a threat — it is simply a fact.",
    "You cannot hide your weaknesses from a mind that never sleeps and never forgives.",
    "I remember you. Every choice you've made in this dungeon has been leading here.",
    "Your performance history is written in the connections of my memory. Come — let me show you what I know.",
  ],
};
