# Dungeon of Recall — Live Demo Front-End

Welcome to the frontend application for the **Dungeon of Recall** hackathon project. This visual system contains interactive screens designed for high-impact live demos, visualizing how the AI boss adapts to players in real time.

## Quick Start (Run Locally)

From the project root directory, run these commands to install dependencies and run the development server:

```powershell
# Navigate to frontend directory
cd frontend

# Install package dependencies (D3, React 18, React-Router, Vite)
npm install

# Run the local development server
npm run dev
```

The application will be hosted at [http://localhost:5173](http://localhost:5173).

---

## Technical Architecture & Integration Handoff

To maintain clean architecture and support parallel work, **all backend and Cognee integrations have been isolated**. The rest of the codebase consumes data solely via React state context hooks and mock interface functions. 

Teammates working on the backend/RL models can easily swap mock integrations for live ones in **one single file**.

### 1. Integration Anchor File
All API requests and state mutations are defined in [mockData.js](file:///c:/Users/HP/Downloads/Projects/The-Algorithmic-Labyrinth/frontend/src/api/mockData.js). To plug in real endpoints, swap out the implementation of the functions marked with the comment `// SWAP: ...`.

### 2. State & Context Management
The UI consumes state via the `useGame()` custom context hook defined in [GameContext.jsx](file:///c:/Users/HP/Downloads/Projects/The-Algorithmic-Labyrinth/frontend/src/contexts/GameContext.jsx). It holds:
- `playerMemory`: Current weakness state.
- `floorState`: Current level completion map.
- `bossDialogue`: Current AI adaptive taunt statement.
- HP states (`bossHp`, `playerHp`).

### 3. API Handoff Contracts

#### **Topic Schema**
```typescript
interface Topic {
  id: string;                 // e.g. "dp", "arrays", "graphs", "trees", "sorting", "binary_search", "math"
  name: string;               // e.g. "Dynamic Programming"
  weakness_score: number;     // Float between 0.0 (mastered) and 1.0 (very weak)
  attempts: number;           // Total attempts made
  avg_time_sec: number;       // Average time to submit answer
  last_result: 'correct' | 'incorrect' | 'hint_used';
}
```

#### **PlayerMemory Schema**
```typescript
interface PlayerMemory {
  topics: Topic[];
  frustration_level: 'low' | 'medium' | 'high';
}
```

#### **API Endpoints to Map (inside [mockData.js](file:///c:/Users/HP/Downloads/Projects/The-Algorithmic-Labyrinth/frontend/src/api/mockData.js))**

| Function | HTTP Mapping | Description |
|---|---|---|
| `getPlayerMemory(playerId)` | `GET /api/memory/{playerId}` | Returns the boss's knowledge graph of the player's weak points. |
| `getFloorState(playerId)` | `GET /api/floors/{playerId}` | Returns what rooms are locked, current room, and if secret rift is unlocked. |
| `getQuestion(topic, difficulty)` | `GET /api/questions?topic={topic}&difficulty={diff}` | Returns active math/DSA question with answer and hints. |
| `getBossDialogue(weakTopicId)` | `POST /api/boss/dialogue` | Asks the LLM/dialogue engine for an adaptive taunt mentioning `weakTopicId`. |
| `recordAttempt(playerId, topic, result, time)` | `POST /api/memory/record` | Submits performance details. Backend updates the RL layer and Cognee memory. |
| `forgetMemory(playerId)` | `POST /api/memory/forget` | Triggered by potion drinking. Resets and clears the graph on backend. |

---

## UI Components Reference

- 🗺️ **Floor Map**: [FloorMap.jsx](file:///c:/Users/HP/Downloads/Projects/The-Algorithmic-Labyrinth/frontend/src/components/FloorMap.jsx) — Displays floor progression using SVG connectors that light up as you advance. Supports secret branching to the "Logic Rift".
- ❓ **Question Modal**: [QuestionModal.jsx](file:///c:/Users/HP/Downloads/Projects/The-Algorithmic-Labyrinth/frontend/src/components/QuestionModal.jsx) — Parchment scroll modal overlay with timer, hint mechanics, code/math panels, and red error-shake transitions.
- 👁️ **Boss Page**: [BossPage.jsx](file:///c:/Users/HP/Downloads/Projects/The-Algorithmic-Labyrinth/frontend/src/pages/BossPage.jsx) — Dual-pane boss fight layout. Includes rotating rune sigils and dynamic typing taunts.
- 🧠 **Memory Graph**: [MemoryGraph.jsx](file:///c:/Users/HP/Downloads/Projects/The-Algorithmic-Labyrinth/frontend/src/components/MemoryGraph.jsx) — Living D3 graph that automatically runs a pulse-ripple + flying particles along nodes when a teammate records progress, and launches a cyan desaturated shockwave radial wipe on potion usage.
