import React, { createContext, useContext } from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import { INTER_B64 } from "./fontInter";

/**
 * Light brand kit: white canvas, soft pink→purple→blue blobs, white cards, Inter.
 * Everything is designed on a 1376x774 artboard and scaled to the target size.
 */
export const ART_W = 1180;
export const ART_H = 664;

export const L = {
  ink: "var(--ink)",
  ink2: "var(--ink2)",
  muted: "var(--muted)",
  line: "rgba(150, 105, 75, 0.16)",
  card: "var(--card)",
  pink: "#D97757",
  purple: "#D97757",
  violet: "#C15F3C",
  blue: "#D97757",
  soft: "#FAF6F1",
};
// Solid accent (Claude orange). Kept as a "gradient" string so background-clip text still works.
export const GRAD = "linear-gradient(90deg, #D97757 0%, #D97757 100%)";
export const GRAD_D = GRAD;
export const FONT = "Inter, 'Segoe UI', sans-serif";

const css = `@font-face{font-family:"Inter";font-weight:100 900;font-display:block;src:url(data:font/ttf;base64,${INTER_B64}) format("truetype");}`;
if (typeof document !== "undefined" && !document.querySelector("style[data-fonts=inter]")) {
  const s = document.createElement("style");
  s.setAttribute("data-fonts", "inter");
  s.textContent = css;
  document.head.appendChild(s);
}

/** Two looks: light (beige) and dark (Anthropic charcoal). Colours flow through CSS variables. */
export const DarkCtx = createContext(false);
export const useDark = () => useContext(DarkCtx);
export const themeVars = (dark: boolean): React.CSSProperties =>
  (dark
    // dark surfaces get a light touch of depth (the chapter list goes further, see learn.tsx): a
    // faintly top-lit fill, a soft top-edge highlight, a hairline border, a modest drop shadow
    ? { "--ink": "#FAF9F5", "--ink2": "#C9C5BC", "--muted": "#9A968E", "--faint": "#6B6760", "--tileic": "#E8916F",
        "--card": "linear-gradient(180deg, #2A2927 0%, #232220 100%)",
        "--cardshadow": "inset 0 1px 0 rgba(255,255,255,0.05), inset 0 0 0 1px rgba(255,255,255,0.05), 0 10px 28px rgba(0,0,0,0.32)",
        "--glowshadow": "inset 0 1px 0 rgba(255,255,255,0.07), 0 0 0 1.5px rgba(217,119,87,0.7), 0 0 26px rgba(217,119,87,0.28), 0 12px 30px rgba(0,0,0,0.35)",
        "--pill": "linear-gradient(180deg, #2F2D2B 0%, #282725 100%)",
        "--pillshadow": "inset 0 1px 0 rgba(255,255,255,0.05), 0 0 0 1px rgba(255,255,255,0.06), 0 4px 12px rgba(0,0,0,0.3)",
        "--tile": "linear-gradient(180deg, #3A322D 0%, #2D2723 100%)",
        "--tileshadow": "inset 0 1px 0 rgba(255,255,255,0.06), 0 0 0 1px rgba(217,119,87,0.18), 0 3px 8px rgba(0,0,0,0.3)",
        "--deepcard": "linear-gradient(180deg, #2F2E2C 0%, #252422 55%, #1F1E1D 100%)",
        "--deepshadowcard": "inset 0 1px 0 rgba(255,255,255,0.09), inset 0 0 0 1px rgba(255,255,255,0.05), 0 1px 2px rgba(0,0,0,0.5), 0 12px 26px rgba(0,0,0,0.38), 0 34px 74px rgba(0,0,0,0.58)",
        "--bar": "linear-gradient(180deg, #2A2826 0%, #343230 100%)", "--ring": "rgba(255,255,255,0.12)", "--deepshadow": "0 24px 56px rgba(0,0,0,0.45)" }
    : { "--ink": "#141413", "--ink2": "#5E5D59", "--muted": "#8F8B85", "--faint": "#B9B4C6", "--tileic": "#C15F3C",
        "--card": "linear-gradient(180deg, #FFFFFF 0%, #FBF8F4 100%)",
        "--cardshadow": "inset 0 1px 0 rgba(255,255,255,0.9), 0 0 0 1px rgba(150,105,75,0.10), 0 2px 4px rgba(80,50,30,0.06), 0 16px 40px rgba(80,50,30,0.14)",
        "--glowshadow": "0 0 0 2px rgba(217,119,87,0.45), 0 18px 50px rgba(217,119,87,0.28)",
        "--pill": "rgba(255,255,255,0.92)", "--pillshadow": "0 6px 18px rgba(80,50,30,0.10), 0 0 0 1px rgba(150,105,75,0.14)",
        "--tile": "#F6E7DD", "--tileshadow": "inset 0 0 0 1px rgba(217,119,87,0.15)",
        "--deepcard": "linear-gradient(180deg, #FFFFFF 0%, #FBF8F4 100%)", "--deepshadowcard": "0 0 0 1px rgba(150,105,75,0.10), 0 16px 40px rgba(80,50,30,0.16)",
        "--bar": "#DCC3AF", "--ring": "#FFFFFF", "--deepshadow": "0 40px 80px rgba(80,50,30,0.28)" }) as React.CSSProperties;

