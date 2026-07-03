import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowLeft, Shield } from "lucide-react";
import { IMG, BOSS_DIALOGUE, LEVELS } from "../data/game";
import { HUD } from "../components/HUD";
import { DialogueBox } from "../components/DialogueBox";
import { QuestionCard } from "../components/QuestionCard";
import { EmberParticles, CyanMist, LightShaft, MotionScreen } from "../components/Atmosphere";
import { MemorySidebar, MemoryTrigger } from "../components/MemorySidebar";
import { MemoryGauge } from "../components/MemoryGauge";
import {
  RecallingBossOverlay,
  RecallingVignette,
} from "../components/RecallingOverlay";
import { useGame } from "../hooks/useGameState";

// Segmented stone HP bar for boss — with optional EMPOWERED frame glow
const BossHP = ({ segs = 10, filled = 7, empowered = false }) => (
  <div
    className="stone-hp"
    data-testid="boss-hp-bar"
    style={
      empowered
        ? {
            boxShadow:
              "inset 0 3px 6px rgba(0,0,0,0.8), 0 0 22px rgba(255,107,53,0.7)",
            borderColor: "#FF6B35",
          }
        : undefined
    }
  >
    {Array.from({ length: segs }).map((_, i) => (
      <div key={i} className={`stone-hp-seg ${i >= filled ? "stone-hp-seg-empty" : ""}`} />
    ))}
  </div>
);

