import React from "react";
import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BlobBg, Card, FONT, Kicker, L, Words, ease, useIn } from "./kit";
import type { TplProps } from "./templates";

/**
 * Real pictures and logos, mostly placed by the `visuals` step: logo / logos when a brand is
 * named, stack / wall for photo moments (the plain Ken Burns `photo` lives in templates.tsx).
 */

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const RIM = "linear-gradient(135deg, #F0B49A 0%, #D97757 50%, #B5532F 100%)";

const Caption: React.FC<{ text?: string; kicker?: string; delay?: number }> = ({ text, kicker, delay = 10 }) => {
  const p = useIn(delay);
  if (!text) return null;
  return (
    <div style={{ position: "absolute", left: 40, bottom: 36, opacity: p, transform: `translateY(${(1 - p) * 20}px)`, zIndex: 50 }}>
      <Card style={{ padding: "14px 24px", borderRadius: 18, display: "flex", flexDirection: "column", gap: 4, maxWidth: 820 }}>
        {kicker ? <div style={{ fontSize: 18, fontWeight: 700, color: L.purple }}>{kicker}</div> : null}
        <div style={{ fontSize: 28, fontWeight: 650, lineHeight: 1.3, color: L.ink, display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ width: 10, height: 10, borderRadius: 5, background: RIM, flex: "none" }} />
          {text}
        </div>
      </Card>
    </div>
  );
};

