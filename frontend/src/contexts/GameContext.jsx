// ============================================================
// DUNGEON OF RECALL — Game Context
// src/contexts/GameContext.jsx
// ============================================================
// Central state store for all game state.
// All UI components consume state and actions via useGame().
// All data mutations go through the mock API functions below —
// teammates swap those function bodies, not this file.
// ============================================================

import {
  createContext,
  useContext,
  useReducer,
  useEffect,
  useCallback,
  useState,
} from 'react';

import {
  getPlayerMemory,
  getFloorState,
  getBossDialogue,
  forgetMemory,
  recordAttempt,
  clearFloor,
} from '../api/mockData';

// ──────────────────────────────────────────────────────────────
// Constants
// ──────────────────────────────────────────────────────────────
// SWAP: replace with real player auth/session ID
const PLAYER_ID = 'player_001';

// Floor → topic mapping for question selection
// SWAP: fetch this from the backend question-bank config
export const FLOOR_TOPIC_MAP = {
  1: 'arrays',
  2: 'sorting',
  3: 'trees',
  4: 'graphs',
  5: 'binary_search',
  6: 'dp', // Boss floor — overridden by weakest topic if available
};

export const FLOOR_DIFFICULTY_MAP = {
  1: 'easy',
  2: 'easy',
  3: 'medium',
  4: 'medium',
  5: 'medium',
  6: 'hard',
};

// ──────────────────────────────────────────────────────────────
// Reducer
// ──────────────────────────────────────────────────────────────
const initialState = {
  playerId: null, // Starts as null to trigger the Title screen
  playerMemory: null,
  floorState: null,
  bossDialogue: '',
  bossHp: 5,
  playerHp: 5,
  isForgetAnimating: false,
  isLoading: false, // Don't block loading when playerId is not set yet
  lastUpdatedTopic: null, // topic ID that just changed — drives graph animation
  graphKey: 0,            // increment to force MemoryGraph remount after forget
};

function reducer(state, action) {
  switch (action.type) {
    case 'SET_PLAYER_ID':
      return { ...state, playerId: action.payload, isLoading: true };

    case 'LOAD_MEMORY':
      return { ...state, playerMemory: action.payload, isLoading: false };

    case 'LOAD_FLOOR_STATE':
      return { ...state, floorState: action.payload };

    case 'UPDATE_MEMORY':
      return {
        ...state,
        playerMemory: action.payload.memory,
        lastUpdatedTopic: action.payload.topicId,
      };

    case 'SET_BOSS_DIALOGUE':
      return { ...state, bossDialogue: action.payload };

    case 'BOSS_TAKE_DAMAGE':
      return { ...state, bossHp: Math.max(0, state.bossHp - 1) };

    case 'PLAYER_TAKE_DAMAGE':
      return { ...state, playerHp: Math.max(0, state.playerHp - 1) };

    case 'START_FORGET':
      return { ...state, isForgetAnimating: true };

    case 'COMPLETE_FORGET':
      return {
        ...state,
        isForgetAnimating: false,
        playerMemory: action.payload,
        lastUpdatedTopic: null,
        graphKey: state.graphKey + 1, // remount MemoryGraph with fresh data
        bossDialogue: '',
      };

    case 'UPDATE_FLOOR_STATE':
      return { ...state, floorState: action.payload };

    case 'CLEAR_TOPIC_UPDATE':
      return { ...state, lastUpdatedTopic: null };

    default:
      return state;
  }
}

// ──────────────────────────────────────────────────────────────
// Context & Provider
// ──────────────────────────────────────────────────────────────
const GameContext = createContext(null);

