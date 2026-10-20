import React from "react";
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { ART_W, FONT, Words } from "./kit";

/**
 * Showreel-grade full-frame cards, used sparingly: intro sting, chapter breaks, outro, and the
 * two warm-dark statement cards learnt from the Greg Isenberg sample (horizon, agenda).
 * Same palette as the rest of the kit: clay accent on warm charcoal, cream text.
 * Every template here draws its own dark background over the whole artboard.
 */
type P = Record<string, any> & { dur: number; seed: number };

const R = { deep: "#141413", dark: "#1F1E1D", clay: "#D97757", clayLight: "#F0B49A", clayDeep: "#B5532F", cream: "#FAF9F5", sand: "#F4DDCB" };
const GRAD = `linear-gradient(180deg, ${R.clayLight} 0%, ${R.clay} 50%, ${R.clayDeep} 100%)`;
const WARM_BG = `radial-gradient(110% 90% at 85% 5%, #5A2E1C 0%, ${R.dark} 55%, ${R.deep} 100%), ${R.deep}`;
const EXPO = Easing.bezier(0.16, 1, 0.3, 1);
const IN = Easing.bezier(0.7, 0, 0.84, 0);
const cl = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const lerp = (f: number, a: number[], b: number[], e = EXPO) => interpolate(f, a, b, { ...cl, easing: e });
// The artboard is 1180 wide and as tall as the frame needs (664 at 16:9, taller for the main
// frame or the bubble area), so vertical placement is relative to its real height.
const CX = ART_W / 2;

const Fill: React.FC<{ bg: string; children: React.ReactNode; style?: React.CSSProperties }> = ({ bg, children, style }) => (
  <div style={{ position: "absolute", inset: 0, background: bg, overflow: "hidden", fontFamily: FONT, color: R.cream, ...style }}>{children}</div>
);

/** Zoom-through exit over the last frames: the whole card rushes at the camera and blurs out. */
const useExit = (dur: number, n = 9) => {
  const f = useCurrentFrame();
  return { transform: `scale(${interpolate(f, [dur - n, dur], [1, 6], { ...cl, easing: IN })})`, filter: `blur(${interpolate(f, [dur - n, dur], [0, 8], { ...cl, easing: IN })}px)`, opacity: interpolate(f, [dur - 3, dur], [1, 0], cl) };
};

/* ---------- horizon: one statement over a glowing planet rim ---------- */
const HorizonT: React.FC<P> = ({ title = "", kicker }) => {
  const f = useCurrentFrame();
  const glow = 0.65 + 0.35 * Math.sin(f / 5);
  const D = 1600;
  return (
    <Fill bg={WARM_BG}>
      <div style={{ position: "absolute", left: CX - D / 2, top: "calc(100% - 264px)", width: D, height: D, borderRadius: "50%", transform: `translateY(${lerp(f, [0, 30], [320, 0])}px)`,
        background: `radial-gradient(circle at 50% 0%, ${R.clayLight} 0%, ${R.clay} 7%, #6E3320 28%, ${R.deep} 60%)`,
        boxShadow: `0 -12px ${56 * glow}px rgba(217,119,87,${0.75 * glow}), inset 0 3px 0 rgba(255,214,190,.95)` }} />
      <div style={{ position: "absolute", left: 60, right: 60, top: "22%", display: "flex", flexDirection: "column", alignItems: "center", gap: 14 }}>
        {kicker ? <div style={{ fontSize: 22, fontWeight: 600, letterSpacing: 6, textTransform: "uppercase", color: R.sand, opacity: lerp(f, [2, 10], [0, 1]) }}>{kicker}</div> : null}
        <Words text={title} delay={8} per={4} size={title.length > 50 ? 52 : 64} color={R.cream} />
      </div>
    </Fill>
  );
};