/** White tile holding a logo, orange gradient rim, pops in with a little overshoot. */
const LogoTile: React.FC<{ src: string; size: number; delay: number }> = ({ src, size, delay }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: f - delay, fps, config: { damping: 11, stiffness: 150 } });
  const sweep = interpolate(f - delay, [10, 28], [-60, 160], clamp);
  return (
    <div style={{ position: "relative", width: size, height: size, transform: `scale(${p}) rotate(${(1 - p) * -14}deg)`, opacity: Math.min(1, p * 2) }}>
      <div style={{ position: "absolute", inset: -size * 0.35, borderRadius: "50%", background: "radial-gradient(closest-side, rgba(217,119,87,0.35), rgba(217,119,87,0))",
        transform: `scale(${interpolate(f - delay, [0, 30], [0.4, 1.1], clamp)})` }} />
      <div style={{ position: "absolute", inset: 0, borderRadius: size * 0.22, padding: 5, background: RIM, boxShadow: "0 24px 60px rgba(120,60,30,0.28)" }}>
        <div style={{ width: "100%", height: "100%", borderRadius: size * 0.22 - 5, background: "#fff", overflow: "hidden", position: "relative", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Img src={src} style={{ width: "72%", height: "72%", objectFit: "contain" }} />
          <div style={{ position: "absolute", top: 0, bottom: 0, left: `${sweep}%`, width: "35%", background: "linear-gradient(100deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.75) 50%, rgba(255,255,255,0) 100%)" }} />
        </div>
      </div>
    </div>
  );
};

/* ---------- logo: one brand, tile pops in, name writes beside it ---------- */
const LogoT: React.FC<TplProps> = ({ src, name = "", desc, seed }) => {
  const f = useCurrentFrame();
  const slide = interpolate(f, [8, 22], [0, 1], { ...clamp, easing: ease });
  return (
    <div style={{ position: "absolute", inset: 0, fontFamily: FONT, color: L.ink }}>
      <BlobBg seed={seed} />
      <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", gap: 56 * slide }}>
        <LogoTile src={src} size={280} delay={0} />
        <div style={{ maxWidth: 620 * slide, overflow: "hidden", whiteSpace: "nowrap" }}>
          <Words text={name} delay={14} per={4} size={name.length > 14 ? 64 : 84} weight={800} align="left" />
          {desc ? <Words text={desc} delay={24} per={2} size={28} weight={500} color={L.ink2} align="left" /> : null}
        </div>
      </div>
    </div>
  );
};

/* ---------- logos: several brands named together, tiles pop in a row ---------- */
const LogosT: React.FC<TplProps> = ({ items = [], title, kicker, seed }) => {
  const list = (items as { src: string; name: string }[]).slice(0, 5);
  const size = list.length > 3 ? 170 : 210;
  return (
    <div style={{ position: "absolute", inset: 0, fontFamily: FONT, color: L.ink }}>
      <BlobBg seed={seed} />
      <div style={{ position: "absolute", inset: 40, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 40 }}>
        <Kicker text={kicker} />
        {title ? <Words text={title} delay={2} size={48} /> : null}
        <div style={{ display: "flex", gap: 44, alignItems: "flex-start" }}>
          {list.map((it, i) => {
            const d = 4 + i * 7;
            return (
              <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 22 }}>
                <LogoTile src={it.src} size={size} delay={d} />
                <Words text={it.name} delay={d + 8} per={2} size={30} weight={700} />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

/* ---------- stack: photos fly in one by one and land on a pile ---------- */
const StackT: React.FC<TplProps> = ({ images = [], caption, kicker, dur, seed }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const list: string[] = (images as string[]).slice(0, 5);
  const each = Math.max(10, Math.min(18, (dur - 30) / Math.max(1, list.length)));
  const push = interpolate(f, [0, dur], [1, 1.08], clamp);
  return (
    <div style={{ position: "absolute", inset: 0, fontFamily: FONT, overflow: "hidden" }}>
      <BlobBg seed={seed} />
      <div style={{ position: "absolute", inset: 0, transform: `scale(${push})` }}>
        {list.map((im, i) => {
          const d = i * each;
          const p = spring({ frame: f - d, fps, config: { damping: 15, stiffness: 110 } });
          const side = i % 2 ? 1 : -1;
          const rot = [-6, 5, -3, 7, -2][i % 5];
          const dx = [-150, 140, -60, 90, 0][i % 5];
          const dy = [-30, 10, 40, -20, 0][i % 5];
          const sink = list.slice(i + 1).reduce((acc, _, j) => acc + spring({ frame: f - (i + 1 + j) * each, fps, config: { damping: 20 } }), 0);
          return (
            <div key={i} style={{ position: "absolute", left: "50%", top: "47%", width: 620, height: 420, marginLeft: -310, marginTop: -210, zIndex: i,
              opacity: f < d ? 0 : 1,
              transform: `translate(${dx + side * (1 - p) * 900}px, ${dy + (1 - p) * 120}px) rotate(${rot + side * (1 - p) * 25}deg) scale(${1 - sink * 0.04})`,
              filter: `brightness(${1 - sink * 0.06})` }}>
              <div style={{ width: "100%", height: "100%", background: "#fff", padding: 12, borderRadius: 18, boxShadow: "0 30px 70px rgba(80,40,20,0.30)" }}>
                <Img src={im} style={{ width: "100%", height: "100%", objectFit: "cover", borderRadius: 10 }} />
              </div>
            </div>
          );
        })}
      </div>
      <Caption text={caption} kicker={kicker} delay={14} />
    </div>
  );
};

/* ---------- wall: a tilted 3D wall of photos, columns scrolling in opposite directions ---------- */
const WallT: React.FC<TplProps> = ({ images = [], caption, kicker, title, dur }) => {
  const f = useCurrentFrame();
  const list: string[] = (images as string[]).length ? images : [];
  const cols = 5, rows = 6, tw = 300, th = 200, gap = 22;
  const intro = interpolate(f, [0, 24], [0, 1], { ...clamp, easing: ease });
  const tp = useIn(10);
  return (
    <AbsoluteFill style={{ background: "#1F1E1D", overflow: "hidden", fontFamily: FONT }}>
      <div style={{ position: "absolute", left: "50%", top: "50%", width: cols * (tw + gap), height: rows * (th + gap), marginLeft: -cols * (tw + gap) / 2, marginTop: -rows * (th + gap) / 2,
        transform: `perspective(1400px) rotateX(${22 - 6 * intro}deg) rotateZ(${-10 + 2 * intro}deg) scale(${1.25 - 0.1 * intro})`, display: "flex", gap }}>
        {Array.from({ length: cols }).map((_, c) => {
          const dir = c % 2 ? 1 : -1;
          const y = dir * interpolate(f, [0, dur], [0, 260], clamp) - (dir > 0 ? 260 : 0);
          return (
            <div key={c} style={{ display: "flex", flexDirection: "column", gap, transform: `translateY(${y}px)` }}>
              {Array.from({ length: rows + 2 }).map((__, r) => {
                const k = (c * 3 + r) % Math.max(1, list.length);
                const appear = interpolate(f, [2 + ((c * 7 + r * 3) % 14), 14 + ((c * 7 + r * 3) % 14)], [0, 1], clamp);
                return (
                  <div key={r} style={{ width: tw, height: th, borderRadius: 16, overflow: "hidden", opacity: appear, transform: `scale(${0.85 + 0.15 * appear})`, boxShadow: "0 16px 40px rgba(0,0,0,0.45)", background: "#2A2927" }}>
                    {list.length ? <Img src={list[k]} style={{ width: "100%", height: "100%", objectFit: "cover" }} /> : null}
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(70% 70% at 50% 50%, rgba(31,30,29,0) 40%, rgba(31,30,29,0.85) 100%)" }} />
      {title ? (
        <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", opacity: tp, transform: `scale(${0.9 + 0.1 * tp})` }}>
          <div style={{ padding: "22px 40px", borderRadius: 24, background: "rgba(31,30,29,0.78)", boxShadow: "0 0 0 2px rgba(217,119,87,0.6), 0 20px 60px rgba(0,0,0,0.5)" }}>
            <Words text={title} delay={12} size={54} weight={800} color="#FAF9F5" />
          </div>
        </div>
      ) : null}
      <Caption text={caption} kicker={kicker} delay={16} />
    </AbsoluteFill>
  );
};

export const MEDIA: Record<string, React.FC<TplProps>> = { logo: LogoT, logos: LogosT, stack: StackT, wall: WallT };
