/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./src/**/*.{js,jsx,ts,tsx}", "./public/index.html"],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Cinzel Decorative"', 'serif'],
        heading: ['"Cinzel"', 'serif'],
        body: ['"Lora"', 'serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        // dungeon palette (locked)
        moss: {
          darkest: '#0B120C',
          dark: '#131A14',
          mid: '#1C2A1E',
          light: '#2A3F2D',
          bright: '#3F5A42',
        },
        stone: {
          darkest: '#141614',
          dark: '#1E201E',
          mid: '#363A36',
          light: '#4F554F',
          pale: '#8A928A',
        },
        earth: {
          brown: '#382918',
          tan: '#6B5138',
        },
        bone: '#E8EDE6',
        cyan: {
          mist: '#00E5FF',
          deep: '#0891A0',
        },
        ember: {
          orange: '#FF6B35',
          deep: '#B44420',
          gold: '#F5B942',
        },
        // shadcn tokens (kept but recolored for dark theme)
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      backgroundImage: {
        'moss-radial': 'radial-gradient(ellipse at center, #1C2A1E 0%, #0B120C 70%)',
        'cavern-radial': 'radial-gradient(ellipse at 50% 30%, #2A1D15 0%, #0B0906 80%)',
      },
      boxShadow: {
        'cyan-glow': '0 0 20px rgba(0,229,255,0.6), 0 0 40px rgba(0,229,255,0.25)',
        'ember-glow': '0 0 20px rgba(255,107,53,0.65), 0 0 40px rgba(255,107,53,0.3)',
        'inset-stone': 'inset 0 3px 0 rgba(255,255,255,0.06), inset 0 -3px 0 rgba(0,0,0,0.6), 0 6px 14px rgba(0,0,0,0.6)',
      },
      keyframes: {
        'accordion-down': { from: { height: '0' }, to: { height: 'var(--radix-accordion-content-height)' } },
        'accordion-up': { from: { height: 'var(--radix-accordion-content-height)' }, to: { height: '0' } },
        'ember-drift': {
          '0%': { transform: 'translateY(0) translateX(0)', opacity: '0' },
          '30%': { opacity: '1' },
          '100%': { transform: 'translateY(-90px) translateX(12px)', opacity: '0' },
        },
        'cyan-pan': {
          '0%': { backgroundPosition: '0% 50%' },
          '100%': { backgroundPosition: '200% 50%' },
        },
        'glow-pulse': {
          '0%,100%': { boxShadow: '0 0 10px rgba(0,229,255,0.5)' },
          '50%': { boxShadow: '0 0 28px rgba(0,229,255,0.9), 0 0 60px rgba(0,229,255,0.35)' },
        },
        'ember-pulse': {
          '0%,100%': { boxShadow: '0 0 12px rgba(255,107,53,0.55)' },
          '50%': { boxShadow: '0 0 30px rgba(255,107,53,0.95), 0 0 60px rgba(255,107,53,0.4)' },
        },
        'idle-bob': {
          '0%,100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-6px)' },
        },
        'sway': {
          '0%,100%': { transform: 'rotate(-2deg)' },
          '50%': { transform: 'rotate(2deg)' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'ember-drift': 'ember-drift 3.6s linear infinite',
        'cyan-pan': 'cyan-pan 12s linear infinite',
        'glow-pulse': 'glow-pulse 2.4s ease-in-out infinite',
        'ember-pulse': 'ember-pulse 2.4s ease-in-out infinite',
        'idle-bob': 'idle-bob 2.2s ease-in-out infinite',
        'sway': 'sway 4s ease-in-out infinite',
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
