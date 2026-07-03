import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import { IMG, LEVELS } from "../data/game";
import { HUD } from "../components/HUD";
import { QuestionCard } from "../components/QuestionCard";
import { EmberParticles, CyanMist, LightShaft, MotionScreen } from "../components/Atmosphere";
import { useGame } from "../hooks/useGameState";

export default function LevelScreen() {
  const navigate = useNavigate();
  const { num } = useParams();
  const level = LEVELS[(parseInt(num) || 1) - 1] || LEVELS[0];

  const {
    challenge,
    runLevel,
    submitAnswerSession,
    fetchNextChallenge,
  } = useGame();

  const [hp, setHp] = useState(4);
  const [activeMonster, setActive] = useState(null);
  const [defeated, setDefeated] = useState([]);
  const [xp, setXp] = useState(64);
  const [floatText, setFloatText] = useState(null);
  const [shakeKey, setShakeKey] = useState(0);

  const monsters = [
    { id: "m1", img: IMG.monster1_idle, hit: IMG.monster1_hit, x: 18, y: 55, scale: 1.0 },
    { id: "m2", img: IMG.monster2_idle, hit: IMG.monster2_hit, x: 50, y: 40, scale: 0.9 },
    { id: "m3", img: IMG.monster3_idle, hit: IMG.monster3_hit, x: 78, y: 60, scale: 1.05 },
  ];

  // Make sure we have the active challenge loaded when entering a floor
  useEffect(() => {
    if (parseInt(num) < runLevel) {
      setDefeated(["m1", "m2", "m3"]);
    } else {
      fetchNextChallenge();
    }
  }, [num, runLevel]);

  const handleAnswer = async (payload) => {
    try {
      const resp = await submitAnswerSession(payload);
      const ok = resp?.result?.correct;
      if (ok) {
        setDefeated(["m1", "m2", "m3"]); // Answering correctly clears the whole room
        setXp((v) => Math.min(100, v + 12));
        setFloatText({ type: "ok", text: "+12 XP" });
      } else {
        setHp((h) => Math.max(0, h - 1));
        setFloatText({ type: "bad", text: "-1 HP" });
        setShakeKey((k) => k + 1);
      }
      setTimeout(() => {
        setActive(null);
        setFloatText(null);
      }, 2000);
      return resp;
    } catch (err) {
      console.error(err);
      throw err;
    }
  };

  const allDown = defeated.length >= monsters.length;

  return (
    <MotionScreen>
      {/* Background */}
      <motion.div
        key={shakeKey}
        animate={shakeKey > 0 ? { x: [-8, 8, -6, 6, 0] } : {}}
        transition={{ duration: 0.35 }}
        className="absolute inset-0"
      >
        <img
          src={IMG.bg_level}
          alt=""
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-moss-darkest/50 via-transparent to-moss-darkest/70" />
        <div className="absolute inset-0 noise pointer-events-none" />
        <LightShaft style={{ top: 40, left: 60, width: 120, height: 400 }} opacity={0.25} />
        <LightShaft style={{ top: 40, right: 40, width: 90, height: 380 }} opacity={0.15} />
        <CyanMist />
      </motion.div>

      {/* Top strip: back + level info */}
      <div className="absolute top-0 left-0 right-0 z-30 p-3 space-y-2">
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate("/")}
            className="w-10 h-10 rounded-full carved-stone flex items-center justify-center"
            data-testid="btn-back-map"
          >
            <ArrowLeft className="w-5 h-5 text-cyan-mist" />
          </button>
          <div className="glass-panel flex-1 px-3 py-1.5 flex items-center justify-between">
            <span className="font-mono text-[10px] tracking-[0.25em] text-cyan-mist/80">
              {level.zone.name.toUpperCase()}
            </span>
            <span className="font-display text-sm font-bold text-bone">
              TRIAL {String(level.num).padStart(2, "0")}
            </span>
          </div>
        </div>
        <HUD hp={hp} xp={xp} level={runLevel} coins={128} />
      </div>

      {/* Playfield with monsters */}
      <div className="absolute inset-x-0 top-[130px] bottom-[280px] px-2 z-20">
        <div className="relative w-full h-full" data-testid="playfield">
          {/* player character bottom-left */}
          <div className="absolute bottom-0 left-2 w-24 h-32 pointer-events-none">
            <img
              src={IMG.player_idle}
              alt=""
              className="w-full h-full object-contain animate-idle-bob drop-shadow-[0_6px_14px_rgba(0,0,0,0.75)]"
            />
          </div>

          {/* Monsters */}
          {monsters.map((m) => {
            const dead = defeated.includes(m.id);
            return (
              <motion.button
                key={m.id}
                onClick={() => !dead && setActive(m)}
                disabled={dead}
                data-testid={`monster-${m.id}`}
                whileHover={{ scale: dead ? 1 : 1.08 }}
                whileTap={{ scale: dead ? 1 : 0.94 }}
                className="absolute w-20 h-20 focus:outline-none"
                style={{
                  left: `${m.x}%`,
                  top: `${m.y}%`,
                  transform: `translate(-50%, -50%) scale(${m.scale})`,
                  opacity: dead ? 0.3 : 1,
                  filter: dead ? "grayscale(1)" : "none",
                }}
              >
                <img
                  src={dead ? m.hit : m.img}
                  alt=""
                  className={`w-full h-full object-contain ${dead ? "" : "animate-idle-bob"} drop-shadow-[0_6px_14px_rgba(0,0,0,0.7)]`}
                />
                {!dead && (
                  <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-cyan-mist animate-ping" />
                )}
              </motion.button>
            );
          })}

          {allDown && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center animate-idle-bob"
            >
              <p className="font-display text-2xl font-bold text-cyan-mist text-shadow-glow">
                TRIAL CLEARED
              </p>
              <button
                onClick={() => navigate("/victory")}
                className="btn-ember mt-4"
                data-testid="btn-goto-victory"
              >
                Claim Reward
              </button>
            </motion.div>
          )}
        </div>
      </div>

      {/* Floating toasts */}
      <AnimatePresence>
        {floatText && (
          <motion.div
            initial={{ opacity: 0, y: 0, scale: 0.8 }}
            animate={{ opacity: 1, y: -30, scale: 1 }}
            exit={{ opacity: 0, y: -60 }}
            className="absolute left-1/2 top-1/2 -translate-x-1/2 z-50 pointer-events-none"
          >
            <div
              className={`font-display font-bold text-2xl ${
                floatText.type === "ok" ? "text-cyan-mist text-shadow-glow" : "text-ember-orange"
              }`}
              style={{
                textShadow:
                  floatText.type === "ok"
                    ? "0 0 20px rgba(0,229,255,0.85)"
                    : "0 0 20px rgba(255,107,53,0.85)",
              }}
            >
              {floatText.text}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Question card slide-up */}
      <AnimatePresence>
        {activeMonster && challenge && (
          <div className="absolute inset-x-0 bottom-0 p-3 pb-5 z-40">
            <QuestionCard
              question={challenge}
              monsterImg={activeMonster.img}
              onAnswer={handleAnswer}
              onClose={() => setActive(null)}
            />
          </div>
        )}
      </AnimatePresence>

      {/* Defeat overlay */}
      {hp === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="absolute inset-0 bg-moss-darkest/85 backdrop-blur-md z-50 flex items-center justify-center"
        >
          <div className="text-center space-y-4">
            <p className="font-display text-3xl text-ember-orange text-shadow-stone">
              THE RUINS REMEMBER…
            </p>
            <button className="btn-cyan" onClick={() => navigate("/defeat")} data-testid="btn-goto-defeat">
              Continue
            </button>
          </div>
        </motion.div>
      )}

      <EmberParticles count={12} />
    </MotionScreen>
  );
}