/* ---------- agenda: a list that builds line by line (new line grey, then cream) ---------- */
const AgendaT: React.FC<P> = ({ title, items = [], dur }) => {
  const f = useCurrentFrame();
  const list: string[] = items.map((x: any) => (typeof x === "string" ? x : x.label || x.title || ""));
  const step = Math.max(6, Math.min(20, Math.floor((dur - 24) / Math.max(1, list.length))));
  return (
    <Fill bg={WARM_BG}>
      <div style={{ position: "absolute", left: 150, right: 120, top: 0, bottom: 0, display: "flex", flexDirection: "column", justifyContent: "center", gap: 10 }}>
        {title ? <div style={{ fontSize: 24, fontWeight: 600, letterSpacing: 5, textTransform: "uppercase", color: R.sand, marginBottom: 14, opacity: lerp(f, [0, 8], [0, 1]) }}>{title}</div> : null}
        {list.map((t, k) => {
          const s = 6 + k * step;
          return (
            <div key={k} style={{ display: "flex", alignItems: "center", gap: 20, fontSize: list.length > 5 ? 38 : 46, fontWeight: 500, lineHeight: 1.3,
              opacity: lerp(f, [s, s + 6], [0, 1]), filter: `blur(${lerp(f, [s, s + 8], [8, 0])}px)`, transform: `translateY(${lerp(f, [s, s + 8], [14, 0])}px)`,
              color: f < s + 8 ? "#8F8B85" : R.cream }}>
              <span style={{ width: 13, height: 13, borderRadius: 99, flex: "none", background: R.clay, boxShadow: `0 0 16px ${R.clay}` }} />
              {t}
            </div>
          );
        })}
      </div>
    </Fill>
  );
};

/* ---------- chapter: big outlined number flies in, line draws, title reveals, zoom-through out ---------- */
const ChapterT: React.FC<P> = ({ num = "", kicker, title = "", dur }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: f, fps, config: { damping: 14, stiffness: 120 } });
  const exit = useExit(dur);
  return (
    <Fill bg={`radial-gradient(60% 60% at 50% 50%, rgba(217,119,87,${0.22 + 0.06 * Math.sin(f / 4)}) 0%, ${R.deep} 72%), ${R.deep}`}>
      <div style={{ position: "absolute", left: CX - 160, top: "50%", marginTop: -160, width: 320, height: 320, borderRadius: "50%", border: `4px solid ${R.clay}`, transform: `scale(${lerp(f, [0, 20], [0, 3.4])})`, opacity: lerp(f, [0, 20], [1, 0]) }} />
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", ...exit }}>
        {num !== "" ? (
          <div style={{ fontSize: 210, fontWeight: 900, lineHeight: 0.9, letterSpacing: -6, color: "transparent", WebkitTextStroke: `3px ${R.clay}`,
            transform: `scale(${lerp(p, [0, 1], [4, 1], Easing.linear)})`, opacity: lerp(f, [0, 6], [0, 1]), filter: `blur(${lerp(f, [0, 10], [10, 0])}px)` }}>
            {String(num).padStart(2, "0")}
          </div>
        ) : null}
        <div style={{ width: lerp(f, [10, 24], [0, 520]), height: 4, borderRadius: 9, background: GRAD, margin: "22px 0 18px", boxShadow: `0 0 20px ${R.clay}` }} />
        {kicker ? <div style={{ fontSize: 22, fontWeight: 600, letterSpacing: 8, textTransform: "uppercase", color: R.sand, opacity: lerp(f, [14, 22], [0, 1]) }}>{kicker}</div> : null}
        <div style={{ maxWidth: 1000 }}>
          <Words text={title} delay={16} per={3} size={title.length > 40 ? 50 : 62} color={R.cream} />
        </div>
      </div>
    </Fill>
  );
};

