import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { IMG, ZONES } from "../data/game";
import { EmberParticles, MotionScreen, RuneDivider } from "../components/Atmosphere";
import { LevelNode, ZoneBanner } from "../components/LevelNode";
import { HeartsHUD, XPBar, CoinCounter, StarRating } from "../components/HUD";
import { MemoryShard, MemoryShardEmpty } from "../components/MemoryShard";
import { MemoryGauge } from "../components/MemoryGauge";
import { MEMORY_SHARDS, EMPTY_MEMORY_MESSAGE } from "../data/memory";
import { DialogueBox } from "../components/DialogueBox";
import { ArrowLeft } from "lucide-react";

const Section = ({ title, subtitle, children }) => (
  <div className="glass-panel p-4 space-y-3">
    <div>
      <p className="font-mono text-[10px] tracking-[0.35em] uppercase text-cyan-mist/80">
        {subtitle}
      </p>
      <h3 className="font-display text-xl font-bold text-bone">{title}</h3>
    </div>
    <RuneDivider />
    {children}
  </div>
);

const Swatch = ({ name, hex }) => (
  <div className="flex items-center gap-2">
    <div
      className="w-8 h-8 rounded-md border-2 border-stone-darkest shrink-0"
      style={{ background: hex, boxShadow: "inset 0 -2px 0 rgba(0,0,0,0.4)" }}
    />
    <div className="min-w-0">
      <p className="font-heading text-xs font-bold text-bone leading-tight">{name}</p>
      <p className="font-mono text-[10px] text-stone-pale">{hex}</p>
    </div>
  </div>
);

