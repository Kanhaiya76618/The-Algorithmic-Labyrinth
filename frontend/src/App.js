import React, { useState } from "react";
import { BrowserRouter, Routes, Route, useLocation, Link } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Map, Swords, Skull, LayoutGrid, Grid3x3, Settings as SettingsIcon, X, Volume2, Trophy, LogOut } from "lucide-react";
import "@/App.css";

import WorldMapScreen from "@/screens/WorldMapScreen";
import LevelScreen from "@/screens/LevelScreen";
import BossScreen from "@/screens/BossScreen";
import VictoryScreen from "@/screens/VictoryScreen";
import DefeatScreen from "@/screens/DefeatScreen";
import ComponentLibraryScreen from "@/screens/ComponentLibraryScreen";
import SpriteSheetScreen from "@/screens/SpriteSheetScreen";
import LeaderboardScreen from "@/screens/LeaderboardScreen";
import { IMG } from "@/data/game";
import { GameProvider, useGame } from "@/hooks/useGameState";

// Desktop side scenery
const SideScenery = ({ side }) => {
  const img = side === "left" ? IMG.bg_side_left : IMG.bg_side_right;
  return (
    <div className="hidden lg:block flex-1 relative overflow-hidden h-screen">
      <img
        src={img}
        alt=""
        className="absolute inset-0 w-full h-full object-cover"
      />
      <div
        className={`absolute inset-0 bg-gradient-to-${side === "left" ? "l" : "r"} from-transparent to-moss-darkest`}
      />
      {/* Bioluminescent motes */}
      {Array.from({ length: 14 }).map((_, i) => (
        <motion.span
          key={i}
          className="absolute rounded-full bg-cyan-mist"
          style={{
            left: `${(i * 37) % 100}%`,
            top: `${(i * 53) % 100}%`,
            width: 3,
            height: 3,
            boxShadow: "0 0 10px #00E5FF",
          }}
          animate={{ opacity: [0.3, 1, 0.3], y: [0, -12, 0] }}
          transition={{ duration: 3 + (i % 4), repeat: Infinity, delay: i * 0.2 }}
        />
      ))}
      {/* Label */}
      <div className="absolute bottom-6 left-6 right-6 opacity-70">
         <p className="font-mono text-[10px] tracking-[0.3em] text-cyan-mist uppercase">
          {side === "left" ? "West Vault" : "East Cascade"}
        </p>
      </div>
    </div>
  );
};

// Top nav bar rendered on desktop above the device frame
const DesktopNav = () => {
  const loc = useLocation();
  const { runLevel, playerName, exitSession } = useGame();
  
  const currentLvl = runLevel || 1;
  const items = [
    { to: "/", label: "World Map", icon: Map, testid: "nav-map" },
    { to: `/level/${currentLvl}`, label: "Level", icon: Swords, testid: "nav-level" },
    { to: "/leaderboard", label: "Leaderboard", icon: Trophy, testid: "nav-leaderboard" },
    { to: "/library", label: "Components", icon: LayoutGrid, testid: "nav-library" },
    { to: "/spritesheet", label: "Sprites", icon: Grid3x3, testid: "nav-spritesheet" },
  ];
  return (
    <div className="mb-3 flex flex-col items-center gap-1.5" data-testid="desktop-nav">
      {/* Main nav links row */}
      <div className="flex gap-1.5 flex-wrap justify-center">
        {items.map((it) => {
          const Ic = it.icon;
          const active = loc.pathname === it.to || (it.to === "/" && loc.pathname === "/");
          return (
            <Link
              key={it.to}
              to={it.to}
              data-testid={it.testid}
              className={`carved-stone px-3 py-1.5 flex items-center gap-1.5 transition-all ${active ? "!bg-cyan-mist/15 border-cyan-mist" : ""}`}
            >
              <Ic className={`w-4 h-4 ${active ? "text-cyan-mist" : "text-stone-pale"}`} />
              <span className={`font-heading text-[11px] font-bold tracking-widest ${active ? "text-cyan-mist" : "text-bone/80"}`}>
                {it.label.toUpperCase()}
              </span>
            </Link>
          );
        })}
      </div>
      {/* Exit Run row — only visible when a player session is active */}
      {playerName && (
        <div className="flex justify-center">
          <button
            onClick={exitSession}
            className="carved-stone px-4 py-1 flex items-center gap-1.5 transition-all text-stone-pale hover:text-ember-orange hover:border-ember-orange"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span className="font-heading text-[10px] font-bold tracking-widest uppercase">
              Exit Run · {playerName.toUpperCase()}
            </span>
          </button>
        </div>
      )}
    </div>
  );
};