export function GameProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  // ── Initial/On-Change data load ────────────────────────────────────────
  useEffect(() => {
    if (!state.playerId) return;
    async function bootstrap() {
      const [memory, floors] = await Promise.all([
        getPlayerMemory(state.playerId),
        getFloorState(state.playerId),
      ]);
      dispatch({ type: 'LOAD_MEMORY', payload: memory });
      dispatch({ type: 'LOAD_FLOOR_STATE', payload: floors });
    }
    bootstrap();
  }, [state.playerId]);

  // ── Load boss dialogue whenever memory refreshes ─────────────
  useEffect(() => {
    if (!state.playerMemory) return;
    const sorted = [...state.playerMemory.topics].sort(
      (a, b) => b.weakness_score - a.weakness_score,
    );
    const weakest = sorted[0];
    getBossDialogue(weakest?.id ?? 'default').then((line) => {
      dispatch({ type: 'SET_BOSS_DIALOGUE', payload: line });
    });
  }, [state.playerMemory]);

  // ── Actions ──────────────────────────────────────────────────

  /** Set player ID and trigger state bootstrap */
  const startSession = useCallback((id) => {
    dispatch({ type: 'SET_PLAYER_ID', payload: id });
  }, []);

  /** Record a question attempt and update memory graph */
  const handleRecordAttempt = useCallback(async (topicId, result, timeSec) => {
    if (!state.playerId) return null;
    const updatedMemory = await recordAttempt(state.playerId, topicId, result, timeSec);
    dispatch({ type: 'UPDATE_MEMORY', payload: { memory: updatedMemory, topicId } });
    // Clear lastUpdatedTopic after a short delay so animation can re-trigger later
    setTimeout(() => dispatch({ type: 'CLEAR_TOPIC_UPDATE' }), 1200);
    return updatedMemory;
  }, [state.playerId]);

  /** Trigger the full forget() sequence — animation-aware */
  const handleForget = useCallback(async () => {
    if (state.isForgetAnimating || !state.playerId) return; // prevent double-trigger
    dispatch({ type: 'START_FORGET' });

    // Let the forget animation run (1.8s) before resetting data
    await forgetMemory(state.playerId);
    setTimeout(async () => {
      const freshMemory = await getPlayerMemory(state.playerId);
      dispatch({ type: 'COMPLETE_FORGET', payload: freshMemory });
    }, 1800);
  }, [state.isForgetAnimating, state.playerId]);

  /** Boss takes a hit (player answered correctly) */
  const handleBossHit = useCallback(() => {
    dispatch({ type: 'BOSS_TAKE_DAMAGE' });
  }, []);

  /** Player takes a hit (player answered incorrectly) */
  const handlePlayerHit = useCallback(() => {
    dispatch({ type: 'PLAYER_TAKE_DAMAGE' });
  }, []);

  /** Mark a floor as cleared and unlock the next */
  const handleClearFloor = useCallback(async (floorId) => {
    if (!state.playerId) return;
    const newFloorState = await clearFloor(state.playerId, floorId);
    dispatch({ type: 'UPDATE_FLOOR_STATE', payload: newFloorState });
    dispatch({ type: 'BOSS_TAKE_DAMAGE' }); // each cleared floor damages boss
  }, [state.playerId]);

  // ── Derived values ───────────────────────────────────────────
  const weakestTopic = state.playerMemory
    ? [...state.playerMemory.topics].sort((a, b) => b.weakness_score - a.weakness_score)[0]
    : null;

  const strongestTopic = state.playerMemory
    ? [...state.playerMemory.topics].sort((a, b) => a.weakness_score - b.weakness_score)[0]
    : null;

  const frustration_level = state.playerMemory?.frustration_level || 'low';

  return (
    <GameContext.Provider
      value={{
        ...state,
        weakestTopic,
        strongestTopic,
        frustration_level,
        startSession,
        handleRecordAttempt,
        handleForget,
        handleBossHit,
        handlePlayerHit,
        handleClearFloor,
      }}
    >
      {children}
    </GameContext.Provider>
  );
}

/** Hook — call inside any component wrapped by GameProvider */
export function useGame() {
  const ctx = useContext(GameContext);
  if (!ctx) throw new Error('useGame must be called inside <GameProvider>');
  return ctx;
}