/* ---------- intro: dot stretches into a line, title letters slam in, zoom-through out ---------- */
const IntroT: React.FC<P> = ({ title = "", sub, dur }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const dot = spring({ frame: f, fps, config: { damping: 8, stiffness: 160 } });
  const exit = useExit(dur, 10);
  const chars = Array.from(title);
  const size = chars.length > 22 ? 70 : chars.length > 12 ? 96 : 140;
  const per = chars.length > 12 ? 1 : 2;   // long titles slam faster so the sub line gets its time
  const last = 22 + chars.length * per;
  return (
    <Fill bg={R.deep}>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", ...exit }}>
        <div style={{ position: "absolute", left: CX - lerp(f, [10, 22], [8, 460]), top: "50%", marginTop: -3 + lerp(f, [22, 34], [0, size * 0.62]), width: lerp(f, [10, 22], [16, 920]), height: lerp(f, [10, 22], [16, 4]),
          borderRadius: 99, background: GRAD, transform: `scale(${f < 10 ? dot : 1})`, boxShadow: `0 0 30px ${R.clay}` }} />
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", maxWidth: 1080 }}>
          {chars.map((ch, i) => {
            const s = 22 + i * per;
            const q = spring({ frame: f - s, fps, config: { damping: 11, stiffness: 210 } });
            return (
              <span key={i} style={{ display: "inline-block", whiteSpace: "pre", fontSize: size, fontWeight: 900, letterSpacing: -2, lineHeight: 1.1, opacity: f < s ? 0 : 1,
                transform: `translateY(${(1 - q) * size * 0.7}px) scale(${1 + (1 - q) * 0.6}) rotate(${(1 - q) * (i % 2 ? -12 : 12)}deg)`, filter: `blur(${lerp(f, [s, s + 7], [12, 0])}px)`,
                ...(i % 5 === 1 && ch.trim() ? { color: "transparent", WebkitTextStroke: `3px ${R.clay}` } : {}) }}>{ch}</span>
            );
          })}
        </div>
        {sub ? <div style={{ marginTop: size * 0.45 }}><Words text={sub} delay={last + 4} per={3} size={30} weight={500} color={R.sand} /></div> : null}
      </div>
    </Fill>
  );
};

/* ---------- outro: shockwave, masked letters rise with an echo trail, ends on the clay dot ---------- */
const OutroT: React.FC<P> = ({ title = "", sub, dur }) => {
  const f = useCurrentFrame();
  const chars = Array.from(title);
  const size = chars.length > 18 ? 80 : 120;
  const out = lerp(f, [dur - 12, dur - 4], [1, 0], IN);
  const letters = (stroke: boolean, delay: number) =>
    chars.map((L, i) => (
      <span key={i} style={{ display: "inline-block", overflow: "hidden", verticalAlign: "top", whiteSpace: "pre" }}>
        <span style={{ display: "inline-block", transform: `translateY(${lerp(f, [4 + delay + i * 1.5, 16 + delay + i * 1.5], [110, 0])}%)`,
          color: stroke ? "transparent" : R.cream, WebkitTextStroke: stroke ? `1.5px ${R.clay}` : undefined }}>{L}</span>
      </span>
    ));
  return (
    <Fill bg={`radial-gradient(60% 60% at 50% 50%, rgba(217,119,87,${0.26 + 0.08 * Math.sin(f / 4)}) 0%, ${R.deep} 70%), ${R.deep}`}>
      <div style={{ position: "absolute", left: CX - 130, top: "50%", marginTop: -130, width: 260, height: 260, borderRadius: "50%", border: `4px solid ${R.clay}`, transform: `scale(${lerp(f, [0, 22], [0, 5])})`, opacity: lerp(f, [0, 22], [1, 0]) }} />
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", opacity: out, transform: `scale(${0.4 + 0.6 * out})` }}>
        <div style={{ position: "relative", fontSize: size, fontWeight: 900, letterSpacing: -3, lineHeight: 1.05 }}>
          {[3, 2, 1].map((k) => (
            <div key={k} style={{ position: "absolute", inset: 0, transform: `translateY(${k * size * 0.12 * lerp(f, [22, 34], [0, 1])}px)`, opacity: 0.5 / k }}>{letters(true, 8 + k * 2)}</div>
          ))}
          <div style={{ position: "relative" }}>{letters(false, 0)}</div>
        </div>
        <div style={{ width: lerp(f, [14, 30], [0, 600]), height: 4, borderRadius: 9, background: GRAD, marginTop: 24, boxShadow: `0 0 20px ${R.clay}` }} />
        {sub ? <div style={{ fontSize: 24, fontWeight: 500, letterSpacing: 10, textTransform: "uppercase", color: R.sand, marginTop: 20, opacity: lerp(f, [24, 32], [0, 1]) }}>{sub}</div> : null}
      </div>
      <div style={{ position: "absolute", left: CX - 9, top: "50%", marginTop: -9, width: 18, height: 18, borderRadius: 99, background: GRAD, boxShadow: `0 0 26px ${R.clay}`, opacity: lerp(f, [dur - 6, dur - 2], [0, 1]) }} />
    </Fill>
  );
};

export const REEL: Record<string, React.FC<P>> = { horizon: HorizonT, agenda: AgendaT, chapter: ChapterT, intro: IntroT, outro: OutroT };
