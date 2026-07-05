import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Trophy, Medal, Brain, Compass, Activity, Award } from "lucide-react";
import { getLeaderboard } from "../api/client";
import { EmberParticles, MotionScreen, RuneDivider, CyanMist } from "../components/Atmosphere";

export default function LeaderboardScreen() {
  const navigate = useNavigate();
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await getLeaderboard();
        setEntries(data || []);
      } catch (err) {
        console.error("Failed to load leaderboard:", err);
        setError("Failed to fetch high scores from the dungeon.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const getRankBadge = (rank) => {
    if (rank === 1) {
      return (
        <div className="w-6 h-6 rounded-full bg-yellow-500/20 border border-yellow-500 flex items-center justify-center shadow-lg shadow-yellow-500/10">
          <Trophy className="w-3.5 h-3.5 text-yellow-500 animate-glow-pulse" />
        </div>
      );
    }
    if (rank === 2) {
      return (
        <div className="w-6 h-6 rounded-full bg-slate-300/20 border border-slate-300 flex items-center justify-center">
          <Medal className="w-3.5 h-3.5 text-slate-300" />
        </div>
      );
    }
    if (rank === 3) {
      return (
        <div className="w-6 h-6 rounded-full bg-amber-600/20 border border-amber-600 flex items-center justify-center">
          <Award className="w-3.5 h-3.5 text-amber-600" />
        </div>
      );
    }
    return (
      <span className="font-mono text-xs text-stone-pale w-6 text-center font-bold">
        {rank}
      </span>
    );
  };

  return (
    <MotionScreen>
      {/* Background theme */}
      <div className="absolute inset-0 bg-moss-radial">
        <div className="absolute inset-0 noise pointer-events-none" />
        <CyanMist />
      </div>

      {/* Top Header */}
      <div className="absolute top-0 left-0 right-0 z-30 p-3">
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate("/")}
            className="w-10 h-10 rounded-full carved-stone flex items-center justify-center hover:border-cyan-mist transition-colors"
            data-testid="btn-back-map"
          >
            <ArrowLeft className="w-5 h-5 text-cyan-mist" />
          </button>
          <div className="glass-panel flex-1 px-3 py-1.5 flex justify-between items-center">
            <span className="font-display text-sm font-bold tracking-widest text-bone">
              LEADERBOARD
            </span>
            <Trophy className="w-4 h-4 text-cyan-mist animate-glow-pulse" />
          </div>
        </div>
      </div>

      {/* Main Container */}
      <div
        className="relative w-full overflow-y-auto pt-16 pb-8 px-3 flex flex-col"
        style={{ height: "100%" }}
        data-testid="leaderboard-scroll"
      >
        <div className="glass-panel p-4 flex-1 flex flex-col overflow-hidden min-h-[500px]">
          <header className="text-center pb-2">
            <p className="font-mono text-[9px] tracking-[0.35em] uppercase text-cyan-mist/80">
              HALL OF HEROES
            </p>
            <h2 className="font-display text-xl font-bold text-bone">Challengers</h2>
          </header>
          <RuneDivider />

          {loading ? (
            <div className="flex-1 flex flex-col items-center justify-center space-y-2">
              <div className="w-8 h-8 rounded-full border-2 border-t-cyan-mist border-cyan-mist/20 animate-spin" />
              <p className="font-mono text-[10px] text-stone-pale uppercase">
                Recalling records...
              </p>
            </div>
          ) : error ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-4">
              <p className="font-body text-xs text-ember-orange">{error}</p>
            </div>
          ) : entries.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-6 space-y-3">
              <Trophy className="w-8 h-8 text-stone-pale/40" />
              <p className="font-body text-xs text-stone-pale italic">
                No dungeon crawlers have entered their names yet. Be the first to start a run!
              </p>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto space-y-2.5 pr-1 mt-2">
              {entries.map((entry, index) => {
                const rank = index + 1;
                const accuracy =
                  entry.total_attempts > 0
                    ? Math.round((entry.correct_attempts / entry.total_attempts) * 100)
                    : 0;

                return (
                  <motion.div
                    key={entry.player_id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className={`p-3 rounded-xl border flex items-center justify-between gap-3 ${
                      rank === 1
                        ? "bg-yellow-500/5 border-yellow-500/20 shadow-[0_0_12px_rgba(234,179,8,0.04)]"
                        : "glass-panel border-cyan-mist/10 hover:border-cyan-mist/30"
                    }`}
                  >
                    {/* Rank & Name */}
                    <div className="flex items-center gap-2.5 min-w-0">
                      {getRankBadge(rank)}
                      <div className="min-w-0">
                        <p className="font-heading text-xs font-bold text-bone leading-tight truncate">
                          {entry.player_id.toUpperCase()}
                        </p>
                        <div className="flex items-center gap-1.5 mt-0.5 opacity-80">
                          <Brain className="w-2.5 h-2.5 text-cyan-mist shrink-0" />
                          <span className="font-mono text-[9px] text-cyan-mist/90">
                            Threat: {Math.round(entry.threat_level)}%
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Stats */}
                    <div className="flex items-center gap-4 shrink-0 text-right">
                      {/* Floor */}
                      <div>
                        <p className="font-mono text-[9px] text-stone-pale uppercase leading-none">Floor</p>
                        <p className="font-heading text-xs font-bold text-ember-orange mt-0.5">
                          {entry.max_level === 50 && entry.correct_attempts > 0 ? "CLEAR" : entry.max_level}
                        </p>
                      </div>

                      {/* Explorer Score */}
                      <div>
                        <p className="font-mono text-[9px] text-stone-pale uppercase leading-none">Explore</p>
                        <div className="flex items-center gap-0.5 mt-0.5 justify-end">
                          <Compass className="w-2.5 h-2.5 text-cyan-mist shrink-0" />
                          <p className="font-heading text-xs font-bold text-cyan-mist">
                            {Math.round(entry.explorer_score * 100)}%
                          </p>
                        </div>
                      </div>

                      {/* Accuracy */}
                      <div>
                        <p className="font-mono text-[9px] text-stone-pale uppercase leading-none">Accuracy</p>
                        <p className="font-heading text-xs font-bold text-bone mt-0.5">
                          {accuracy}%
                        </p>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      <EmberParticles count={5} />
    </MotionScreen>
  );
}