export default function BossScreen() {
  const navigate = useNavigate();
  const { num } = useParams();
  const level = LEVELS[(parseInt(num) || 10) - 1] || LEVELS[9];

  const {
    playerName,
    challenge,
    shards,
    report,
    gaugeLevel,
    submitAnswerSession,
    fetchNextChallenge,
    getRecalledDialogue,
    forgetSession,
  } = useGame();

  const [dialogueIdx, setDialogueIdx] = useState(0);
  // phase: dialogue | sidebar | recalling | recalled | question | attacking | victory
  const [phase, setPhase] = useState("dialogue");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [bossHp, setBossHp] = useState(10);
  const [playerHp, setPlayerHp] = useState(5);
  const [bossPose, setBossPose] = useState("idle"); // idle | attack | hurt | recalling
  const [playerPose, setPlayerPose] = useState("idle");
  const [shakeKey, setShakeKey] = useState(0);
  const [recalledLines, setRecalledLines] = useState([]);
  const [recalledIdx, setRecalledIdx] = useState(0);

  const empowered = gaugeLevel >= 5;

  // Make sure we have the active challenge loaded when entering boss floor
  useEffect(() => {
    fetchNextChallenge();
  }, []);

  const advanceDialogue = () => {
    if (dialogueIdx < BOSS_DIALOGUE.length - 1) {
      setDialogueIdx(dialogueIdx + 1);
    } else {
      setPhase("question");
    }
  };

  const openSidebar = () => {
    setSidebarOpen(true);
    setPhase("sidebar");
  };

  // Closing sidebar triggers the RECALLING → RECALLED dialogue → question chain.
  const closeSidebar = () => {
    setSidebarOpen(false);
    setBossPose("recalling");
    setPhase("recalling");
    // Hold RECALLING pose for ~1.8s, then show RECALLED dialogue
    setTimeout(() => {
      setBossPose("idle");
      const lines = getRecalledDialogue();
      if (lines.length > 0) {
        setRecalledLines(lines);
        setRecalledIdx(0);
        setPhase("recalled");
      } else {
        setPhase("question");
      }
    }, 1800);
  };

  const advanceRecalled = () => {
    if (recalledIdx < recalledLines.length - 1) {
      setRecalledIdx(recalledIdx + 1);
    } else {
      setPhase("question");
    }
  };

  const handleAnswer = async (payload) => {
    try {
      const resp = await submitAnswerSession(payload);
      const ok = resp?.result?.correct;

      if (ok) {
        setPlayerPose("attack");
        setBossPose("hurt");
        // If floor cleared, boss drains to 0
        const newHp = resp?.result?.floor_cleared ? 0 : Math.max(2, bossHp - 3);
        setBossHp(newHp);

        setTimeout(async () => {
          setPlayerPose("idle");
          setBossPose("idle");
          if (resp?.result?.floor_cleared || resp?.result?.run_complete) {
            setPhase("victory");
            setTimeout(() => navigate("/victory"), 1200);
          } else {
            await fetchNextChallenge();
            setPhase("question");
          }
        }, 900);
      } else {
        setBossPose("attack");
        setPlayerPose("hurt");
        const newHp = Math.max(0, playerHp - 1);
        setPlayerHp(newHp);
        setShakeKey((k) => k + 1);

        setTimeout(() => {
          setPlayerPose("idle");
          setBossPose("idle");
          if (newHp <= 0) {
            navigate("/defeat");
          } else {
            if (resp?.result?.message) {
              setRecalledLines([
                {
                  id: "rd-taunt",
                  speaker: "boss",
                  name: "Vashkar",
                  text: resp.result.message,
                },
              ]);
              setRecalledIdx(0);
              setBossPose("recalling");
              setPhase("recalling");
              setTimeout(() => {
                setBossPose("idle");
                setPhase("recalled");
              }, 1800);
            } else {
              setPhase("question");
            }
          }
        }, 900);
      }
      setPhase("attacking");
      return resp;
    } catch (err) {
      console.error(err);
      throw err;
    }
  };

  const handleForget = async () => {
    await forgetSession();
    navigate("/");
  };

  // Boss image source per pose (RECALLING reuses idle + CSS overlay)
  const bossImg =
    bossPose === "attack"
      ? IMG.boss_attack
      : bossPose === "hurt"
        ? IMG.boss_hurt
        : IMG.boss_idle;

  const playerImg =
    playerPose === "attack"
      ? IMG.player_attack
      : playerPose === "hurt"
        ? IMG.player_hurt
        : IMG.player_idle;

  const isRecalling = bossPose === "recalling";

  return (
    <MotionScreen>
      <motion.div
        key={shakeKey}
        animate={shakeKey > 0 ? { x: [-10, 10, -6, 6, 0] } : {}}
        transition={{ duration: 0.4 }}
        className="absolute inset-0"
      >
        <img src={IMG.bg_boss_cavern} alt="" className="absolute inset-0 w-full h-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-b from-stone-darkest/40 via-transparent to-stone-darkest/85" />
        <div className="absolute inset-0 noise pointer-events-none" />
        <LightShaft style={{ top: 20, left: "38%", width: 140, height: 500 }} opacity={0.28} />
        <CyanMist />
      </motion.div>

      {/* Top strip */}
      <div className="absolute top-0 left-0 right-0 z-30 p-3 space-y-2">
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate("/")}
            className="w-10 h-10 rounded-full carved-stone flex items-center justify-center"
            data-testid="btn-back-map"
          >
            <ArrowLeft className="w-5 h-5 text-cyan-mist" />
          </button>
          <div className="glass-panel-ember flex-1 px-3 py-1.5 flex items-center gap-2 min-w-0">
            <Shield className="w-4 h-4 text-ember-orange shrink-0" />
            <span className="font-display text-sm font-bold tracking-widest text-bone truncate">
              {level.title.toUpperCase()}
            </span>
          </div>
          <MemoryTrigger
            onClick={openSidebar}
            active={sidebarOpen}
            count={shards.length}
          />
        </div>

        {/* Boss HP + Memory Gauge row */}
        <div
          className="glass-panel-ember p-2.5 space-y-2"
          style={
            empowered
              ? { boxShadow: "0 12px 40px rgba(0,0,0,0.55), 0 0 30px rgba(255,107,53,0.55)" }
              : undefined
          }
        >
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] tracking-[0.3em] uppercase text-ember-orange">
              VASHKAR
            </span>
            <span className="font-mono text-xs text-bone">{bossHp * 10}/100</span>
          </div>
          <BossHP segs={10} filled={bossHp} empowered={empowered} />
          <MemoryGauge filled={gaugeLevel} segments={5} />
        </div>

        <HUD hp={playerHp} xp={80} level={level.num} coins={128} />
      </div>

      {/* Arena — boss upper, player lower-left */}
      <div className="absolute inset-x-0 top-[260px] bottom-[240px] pointer-events-none z-20">
        {/* Boss + optional RECALLING overlay */}
        <div className="absolute top-4 left-1/2 -translate-x-1/2 w-56 h-64">
          <RecallingBossOverlay active={isRecalling} />
          <motion.div
            animate={{
              y: bossPose === "attack" ? -8 : bossPose === "hurt" ? 8 : [0, -4, 0],
              x: bossPose === "attack" ? -12 : 0,
              scale: isRecalling ? [1, 1.04, 1] : 1,
            }}
            transition={
              bossPose === "idle" || isRecalling
                ? { duration: 2.4, repeat: Infinity, ease: "easeInOut" }
                : { duration: 0.5 }
            }
            className="relative w-full h-full"
            data-testid={`boss-pose-${bossPose}`}
          >
            <img
              src={bossImg}
              alt=""
              className="w-full h-full object-contain drop-shadow-[0_20px_40px_rgba(255,107,53,0.35)]"
              style={
                isRecalling
                  ? { filter: "drop-shadow(0 0 24px #00E5FF) brightness(1.15) saturate(1.2)" }
                  : undefined
              }
            />
          </motion.div>
        </div>

        {/* Player */}
        <motion.div
          animate={{
            y: playerPose === "hurt" ? 6 : playerPose === "attack" ? -8 : [0, -3, 0],
            x: playerPose === "attack" ? 30 : 0,
          }}
          transition={
            playerPose === "idle"
              ? { duration: 2.2, repeat: Infinity, ease: "easeInOut" }
              : { duration: 0.5 }
          }
          className="absolute bottom-4 left-6 w-28 h-40"
          data-testid={`player-pose-${playerPose}`}
        >
          <img
            src={playerImg}
            alt=""
            className="w-full h-full object-contain drop-shadow-[0_10px_20px_rgba(0,0,0,0.85)]"
          />
        </motion.div>
      </div>

      {/* Screen-edge vignette during RECALLING */}
      <RecallingVignette active={isRecalling} />

      {/* Bottom stack: dialogue OR question */}
      <div className="absolute inset-x-0 bottom-0 z-40 p-3 pb-5">
        <AnimatePresence mode="wait">
          {phase === "dialogue" && (
            <motion.div key="dialogue" initial={{ y: 40, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 40, opacity: 0 }}>
              <DialogueBox
                entry={BOSS_DIALOGUE[dialogueIdx]}
                onAdvance={advanceDialogue}
                index={dialogueIdx}
                total={BOSS_DIALOGUE.length}
              />
            </motion.div>
          )}

          {phase === "recalling" && (
            <motion.div
              key="recalling-tag"
              initial={{ y: 40, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 40, opacity: 0 }}
            >
              <div className="glass-panel px-4 py-3 flex items-center gap-3" data-testid="recalling-status">
                <motion.div
                  animate={{ rotate: [0, 12, -12, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                  className="w-8 h-8 rounded-md flex items-center justify-center border border-cyan-mist bg-moss-dark"
                  style={{ boxShadow: "0 0 18px rgba(0,229,255,0.6)" }}
                >
                  <svg viewBox="0 0 16 16" className="w-4 h-4">
                    <circle cx="8" cy="8" r="6" stroke="#00E5FF" strokeWidth="1.4" fill="none" />
                    <path d="M8 2 L8 14 M2 8 L14 8" stroke="#00E5FF" strokeWidth="1" />
                  </svg>
                </motion.div>
                <div className="flex-1 min-w-0">
                  <p className="font-mono text-[10px] tracking-[0.32em] uppercase text-cyan-mist">
                    RECALLING…
                  </p>
                  <p className="font-body text-xs text-stone-pale italic">
                    Vashkar is searching its memory of you.
                  </p>
                </div>
              </div>
            </motion.div>
          )}

          {phase === "recalled" && (
            <motion.div key="recalled" initial={{ y: 40, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 40, opacity: 0 }}>
              <DialogueBox
                entry={recalledLines[recalledIdx]}
                onAdvance={advanceRecalled}
                index={recalledIdx}
                total={recalledLines.length}
                recalled
              />
            </motion.div>
          )}

          {(phase === "question" || phase === "attacking") && challenge && (
            <motion.div key="question" initial={{ y: 40, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 40, opacity: 0 }}>
              <QuestionCard question={challenge} onAnswer={handleAnswer} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Memory sidebar */}
      <MemorySidebar
        open={sidebarOpen}
        onClose={closeSidebar}
        shards={shards}
        bossName="Vashkar"
        source="cognee.memory.v1"
        onForget={handleForget}
        graph={report?.graph}
        profile={report?.profile}
        playerName={playerName}
      />

      <EmberParticles count={18} />
    </MotionScreen>
  );
}
