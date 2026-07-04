// ============================================================
// DUNGEON OF RECALL — Chronicle Page / Leaderboard
// src/pages/ChroniclePage.jsx
// ============================================================
// Guild ledger record screen. Displays leaderboard stats of
// other challengers, highlighting the current active session.
// ============================================================

import React, { useState, useEffect } from 'react';
import { useGame } from '../contexts/GameContext';
import { getLeaderboard } from '../api/mockData';

export default function ChroniclePage() {
  const { playerId, floorState, playerMemory, bossHp } = useGame();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  // Compute live stats for the current player
  const floorsCleared = floorState?.clearedFloors?.length ?? 0;
  const currentFloor = floorState?.currentFloor ?? 1;
  const bossWins = bossHp <= 0 ? 1 : 0;

  // Calculate live overall mastery % (100 - average weakness %)
  let overallMastery = 50;
  if (playerMemory && playerMemory.topics.length > 0) {
    const totalWeakness = playerMemory.topics.reduce((acc, t) => acc + t.weakness_score, 0);
    const avgWeakness = totalWeakness / playerMemory.topics.length;
    overallMastery = Math.round((1 - avgWeakness) * 100);
  }

  useEffect(() => {
    let active = true;
    async function loadRecords() {
      setLoading(true);
      const stats = {
        floorsCleared,
        currentFloor,
        overallMastery,
        bossWins,
      };
      const leaderboard = await getLeaderboard(playerId, stats);
      if (active) {
        setRecords(leaderboard);
        setLoading(false);
      }
    }
    loadRecords();
    return () => {
      active = false;
    };
  }, [playerId, floorsCleared, currentFloor, overallMastery, bossWins]);

  if (loading) {
    return (
      <div className="chronicle-page">
        <div className="loading-rune">Consulting the Chronicler's ledger…</div>
      </div>
    );
  }

  return (
    <div className="chronicle-page">
      <header className="chronicle-header">
        <h2 className="chronicle-title">Chronicle of Labyrinth Runes</h2>
        <p className="chronicle-subtitle">Records of those who braved the memory-crawler</p>
      </header>

      <div className="chronicle-ledger">
        <table className="chronicle-table">
          <thead>
            <tr>
              <th style={{ width: '60px' }}>Rank</th>
              <th>Challenger</th>
              <th>Progress</th>
              <th>Current Floor</th>
              <th>Mastery Rate</th>
              <th>Boss Wins</th>
              <th>Memory Wipes</th>
            </tr>
          </thead>
          <tbody>
            {records.map((record, index) => {
              const isSelf = record.playerId === playerId;
              const isTop = index === 0;

              return (
                <tr
                  key={record.playerId}
                  className={`${isSelf ? 'chronicle-row-current' : ''} ${isTop ? 'chronicle-row-top' : ''}`}
                >
                  <td className={isTop ? 'gilt-text' : ''}>
                    {isTop ? '👑 I' : index + 1}
                  </td>
                  <td>
                    {record.playerId} {isSelf && <span className="current-indicator"> (You)</span>}
                  </td>
                  <td className={isTop ? 'gilt-text' : ''}>
                    {record.floorsCleared} / {record.totalFloors}
                  </td>
                  <td>
                    Floor {record.currentFloor}
                  </td>
                  <td className={isTop ? 'gilt-text' : ''} style={{ fontFamily: 'var(--font-mono)' }}>
                    {record.masteryPercent}%
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>
                    {record.bossWins}
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', color: record.potionUses > 0 ? 'var(--cognition-glow)' : 'var(--bone-dim)' }}>
                    {record.potionUses}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
