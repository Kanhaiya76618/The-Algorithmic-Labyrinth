import React from "react";
import { useNavigate } from "react-router-dom";
import { IMG } from "../data/game";
import { MotionScreen } from "../components/Atmosphere";
import { ArrowLeft, Download } from "lucide-react";

// Sprite cell (transparent background PNG with mono label)
const Sprite = ({ src, label }) => (
  <div className="flex flex-col items-center gap-1.5">
    <div
      className="w-24 h-24 rounded-lg flex items-center justify-center relative overflow-hidden"
      style={{
        background:
          "repeating-conic-gradient(#1E201E 0deg 90deg, #131A14 90deg 180deg) 0 0/16px 16px",
        border: "1px solid #2A3F2D",
      }}
      data-testid={`sprite-${label.toLowerCase().replace(/\s+/g, "-")}`}
    >
      <img
        src={src}
        alt={label}
        className="w-[85%] h-[85%] object-contain"
        style={{ imageRendering: "auto" }}
      />
      {/* corner marks */}
      {["top-1 left-1", "top-1 right-1", "bottom-1 left-1", "bottom-1 right-1"].map((c) => (
        <span key={c} className={`absolute ${c} w-2 h-2 border border-cyan-mist/60`} />
      ))}
    </div>
    <p className="font-mono text-[9px] tracking-widest text-cyan-mist/80 uppercase text-center">
      {label}
    </p>
  </div>
);

const Row = ({ title, sprites }) => (
  <div className="space-y-2">
    <div className="flex items-baseline justify-between">
      <h3 className="font-display text-sm font-bold text-bone tracking-widest">
        {title}
      </h3>
      <span className="font-mono text-[10px] text-stone-pale">
        × {sprites.length}
      </span>
    </div>
    <div className="rune-divider" />
    <div className="grid grid-cols-3 gap-3">
      {sprites.map((s, i) => (
        <Sprite key={i} src={s.src} label={s.label} />
      ))}
    </div>
  </div>
);

export default function SpriteSheetScreen() {
  const navigate = useNavigate();

  const rows = [
    {
      title: "PLAYER — Red Scarf Explorer",
      sprites: [
        { src: IMG.player_idle, label: "player_idle" },
        { src: IMG.player_attack, label: "player_attack" },
        { src: IMG.player_hurt, label: "player_hurt" },
      ],
    },
    {
      title: "BOSS — Stone Deity Guardian",
      sprites: [
        { src: IMG.boss_idle, label: "boss_idle" },
        { src: IMG.boss_attack, label: "boss_attack" },
        { src: IMG.boss_hurt, label: "boss_hurt" },
      ],
    },
    {
      title: "MONSTERS",
      sprites: [
        { src: IMG.monster1_idle, label: "vinegoblin_idle" },
        { src: IMG.monster1_hit, label: "vinegoblin_hit" },
        { src: IMG.monster2_idle, label: "stoneskull_idle" },
        { src: IMG.monster2_hit, label: "stoneskull_hit" },
        { src: IMG.monster3_idle, label: "ruinbug_idle" },
        { src: IMG.monster3_hit, label: "ruinbug_hit" },
      ],
    },
    {
      title: "NPCs",
      sprites: [
        { src: IMG.npc1_a, label: "sage_a" },
        { src: IMG.npc1_b, label: "sage_b" },
        { src: IMG.npc2_a, label: "merchant_a" },
        { src: IMG.npc2_b, label: "merchant_b" },
      ],
    },
    {
      title: "PROPS",
      sprites: [
        { src: IMG.prop_chest, label: "relic_chest" },
        { src: IMG.prop_statue, label: "deity_statue" },
        { src: IMG.prop_plant, label: "biolum_plant" },
      ],
    },
  ];

  return (
    <MotionScreen>
      <div className="absolute inset-0 bg-moss-radial">
        <div className="absolute inset-0 noise pointer-events-none" />
      </div>

      <div className="absolute top-0 left-0 right-0 z-30 p-3">
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate("/")}
            className="w-10 h-10 rounded-full carved-stone flex items-center justify-center"
            data-testid="btn-back-map"
          >
            <ArrowLeft className="w-5 h-5 text-cyan-mist" />
          </button>
          <div className="glass-panel flex-1 px-3 py-1.5 flex items-center justify-between">
            <span className="font-display text-sm font-bold tracking-widest text-bone">
              SPRITE SHEET
            </span>
            <span className="font-mono text-[10px] text-cyan-mist tracking-widest">
              EXPORT.PNG
            </span>
          </div>
        </div>
      </div>

      <div
        className="relative w-full overflow-y-auto pt-16 pb-8 px-3 space-y-5"
        style={{ height: "100%" }}
        data-testid="spritesheet-scroll"
      >
        {/* Instructions */}
        <div className="glass-panel p-3">
          <p className="font-mono text-[10px] text-cyan-mist/90 tracking-widest uppercase">
            Engine handoff
          </p>
          <p className="font-body text-xs text-stone-pale mt-1 leading-relaxed">
            Every sprite is a transparent PNG rendered on a checker matte for alpha inspection.
            Files live at <span className="text-cyan-mist font-mono">/generated/*.png</span> —
            drag them into your atlas packer or import as individual textures.
          </p>
          <a
            href={IMG.player_idle}
            download
            className="btn-cyan mt-3 !py-2 !px-3 inline-flex"
            data-testid="btn-download-example"
          >
            <Download className="w-4 h-4" />
            Download Sample
          </a>
        </div>

        {rows.map((row) => (
          <Row key={row.title} title={row.title} sprites={row.sprites} />
        ))}

        <div className="pb-4" />
      </div>
    </MotionScreen>
  );
}
