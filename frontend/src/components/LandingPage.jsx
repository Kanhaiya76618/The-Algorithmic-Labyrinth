// ============================================================
// DUNGEON OF RECALL — Landing Page / Title Screen
// src/components/LandingPage.jsx
// ============================================================
// The thematic entry page of the game. Collects player ID
// and displays atmospheric copy with drifting particles.
// ============================================================

import React, { useState } from 'react';

export default function LandingPage({ onStart }) {
  const [name, setName] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    onStart(name.trim());
  };

  // Generate 25 drifting particles at random initial positions, delays and durations
  const particles = Array.from({ length: 25 }).map((_, i) => {
    const left = Math.random() * 100; // %
    const delay = Math.random() * 10; // seconds
    const duration = 10 + Math.random() * 10; // seconds
    const scale = 0.5 + Math.random() * 1.5;
    return (
      <div
        key={i}
        className="drifting-particle"
        style={{
          left: `${left}%`,
          animationDelay: `${delay}s`,
          animationDuration: `${duration}s`,
          transform: `scale(${scale})`,
        }}
      />
    );
  });

  return (
    <div className="landing-page">
      {/* Drifting particle ember field */}
      <div className="particles-container">
        {particles}
      </div>

      <div className="landing-content">
        <header className="landing-header">
          <h1 className="landing-title">Dungeon of Recall</h1>
          <p className="landing-subtitle">A dungeon that remembers you.</p>
        </header>

        <p className="landing-copy">
          "The stones here do not just watch; they listen, learn, and whisper of your failures.
          To conquer Cognee is to master your own mind... or watch your flaws materialize in the dark."
        </p>

        <form onSubmit={handleSubmit} className="landing-form">
          <div className="input-group">
            <label htmlFor="playerIdInput" className="input-label">Identify Thyself</label>
            <input
              id="playerIdInput"
              type="text"
              className="landing-input"
              placeholder="e.g. Knight_of_Recursion"
              value={name}
              onChange={(e) => setName(e.target.value)}
              maxLength={20}
              required
              autoFocus
            />
          </div>

          <button type="submit" className="btn-blood" disabled={!name.trim()}>
            Begin Descent
          </button>
        </form>
      </div>
    </div>
  );
}