export const ease = Easing.bezier(0.22, 1, 0.36, 1);

/** 0→1 spring that starts at `delay` frames. */
export const useIn = (delay = 0, damping = 18, stiffness = 120) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: f - delay, fps, config: { damping, stiffness, mass: 0.9 } });
};

export const lerp = (p: number, a: number, b: number) => a + (b - a) * p;

/** Soft drifting colour blobs on white — the background of every scene. */
export const BlobBg: React.FC<{ seed?: number; strength?: number }> = ({ seed = 0, strength = 1 }) => {
  const f = useCurrentFrame();
  const t = f / 30;
  const blob = (cx: number, cy: number, r: number, color: string, k: number) => {
    const x = cx + Math.sin(t * 0.35 + k + seed) * 60;
    const y = cy + Math.cos(t * 0.28 + k * 1.3 + seed) * 40;
    return (
      <div
        style={{
          position: "absolute",
          left: x - r,
          top: y - r,
          width: r * 2,
          height: r * 2,
          borderRadius: "50%",
          background: color,
          filter: "blur(90px)",
          opacity: 0.6 * strength,
        }}
      />
    );
  };
  if (useDark()) {
    // dark theme (default): near-black charcoal, a warm clay glow pooling up from the bottom edge,
    // the corners falling off into shadow
    const breathe = 0.85 + 0.15 * Math.sin(t * 0.6 + seed);
    return (
      <div style={{ position: "absolute", inset: 0, background: "#161514", overflow: "hidden" }}>
        <div style={{ position: "absolute", inset: 0, background: `radial-gradient(75% 55% at ${50 + Math.sin(t * 0.25 + seed) * 6}% 112%, rgba(217,119,87,${0.42 * breathe}) 0%, rgba(140,62,36,0.22) 38%, rgba(26,25,24,0) 72%)` }} />
        <div style={{ position: "absolute", inset: 0, background: "radial-gradient(120% 90% at 50% 40%, rgba(255,255,255,0.035) 0%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.45) 100%)" }} />
      </div>
    );
  }
  return (
    <div style={{ position: "absolute", inset: 0, background: "linear-gradient(135deg, #F7F3EC 0%, #F5EBE0 55%, #F4DDCB 100%)", overflow: "hidden" }}>
      {blob(220, 560, 260, "#F2C9AE", 0)}
      {blob(620, 330, 240, "#F8E6D6", 2)}
      {blob(1000, 150, 260, "#F1D3BD", 4)}
      {blob(1010, 640, 200, "#EFC0A2", 6)}
    </div>
  );
};

export const GradText: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <span
    style={{
      background: GRAD,
      WebkitBackgroundClip: "text",
      backgroundClip: "text",
      color: "transparent",
      paddingBottom: "0.08em",
      ...style,
    }}
  >
    {children}
  </span>
);

export const Card: React.FC<{ style?: React.CSSProperties; children?: React.ReactNode; glow?: boolean }> = ({ style, children, glow }) => (
  <div
    style={{
      background: L.card,
      borderRadius: 24,
      boxShadow: glow ? "var(--glowshadow)" : "var(--cardshadow)",
      ...style,
    }}
  >
    {children}
  </div>
);

export const Pill: React.FC<{ children: React.ReactNode; active?: boolean; style?: React.CSSProperties }> = ({ children, active, style }) => (
  <div
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 10,
      padding: "10px 22px",
      borderRadius: 999,
      fontFamily: FONT,
      fontSize: 22,
      fontWeight: 600,
      lineHeight: 1.3,
      color: active ? "#fff" : L.ink2,
      background: active ? GRAD : "var(--pill)",
      boxShadow: active ? "0 8px 22px rgba(217,119,87,0.32)" : "var(--pillshadow)",
      ...style,
    }}
  >
    {children}
  </div>
);

export const Kicker: React.FC<{ text?: string; delay?: number }> = ({ text, delay = 0 }) => {
  const p = useIn(delay);
  if (!text) return null;
  // a label, not a button: small spaced capitals behind a clay dot, no capsule around it
  return (
    <div style={{ opacity: p, transform: `translateY(${(1 - p) * 14}px)`, display: "flex", alignItems: "center", gap: 10, fontFamily: FONT,
      fontSize: 17, fontWeight: 700, letterSpacing: "0.16em", textTransform: "uppercase", color: L.muted }}>
      <span style={{ width: 8, height: 8, borderRadius: 4, background: GRAD }} />
      {text}
    </div>
  );
};

