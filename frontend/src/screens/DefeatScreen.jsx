import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { IMG } from "../data/game";
import { EmberParticles, MotionScreen } from "../components/Atmosphere";

export default function DefeatScreen() {
  const navigate = useNavigate();

  return (
    <MotionScreen>
      <div className="absolute inset-0">
        <img src={IMG.bg_world_map} alt="" className="absolute inset-0 w-full h-full object-cover blur-[6px] scale-110 grayscale" />
        <div className="absolute inset-0 bg-stone-darkest/85" />
        {/* Mist swallow overlay */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.5 }}
          className="absolute inset-0"
          style={{
            background:
              "radial-gradient(ellipse at 50% 60%, rgba(11,18,12,0.2) 0%, rgba(11,18,12,0.95) 65%)",
          }}
        />
      </div>

      <div className="absolute inset-0 flex flex-col items-center justify-center px-6 space-y-8 z-10">
        {/* Skull silhouette using player hurt */}
        <motion.div
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="relative w-48 h-56"
        >
          <img
            src={IMG.player_hurt}
            alt=""
            className="w-full h-full object-contain grayscale contrast-125"
            style={{ filter: "grayscale(1) brightness(0.6) drop-shadow(0 0 30px rgba(255,107,53,0.4))" }}
          />
          <motion.div
            animate={{ opacity: [0.4, 0.9, 0.4] }}
            transition={{ duration: 3, repeat: Infinity }}
            className="absolute inset-0 pointer-events-none"
            style={{
              background:
                "radial-gradient(circle at 50% 40%, rgba(255,107,53,0.35) 0%, transparent 55%)",
              filter: "blur(20px)",
            }}
          />
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="font-mono text-[11px] tracking-[0.4em] uppercase text-ember-orange"
        >
          DEFEAT
        </motion.p>
        <motion.h1
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="font-display text-4xl md:text-5xl font-black text-bone/95 text-center leading-tight text-shadow-stone"
          data-testid="defeat-title"
        >
          THE RUINS REMEMBER…
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.05 }}
          className="font-body italic text-stone-pale text-center max-w-xs"
        >
          But Vashkar does. Your mistakes have been written to the graph, and the Boss AI will remember your vulnerabilities for your next descent.
        </motion.p>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.3 }}
          className="flex flex-col gap-2 w-full max-w-xs pt-2"
        >
          <button
            className="btn-ember w-full"
            onClick={() => navigate("/level/7")}
            data-testid="btn-defeat-retry"
          >
            Try Again
          </button>
          <button
            className="btn-cyan w-full"
            onClick={() => navigate("/")}
            data-testid="btn-defeat-map"
          >
            Return to Map
          </button>
        </motion.div>
      </div>

      <EmberParticles count={8} />
    </MotionScreen>
  );
}