// Settings modal
const SettingsModal = ({ open, onClose }) => (
  <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
    <DialogContent
      className="glass-panel !bg-transparent border-0 max-w-sm p-0"
      data-testid="settings-modal"
    >
      <div className="glass-panel p-5 space-y-4">
        <DialogHeader className="flex-row items-center justify-between space-y-0">
          <DialogTitle asChild>
            <div>
              <p className="font-mono text-[10px] tracking-[0.3em] text-cyan-mist uppercase">Rune of Setting</p>
              <p className="font-display text-2xl font-bold text-bone">Settings</p>
            </div>
          </DialogTitle>
          <DialogDescription className="sr-only">Adjust music, sfx, haptics, and mist FX for the game.</DialogDescription>
          <button
            onClick={onClose}
            data-testid="settings-close"
            className="w-8 h-8 rounded-full border border-cyan-mist/40 flex items-center justify-center hover:border-cyan-mist"
          >
            <X className="w-4 h-4 text-bone" />
          </button>
        </DialogHeader>
        <div className="rune-divider" />

        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="font-heading text-xs text-bone tracking-widest">MUSIC</span>
              <span className="font-mono text-[10px] text-cyan-mist">72%</span>
            </div>
            <Slider defaultValue={[72]} max={100} step={1} data-testid="settings-music" />
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="font-heading text-xs text-bone tracking-widest">SFX</span>
              <span className="font-mono text-[10px] text-cyan-mist">88%</span>
            </div>
            <Slider defaultValue={[88]} max={100} step={1} data-testid="settings-sfx" />
          </div>
          <div className="flex items-center justify-between">
            <span className="font-heading text-xs text-bone tracking-widest">HAPTICS</span>
            <Switch defaultChecked data-testid="settings-haptics" />
          </div>
          <div className="flex items-center justify-between">
            <span className="font-heading text-xs text-bone tracking-widest">CYAN MIST FX</span>
            <Switch defaultChecked data-testid="settings-mist" />
          </div>
        </div>

        <div className="pt-2 flex gap-2">
          <button onClick={onClose} className="btn-ember flex-1" data-testid="settings-save">
            Save
          </button>
          <button onClick={onClose} className="btn-cyan flex-1" data-testid="settings-cancel">
            Cancel
          </button>
        </div>
      </div>
    </DialogContent>
  </Dialog>
);

// Main app shell: routes the mobile "device" and paints desktop scenery on the sides
function AppShell() {
  const [settingsOpen, setSettingsOpen] = useState(false);

  return (
    <div className="min-h-screen w-full flex bg-moss-radial">
      {/* Left scenery */}
      <SideScenery side="left" />

      {/* Center device column */}
      <div className="flex-shrink-0 flex flex-col items-center justify-start py-6 px-3 min-h-screen w-full lg:w-auto">
        {/* Title on desktop only */}
        <div className="hidden lg:block mb-3 text-center">
          <p className="font-mono text-[10px] tracking-[0.4em] text-cyan-mist uppercase">A Cognitive Memory Trial</p>
          <h1 className="font-display text-2xl font-black text-bone text-shadow-stone">
            DUNGEON OF RECALL
          </h1>
        </div>
        <DesktopNav />

        {/* Mobile device frame — but on mobile expands full width */}
        <div className="lg:device-frame w-full max-w-[390px] min-h-[844px] relative overflow-hidden rounded-3xl bg-moss-darkest shadow-2xl">
          <AnimatePresence mode="wait">
            <Routes>
              <Route path="/" element={<WorldMapScreen onOpenSettings={() => setSettingsOpen(true)} />} />
              <Route path="/level/:num" element={<LevelScreen />} />
              <Route path="/boss/:num" element={<BossScreen />} />
              <Route path="/victory" element={<VictoryScreen />} />
              <Route path="/defeat" element={<DefeatScreen />} />
              <Route path="/library" element={<ComponentLibraryScreen />} />
              <Route path="/spritesheet" element={<SpriteSheetScreen />} />
              <Route path="/leaderboard" element={<LeaderboardScreen />} />
            </Routes>
          </AnimatePresence>
        </div>

        <div className="hidden lg:block mt-4 text-center max-w-md">
          <p className="font-mono text-[10px] tracking-[0.25em] text-stone-pale uppercase">
            Mobile 390 × 844 · Vertical Scroll · Powered by Cognee
          </p>
        </div>
      </div>

      {/* Right scenery */}
      <SideScenery side="right" />

      <SettingsModal open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <GameProvider>
        <AppShell />
      </GameProvider>
    </BrowserRouter>
  );
}
