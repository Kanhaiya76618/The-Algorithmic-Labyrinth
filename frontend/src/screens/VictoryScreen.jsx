import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { IMG } from "../data/game";
import { EmberParticles, CyanMist, MotionScreen } from "../components/Atmosphere";
import { StarRating } from "../components/HUD";

export default function VictoryScreen() {
  const navigate = useNavigate();

  return (
    <MotionScreen>
      <div className="absolute inset-0">
        <img src={IMG.bg_boss_cavern} alt="" className="absolute inset-0 w-full h-full object-cover blur-sm scale-110" />
        <div className="absolute inset-0 bg-moss-darkest/80" />
        <CyanMist />
      </div>

      {/* Radial cyan burst */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: [0, 1.6, 1.2], opacity: [0, 0.9, 0.6] }}
        transition={{ duration: 1.2, times: [0, 0.6, 1] }}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full pointer-events-none"
        style={{
          background:
            "radial-gradient(circle, rgba(0,229,255,0.4) 0%, transparent 60%)",
          filter: "blur(20px)",
        }}
      />

      <div className="absolute inset-0 flex flex-col items-center justify-center px-6 space-y-6 z-10">
        <motion.p
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="font-mono text-[11px] tracking-[0.4em] uppercase text-cyan-mist"
        >
          MEMORY RECLAIMED
        </motion.p>
        <motion.h1
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.35, type: "spring" }}
          className="font-display text-4xl md:text-5xl font-black text-bone text-shadow-stone text-center leading-tight"
          data-testid="victory-title"
        >
          THE RUINS<br />OPEN THEIR GATES
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="font-body text-xs italic text-stone-pale text-center max-w-xs px-2"
        >
          You have conquered the floor. Vashkar has reinforced your strengths, ensuring your mind stands stronger in the next memory trial.
        </motion.p>

        <div className="pt-1 pb-2">
          <StarRating stars={3} max={3} size={40} />
        </div>

        {/* Relic chest */}
        <motion.div
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="relative w-40 h-40"
          data-testid="victory-chest"
        >
          <img
            src={IMG.prop_chest}
            alt=""
            className="w-full h-full object-contain drop-shadow-[0_16px_30px_rgba(255,107,53,0.5)] animate-idle-bob"
          />
          <motion.div
            animate={{ opacity: [0.3, 1, 0.3] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="absolute inset-0 rounded-full pointer-events-none"
            style={{
              background:
                "radial-gradient(circle at center, rgba(245,185,66,0.6) 0%, transparent 60%)",
              filter: "blur(24px)",
            }}
          />
        </motion.div>

        {/* Rewards */}
        <div className="glass-panel px-4 py-3 flex items-center gap-6" data-testid="victory-rewards">
          <div className="text-center">
            <p className="font-mono text-[9px] tracking-widest text-cyan-mist/80 uppercase">XP</p>
            <p className="font-display font-bold text-2xl text-bone">+ 240</p>
          </div>
          <div className="h-8 w-px bg-cyan-mist/30" />
          <div className="text-center">
            <p className="font-mono text-[9px] tracking-widest text-ember-orange/80 uppercase">Relics</p>
            <p className="font-display font-bold text-2xl text-ember-orange">+ 12</p>
          </div>
        </div>

        <div className="flex flex-col gap-2 w-full max-w-xs pt-2">
          <button
            className="btn-ember w-full"
            onClick={() => navigate("/")}
            data-testid="btn-victory-continue"
          >
            Return to Map
          </button>
          <button
            className="btn-cyan w-full"
            onClick={() => navigate("/spritesheet")}
            data-testid="btn-victory-view-loot"
          >
            View Sprite Sheet
          </button>
        </div>
      </div>

      <EmberParticles count={22} />
    </MotionScreen>
  );
}