export default function ComponentLibraryScreen() {
  const navigate = useNavigate();

  const demoNodes = [
    { num: 1, isBoss: false, status: "completed", zone: ZONES[0], zoneIndex: 0, xPct: 50 },
    { num: 2, isBoss: false, status: "current", zone: ZONES[0], zoneIndex: 0, xPct: 50 },
    { num: 3, isBoss: false, status: "unlocked", zone: ZONES[0], zoneIndex: 0, xPct: 50 },
    { num: 4, isBoss: false, status: "locked", zone: ZONES[0], zoneIndex: 0, xPct: 50 },
    { num: 10, isBoss: true, status: "unlocked", zone: ZONES[0], zoneIndex: 0, xPct: 50 },
  ];

  return (
    <MotionScreen>
      <div className="absolute inset-0 bg-moss-radial">
        <div className="absolute inset-0 noise pointer-events-none" />
      </div>

      {/* Top bar */}
      <div className="absolute top-0 left-0 right-0 z-30 p-3">
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate("/")}
            className="w-10 h-10 rounded-full carved-stone flex items-center justify-center"
            data-testid="btn-back-map"
          >
            <ArrowLeft className="w-5 h-5 text-cyan-mist" />
          </button>
          <div className="glass-panel flex-1 px-3 py-1.5">
            <span className="font-display text-sm font-bold tracking-widest text-bone">
              COMPONENT LIBRARY
            </span>
          </div>
        </div>
      </div>

      <div
        className="relative w-full overflow-y-auto pt-16 pb-8 px-3 space-y-3"
        style={{ height: "100%" }}
        data-testid="library-scroll"
      >
        {/* Typography */}
        <Section subtitle="01 — Type" title="Typography">
          <div className="space-y-2">
            <p className="font-display text-3xl font-bold text-bone leading-none">Cinzel Decorative</p>
            <p className="font-heading text-lg font-bold text-bone">Cinzel (Headings)</p>
            <p className="font-body text-sm text-stone-pale italic">Lora — narrative body text for the ruins.</p>
            <p className="font-mono text-xs text-cyan-mist">JetBrains Mono — data labels.</p>
          </div>
        </Section>

        {/* Palette */}
        <Section subtitle="02 — Color" title="Palette">
          <div className="grid grid-cols-2 gap-2">
            <Swatch name="Moss Dark" hex="#131A14" />
            <Swatch name="Moss Light" hex="#2A3F2D" />
            <Swatch name="Stone Mid" hex="#363A36" />
            <Swatch name="Earth Brown" hex="#382918" />
            <Swatch name="Cyan Mist" hex="#00E5FF" />
            <Swatch name="Ember Orange" hex="#FF6B35" />
            <Swatch name="Ember Gold" hex="#F5B942" />
            <Swatch name="Bone" hex="#E8EDE6" />
          </div>
        </Section>

        {/* Buttons */}
        <Section subtitle="03 — Buttons" title="Rune Buttons">
          <div className="flex flex-wrap gap-2" data-testid="library-buttons">
            <button className="btn-ember" data-testid="lib-btn-ember">Begin Trial</button>
            <button className="btn-cyan" data-testid="lib-btn-cyan">Return</button>
            <button className="btn-disabled" data-testid="lib-btn-disabled">Sealed</button>
          </div>
        </Section>

        {/* Level Nodes */}
        <Section subtitle="04 — Nodes" title="Level Nodes">
          <div className="flex items-end gap-4 py-2 justify-around">
            {demoNodes.map((n) => (
              <div key={n.num} className="flex flex-col items-center gap-2">
                <LevelNode level={n} onClick={() => {}} isPreview />
                <span className="font-mono text-[9px] tracking-widest text-stone-pale uppercase">
                  {n.isBoss ? "boss" : n.status}
                </span>
              </div>
            ))}
          </div>
        </Section>

        {/* HUD */}
        <Section subtitle="05 — HUD" title="Heads-Up Display">
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <HeartsHUD hp={3} max={5} testid="lib-hearts" />
              <span className="font-mono text-[10px] text-stone-pale">3 / 5 HP</span>
            </div>
            <XPBar value={72} level={7} testid="lib-xp" />
            <div className="flex gap-3">
              <CoinCounter value={128} testid="lib-coins" />
              <div className="carved-stone px-2.5 py-1 flex items-center gap-2">
                <StarRating stars={3} max={3} size={18} />
              </div>
            </div>
          </div>
        </Section>

        {/* Zone banners */}
        <Section subtitle="06 — Zones" title="Zone Banners">
          <div className="space-y-1 -mx-2">
            {ZONES.slice(0, 3).map((z, i) => (
              <ZoneBanner key={z.id} zone={z} index={i} />
            ))}
          </div>
        </Section>

        {/* Cards */}
        <Section subtitle="07 — Panels" title="Glassmorphism & Carved Stone">
          <div className="grid grid-cols-2 gap-2">
            <div className="glass-panel p-3">
              <p className="font-heading text-xs font-bold text-cyan-mist tracking-widest uppercase">
                Cyan Glass
              </p>
              <p className="font-body text-xs text-stone-pale mt-1">Question popups, tooltips.</p>
            </div>
            <div className="glass-panel-ember p-3">
              <p className="font-heading text-xs font-bold text-ember-orange tracking-widest uppercase">
                Ember Glass
              </p>
              <p className="font-body text-xs text-stone-pale mt-1">Boss cards, warnings.</p>
            </div>
            <div className="carved-stone p-3">
              <p className="font-heading text-xs font-bold text-bone tracking-widest uppercase">
                Carved Stone
              </p>
              <p className="font-body text-xs text-stone-pale mt-1">Dialogue, HUD widgets.</p>
            </div>
            <div className="p-3 rounded-xl border-2 border-cyan-mist/70 bg-moss-dark shadow-cyan-glow">
              <p className="font-heading text-xs font-bold text-cyan-mist tracking-widest uppercase">
                Cyan Glow
              </p>
              <p className="font-body text-xs text-stone-pale mt-1">Interactive highlight.</p>
            </div>
          </div>
        </Section>

        {/* Motion */}
        <Section subtitle="08 — Motion" title="Signature Animations">
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="glass-panel p-3">
              <p className="font-heading text-cyan-mist tracking-widest text-[10px] uppercase">Glow Pulse</p>
              <div className="mt-2 w-10 h-10 rounded-full bg-moss-mid border-2 border-cyan-mist animate-glow-pulse mx-auto" />
            </div>
            <div className="glass-panel p-3 relative overflow-hidden h-24">
              <p className="font-heading text-ember-orange tracking-widest text-[10px] uppercase">Ember Drift</p>
              <EmberParticles count={8} />
            </div>
            <div className="glass-panel p-3">
              <p className="font-heading text-cyan-mist tracking-widest text-[10px] uppercase">Idle Bob</p>
              <img src={IMG.monster1_idle} alt="" className="w-12 h-12 mx-auto object-contain animate-idle-bob" />
            </div>
            <div className="glass-panel p-3">
              <p className="font-heading text-cyan-mist tracking-widest text-[10px] uppercase">Sway</p>
              <img src={IMG.prop_plant} alt="" className="w-12 h-12 mx-auto object-contain animate-sway" />
            </div>
          </div>
        </Section>

        {/* Cognee Memory System */}
        <Section subtitle="09 — Cognee" title="Memory System">
          <p className="font-body text-xs text-stone-pale italic mb-3">
            All shards, journal rows, and recalled lines render from a single mock
            <code className="mx-1 font-mono text-[10px] text-cyan-mist">/data/memory.js</code>
            object — swap it with the real Cognee API response.
          </p>

          <p className="font-mono text-[9px] tracking-[0.3em] text-cyan-mist/80 uppercase mb-1.5">
            Memory Shards (4 variants)
          </p>
          <div className="space-y-2">
            {MEMORY_SHARDS.map((s, i) => (
              <MemoryShard key={s.id} shard={s} index={i} />
            ))}
          </div>

          <div className="mt-3">
            <p className="font-mono text-[9px] tracking-[0.3em] text-cyan-mist/80 uppercase mb-1.5">
              Empty State
            </p>
            <MemoryShardEmpty message={EMPTY_MEMORY_MESSAGE} />
          </div>

          <div className="mt-4">
            <p className="font-mono text-[9px] tracking-[0.3em] text-cyan-mist/80 uppercase mb-2">
              Memory Gauge — 3 states
            </p>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="font-mono text-[9px] w-14 text-stone-pale uppercase">empty</span>
                <MemoryGauge filled={0} />
              </div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-[9px] w-14 text-stone-pale uppercase">partial</span>
                <MemoryGauge filled={3} />
              </div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-[9px] w-14 text-stone-pale uppercase">full</span>
                <MemoryGauge filled={5} />
              </div>
            </div>
          </div>

          <div className="mt-4">
            <p className="font-mono text-[9px] tracking-[0.3em] text-cyan-mist/80 uppercase mb-2">
              Recalled Dialogue variant
            </p>
            <DialogueBox
              entry={{
                speaker: "boss",
                name: "Vashkar",
                text: "Arrays again, little flame? I remember every time they burned you.",
              }}
              onAdvance={() => {}}
              index={0}
              total={1}
              recalled
            />
          </div>
        </Section>

        <div className="pb-4" />
      </div>

      <EmberParticles count={6} />
    </MotionScreen>
  );
}