/** Words blur in one by one (sample 2). Words wrapped in *stars* get the gradient. */
export const Words: React.FC<{ text: string; delay?: number; per?: number; size?: number; weight?: number; color?: string; align?: "left" | "center"; lineHeight?: number }> = ({
  text,
  delay = 0,
  per = 3,
  size = 64,
  weight = 700,
  color = L.ink,
  align = "center",
  lineHeight = 1.24,
}) => {
  const f = useCurrentFrame();
  const parts: { w: string; g: boolean }[] = [];
  let grad = false;
  for (const raw of text.split(/\s+/).filter(Boolean)) {
    let w = raw;
    let open = false;
    let close = false;
    if (w.startsWith("*")) { open = true; w = w.slice(1); }
    // closing star may be followed by punctuation: "*gói định kỳ*," → "gói định kỳ,"
    const m = w.match(/^(.*)\*([^\p{L}\p{N}*]*)$/u);
    if (m) { close = true; w = m[1] + m[2]; }
    if (open) grad = true;
    parts.push({ w, g: grad });
    if (close) grad = false;
  }
  return (
    <div style={{ fontFamily: FONT, fontSize: size, fontWeight: weight, lineHeight, letterSpacing: "-0.02em", color, textAlign: align, padding: "6px 0" }}>
      {parts.map((p, i) => {
        const t = interpolate(f - delay - i * per, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
        const st: React.CSSProperties = {
          display: "inline-block",
          opacity: t,
          filter: `blur(${(1 - t) * 10}px)`,
          transform: `translateY(${(1 - t) * 18}px)`,
          marginRight: "0.26em",
        };
        return p.g ? (
          <span key={i} style={st}>
            <GradText>{p.w}</GradText>
          </span>
        ) : (
          <span key={i} style={st}>{p.w}</span>
        );
      })}
    </div>
  );
};

/** Characters typed in with a gradient caret (sample 1 input). */
export const Typed: React.FC<{ text: string; delay?: number; cps?: number; style?: React.CSSProperties; caret?: boolean }> = ({ text, delay = 0, cps = 28, style, caret = true }) => {
  const f = useCurrentFrame();
  const n = Math.max(0, Math.min(text.length, Math.floor(((f - delay) / 30) * cps)));
  const blink = Math.floor(f / 15) % 2 === 0;
  return (
    <span style={{ fontFamily: FONT, ...style }}>
      {text.slice(0, n)}
      {caret && n < text.length + 1 ? (
        <span style={{ display: "inline-block", width: 3, height: "1.05em", marginLeft: 2, verticalAlign: "-0.15em", background: GRAD, opacity: blink || n < text.length ? 1 : 0 }} />
      ) : null}
    </span>
  );
};

/** Pointer hand that glides to (x,y) and taps at frame `at`. */
export const Cursor: React.FC<{ fromX: number; fromY: number; x: number; y: number; at: number }> = ({ fromX, fromY, x, y, at }) => {
  const f = useCurrentFrame();
  const move = interpolate(f, [at - 22, at], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const tap = interpolate(f, [at, at + 4, at + 10], [1, 0.84, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const ring = interpolate(f, [at, at + 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const vis = interpolate(f, [at - 30, at - 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const cx = lerp(move, fromX, x);
  const cy = lerp(move, fromY, y);
  return (
    <div style={{ position: "absolute", left: 0, top: 0, pointerEvents: "none", opacity: vis }}>
      {f >= at ? (
        <div style={{ position: "absolute", left: x - 40 * ring, top: y - 40 * ring, width: 80 * ring, height: 80 * ring, borderRadius: "50%", border: `3px solid ${L.purple}`, opacity: 1 - ring }} />
      ) : null}
      <svg width="54" height="60" viewBox="0 0 24 26" style={{ position: "absolute", left: cx - 14, top: cy - 4, transform: `scale(${tap})`, filter: "drop-shadow(0 6px 10px rgba(120,60,30,0.35))" }}>
        <path d="M9 11V4.5a1.5 1.5 0 0 1 3 0V10m0-.5V3a1.5 1.5 0 0 1 3 0v6.5m0-1a1.5 1.5 0 0 1 3 0V10m0-.5a1.5 1.5 0 0 1 3 0V15a7 7 0 0 1-7 7h-1.2a7 7 0 0 1-5.4-2.6L3.3 15.6a1.6 1.6 0 0 1 2.4-2.1L9 16" fill="#fff" stroke={L.purple} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </div>
  );
};

/** Rings were tried and dropped (too busy); kept as a no-op so templates need no changes. */
export const Rings: React.FC<{ w: number; h: number; delay?: number }> = () => null;

/** Fills the artboard; scenes position their content inside. */
export const Stage: React.FC<{ children: React.ReactNode; seed?: number; pad?: number; center?: boolean }> = ({ children, seed = 0, pad = 40, center = true }) => (
  <div style={{ position: "absolute", inset: 0, fontFamily: FONT, color: L.ink }}>
    <BlobBg seed={seed} />
    <div
      style={{
        position: "absolute",
        inset: pad,
        display: "flex",
        flexDirection: "column",
        alignItems: center ? "center" : "stretch",
        justifyContent: "center",
        gap: 26,
      }}
    >
      {children}
    </div>
  </div>
);
