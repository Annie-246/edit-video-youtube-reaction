import React from "react";
import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Card, Cursor, FONT, Typed, Words, ease, useDark, useIn } from "./kit";
import { Icon } from "./icons";
import type { TplProps } from "./templates";

/**
 * Studio set: motion learned from agency reels (swipe carousels, colour strips, floating cards,
 * giant type, pill stacks, orbits, a typing bar over a photo, a product UI tilted in 3D),
 * redrawn in the clay palette. Every scene has a light and a dark look (Main alternates them,
 * "dark": true/false pins one). Positions are fractions of the frame so any artboard height works.
 */

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const C = { clay: "#D97757", light: "#F0B49A", deep: "#B5532F", rust: "#C15F3C", sand: "#F4DDCB", cream: "#F7F3EC", coal: "#1F1E1D", ink: "#141413", ink2: "#5E5D59" };
const RIM = `linear-gradient(135deg, ${C.light} 0%, ${C.clay} 50%, ${C.deep} 100%)`;
const SHADES = [C.clay, C.sand, C.deep, C.light, C.coal, C.rust, "#E8A383", "#FAF6F1"];
const W = 1180;
const pick = (list: string[], i: number) => (list.length ? list[((i % list.length) + list.length) % list.length] : "");

/** The two looks every studio scene is drawn in. */
const useTone = () => {
  const d = useDark();
  return d
    ? { dark: true, bg: C.coal, field: `radial-gradient(90% 90% at 50% 30%, #2C2A28 0%, ${C.coal} 70%)`, ink: C.cream, sub: "#C9C5BC", card: "#2A2927", soft: "rgba(255,255,255,0.06)",
        line: "rgba(240,180,154,0.28)", shadow: "rgba(0,0,0,0.5)", glow: 0.32 }
    : { dark: false, bg: C.cream, field: `radial-gradient(90% 90% at 50% 30%, #FFFFFF 0%, ${C.cream} 60%, ${C.sand} 100%)`, ink: C.ink, sub: C.ink2, card: "#FFFFFF", soft: "#FAF6F1",
        line: "rgba(181,83,47,0.22)", shadow: "rgba(80,40,20,0.20)", glow: 0.18 };
};

const Glow: React.FC<{ x: string; y: string; size: number; color: string; o?: number }> = ({ x, y, size, color, o = 0.5 }) => {
  const f = useCurrentFrame();
  return <div style={{ position: "absolute", left: x, top: y, width: size, height: size, marginLeft: -size / 2 + Math.sin(f / 40) * 30, marginTop: -size / 2,
    borderRadius: "50%", background: color, filter: "blur(90px)", opacity: o }} />;
};

const Chip: React.FC<{ text?: string; delay?: number; low?: boolean }> = ({ text, delay = 6, low }) => {
  const p = useIn(delay);
  const T = useTone();
  if (!text) return null;
  return (
    <div style={{ position: "absolute", left: 40, ...(low ? { bottom: 30 } : { top: 36 }), opacity: p, transform: `translateY(${(1 - p) * -16}px)`, zIndex: 60, display: "flex", alignItems: "center", gap: 10,
      padding: "10px 22px", borderRadius: 99, fontSize: 22, fontWeight: 650, color: T.ink, background: T.dark ? "rgba(42,41,39,0.85)" : "rgba(255,255,255,0.92)",
      boxShadow: T.dark ? "0 0 0 1px rgba(255,255,255,0.12)" : "0 8px 24px rgba(80,50,30,0.12)" }}>
      <span style={{ width: 10, height: 10, borderRadius: 5, background: RIM }} />{text}
    </div>
  );
};

/* ---------- swipe: rows of portrait shots glide sideways; a shot swells as it crosses its row's focus ---------- */
const SwipeT: React.FC<TplProps> = ({ images = [], kicker, rows = 3 }) => {
  const f = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const T = useTone();
  const artH = W * height / width;
  const list = images as string[];
  const n = Math.max(2, Math.min(4, Number(rows)));
  const ch = Math.round(artH * (n > 3 ? 0.17 : 0.22)), cw = Math.round(ch * 0.5), gap = 20, step = cw + gap, count = Math.ceil(W / step) + 3;
  const enter = interpolate(f, [0, 20], [0, 1], { ...clamp, easing: ease });
  return (
    <AbsoluteFill style={{ background: T.bg, fontFamily: FONT, overflow: "hidden" }}>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", justifyContent: "center", gap: artH * (n > 3 ? 0.055 : 0.08) }}>
        {Array.from({ length: n }).map((_, r) => {
          const dir = r % 2 ? 1 : -1;
          const shift = dir * f * 2.2 + (1 - enter) * dir * -400 + r * 61;
          const focus = W * [0.3, 0.66, 0.46, 0.8][r];
          return (
            <div key={r} style={{ position: "relative", height: ch }}>
              {Array.from({ length: count }).map((__, i) => {
                const x = ((((i * step + shift) % (count * step)) + count * step) % (count * step)) - step;
                const d = (x + cw / 2 - focus) / (cw * 1.1);
                const s = 1 + 0.38 * Math.exp(-d * d);
                return (
                  <div key={i} style={{ position: "absolute", left: x, top: 0, width: cw, height: ch, borderRadius: 18, overflow: "hidden", transform: `scale(${s})`, zIndex: Math.round(s * 100),
                    boxShadow: `0 ${10 * s}px ${30 * s}px ${T.shadow}`, background: SHADES[(i + r) % SHADES.length] }}>
                    {list.length ? <Img src={pick(list, i * 2 + r * 3)} style={{ width: "100%", height: "100%", objectFit: "cover" }} /> : null}
                    <div style={{ position: "absolute", left: "50%", top: 8, width: 44, height: 12, marginLeft: -22, borderRadius: 8, background: "rgba(20,20,19,0.75)" }} />
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>
      <Chip text={kicker} low />
    </AbsoluteFill>
  );
};

/* ---------- strips: tall clay-tone strips rise in a fan, each with a label and a picture, then breathe ---------- */
const StripsT: React.FC<TplProps> = ({ items = [], title }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const T = useTone();
  const list = (items as { label: string; src?: string }[]).slice(0, 9);
  const sw = Math.min(150, 1060 / Math.max(1, list.length));
  const push = interpolate(f, [0, 200], [1, 1.07], clamp);
  // on the dark look the coal strip would vanish: swap it for cream
  const shades = T.dark ? SHADES.map((c) => (c === C.coal ? "#FAF6F1" : c)) : SHADES;
  return (
    <AbsoluteFill style={{ background: T.field, fontFamily: FONT, overflow: "hidden" }}>
      {T.dark ? <Glow x="50%" y="95%" size={700} color={C.clay} o={0.3} /> : null}
      {title ? <div style={{ position: "absolute", left: 0, right: 0, top: "6%", zIndex: 5 }}><Words text={title} delay={2} size={44} weight={800} color={T.ink} /></div> : null}
      <div style={{ position: "absolute", left: 0, right: 0, top: title ? "20%" : "10%", bottom: "8%", display: "flex", justifyContent: "center", alignItems: "center",
        transform: `perspective(1600px) rotateY(${interpolate(f, [0, 60], [-18, -6], { ...clamp, easing: ease })}deg) scale(${push})` }}>
        {list.map((it, i) => {
          const p = spring({ frame: f - 4 - i * 3, fps, config: { damping: 14, stiffness: 120 } });
          const bob = Math.sin((f + i * 9) / 18) * 10;
          const h = [86, 94, 80, 98, 88, 92, 82, 96, 90][i % 9];
          const bg = shades[i % shades.length];
          const darkStrip = bg === C.coal || bg === C.deep || bg === C.rust;
          return (
            <div key={i} style={{ width: sw, height: `${h}%`, marginLeft: i ? -6 : 0, background: bg, borderRadius: 6, position: "relative", overflow: "hidden", zIndex: i,
              transform: `translateY(${(1 - p) * 700 + bob}px) rotate(${(i - list.length / 2) * 0.8}deg)`, boxShadow: `-10px 0 30px ${T.shadow}` }}>
              <div style={{ padding: "16px 12px", fontSize: 17, fontWeight: 750, lineHeight: 1.2, color: darkStrip ? C.cream : C.ink }}>{it.label}</div>
              {it.src ? <Img src={it.src} style={{ position: "absolute", left: 10, right: 10, bottom: 12, width: sw - 20, height: "62%", objectFit: "cover", borderRadius: 4 }} /> : null}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/* ---------- float: plain photos drift at different depths; a line is typed inside a selection box ---------- */
const SPOTS = [[0.12, 0.2, 0.9], [0.36, 0.14, 1.1], [0.66, 0.16, 0.8], [0.86, 0.36, 1.0], [0.1, 0.62, 1.05], [0.36, 0.78, 0.85], [0.72, 0.72, 1.15], [0.9, 0.8, 0.75]];
const FloatT: React.FC<TplProps> = ({ images = [], title = "", kicker }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const T = useTone();
  const list = images as string[];
  const box = useIn(14);
  return (
    <AbsoluteFill style={{ background: T.field, fontFamily: FONT, overflow: "hidden" }}>
      <Glow x="20%" y="85%" size={520} color={C.clay} o={T.glow} />
      <Glow x="85%" y="10%" size={420} color={T.dark ? C.deep : C.light} o={T.glow} />
      {SPOTS.map(([x, y, z], i) => {
        const p = spring({ frame: f - i * 3, fps, config: { damping: 16, stiffness: 90 } });
        const dx = Math.sin((f + i * 20) / (40 + i * 4)) * 14 * z;
        const dy = Math.cos((f + i * 13) / (46 + i * 3)) * 12 * z;
        const w = 210 * z;
        // straight, square-cornered photos: the pictures carry the scene, no frames around them
        return (
          <div key={i} style={{ position: "absolute", left: `${x * 100}%`, top: `${y * 100}%`, width: w, height: w * 0.66, marginLeft: -w / 2, marginTop: -w * 0.33,
            transform: `translate(${dx}px, ${dy + (1 - p) * 120}px) scale(${0.6 + 0.4 * p})`, opacity: p, filter: `blur(${z < 0.85 ? 2 : 0}px)`,
            overflow: "hidden", background: SHADES[i % SHADES.length], boxShadow: `0 ${18 * z}px ${40 * z}px ${T.shadow}` }}>
            {list.length ? <Img src={pick(list, i)} style={{ width: "100%", height: "100%", objectFit: "cover" }} /> : null}
          </div>
        );
      })}
      <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ position: "relative", padding: "14px 28px", opacity: box, transform: `scale(${0.9 + 0.1 * box})`,
          background: T.dark ? "rgba(31,30,29,0.55)" : "rgba(255,255,255,0.72)", border: `2px dashed ${T.dark ? C.light : C.clay}` }}>
          {[[0, 0], [1, 0], [0, 1], [1, 1]].map(([a, b], k) => (
            <div key={k} style={{ position: "absolute", left: `calc(${a * 100}% - 7px)`, top: `calc(${b * 100}% - 7px)`, width: 12, height: 12, background: T.dark ? C.cream : "#fff", border: `2px solid ${C.clay}` }} />
          ))}
          <Typed text={title} delay={18} cps={22} style={{ fontSize: 58, fontWeight: 800, color: T.ink, letterSpacing: "-0.02em" }} />
        </div>
      </div>
      <Chip text={kicker} />
    </AbsoluteFill>
  );
};

/* ---------- bigtype: giant words slide behind; the middle line is the message ---------- */
const BigTypeT: React.FC<TplProps> = ({ text = "", echo }) => {
  const f = useCurrentFrame();
  const T = useTone();
  const back = (echo || text) + " · ";
  const row = (s: string, dir: number, speed: number, color: string, off: number) => (
    <div style={{ whiteSpace: "nowrap", fontSize: 190, fontWeight: 900, letterSpacing: "-0.04em", lineHeight: 1, color, transform: `translateX(${off + dir * f * speed}px)` }}>
      {s.repeat(4)}
    </div>
  );
  const p = useIn(4, 16, 140);
  // light: the clay field with cream type; dark: charcoal with clay echoes and cream type
  return (
    <AbsoluteFill style={{ background: T.dark ? C.coal : RIM, fontFamily: FONT, overflow: "hidden", justifyContent: "center" }}>
      {T.dark ? <Glow x="50%" y="50%" size={800} color={C.clay} o={0.22} /> : null}
      <div style={{ display: "flex", flexDirection: "column", gap: 10, transform: `rotate(-4deg) scale(${1.15 - 0.1 * p})` }}>
        {row(back, -1, 3, T.dark ? "rgba(217,119,87,0.28)" : "rgba(255,255,255,0.16)", -300)}
        <div style={{ opacity: p, whiteSpace: "nowrap", textAlign: "center", fontSize: Math.min(190, 1900 / Math.max(1, text.length)), fontWeight: 900, letterSpacing: "-0.04em", lineHeight: 1,
          color: C.cream, textShadow: T.dark ? "0 0 50px rgba(217,119,87,0.45)" : "0 12px 40px rgba(120,50,20,0.35)", transform: `translateX(${(f - 40) * 0.6}px) scale(${0.85 + 0.15 * p})` }}>{text}</div>
        {row(back, -1, 2.5, T.dark ? "rgba(255,255,255,0.07)" : "rgba(20,20,19,0.16)", -600)}
      </div>
    </AbsoluteFill>
  );
};

/* ---------- pills: pill buttons drop in one by one, icon side alternating, last one clay ---------- */
const PillsT: React.FC<TplProps> = ({ items = [], title }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const T = useTone();
  const list = (items as { icon?: string; label: string }[]).slice(0, 6);
  // the pill takes the opposite tone of the background
  const pillBg = T.dark ? C.cream : C.coal, pillInk = T.dark ? C.ink : C.cream, dot = T.dark ? C.coal : "#FAF9F5";
  return (
    <AbsoluteFill style={{ background: T.field, fontFamily: FONT, alignItems: "center", justifyContent: "center", gap: 36 }}>
      {T.dark ? <Glow x="50%" y="60%" size={600} color={C.clay} o={0.22} /> : null}
      {title ? <Words text={title} delay={2} size={46} weight={800} color={T.ink} /> : null}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 18 }}>
        {list.map((it, i) => {
          const d = 8 + i * 9;
          const p = spring({ frame: f - d, fps, config: { damping: 12, stiffness: 160 } });
          const right = i % 2 === 1;
          const last = i === list.length - 1;
          return (
            <div key={i} style={{ display: "flex", flexDirection: right ? "row-reverse" : "row", alignItems: "center", gap: 18, padding: right ? "10px 10px 10px 30px" : "10px 30px 10px 10px",
              borderRadius: 99, background: pillBg, color: pillInk, fontSize: 30, fontWeight: 650, opacity: Math.min(1, p * 1.5), marginLeft: (i % 3 - 1) * 26,
              transform: `translateY(${(1 - p) * 60}px) scale(${0.7 + 0.3 * p})`, filter: `blur(${(1 - Math.min(1, p)) * 8}px)`, boxShadow: `0 16px 30px ${T.shadow}` }}>
              <div style={{ width: 54, height: 54, borderRadius: 27, background: last ? RIM : dot, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Icon name={it.icon || "sparkle"} size={28} color={last ? "#fff" : pillBg} />
              </div>
              {it.label}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/* ---------- orbit: a hub with rings; avatars / logos circle it ---------- */
const OrbitT: React.FC<TplProps> = ({ center, icon = "globe", items = [], title }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const T = useTone();
  const list = (items as { src?: string; icon?: string; label?: string }[]).slice(0, 8);
  const hub = spring({ frame: f, fps, config: { damping: 12 } });
  const radii = [210, 300, 380];
  return (
    <AbsoluteFill style={{ background: T.field, fontFamily: FONT, overflow: "hidden" }}>
      <Glow x="50%" y="50%" size={600} color={C.clay} o={T.dark ? 0.25 : 0.15} />
      <div style={{ position: "absolute", left: "50%", top: title ? "46%" : "50%", width: 0, height: 0 }}>
        {radii.map((r, k) => {
          const p = interpolate(f, [4 + k * 5, 24 + k * 5], [0, 1], { ...clamp, easing: ease });
          return <div key={k} style={{ position: "absolute", left: -r, top: -r * 0.62, width: 2 * r, height: 2 * r * 0.62, borderRadius: "50%", border: `1.5px solid ${T.line}`, transform: `scale(${p})` }} />;
        })}
        <div style={{ position: "absolute", left: -70, top: -70, width: 140, height: 140, borderRadius: 70, background: RIM, transform: `scale(${hub})`, display: "flex", alignItems: "center", justifyContent: "center",
          boxShadow: `0 0 60px rgba(217,119,87,${T.dark ? 0.6 : 0.4})`, overflow: "hidden" }}>
          {center ? <div style={{ width: 112, height: 112, borderRadius: 56, background: "#fff", display: "flex", alignItems: "center", justifyContent: "center" }}><Img src={center} style={{ width: 76, height: 76, objectFit: "contain" }} /></div>
            : <Icon name={icon} size={70} color="#fff" />}
        </div>
        {list.map((it, i) => {
          // each ring spreads its own avatars evenly and turns as one, so two never meet
          const ring = i % radii.length, r = radii[ring];
          const inRing = Math.ceil((list.length - ring) / radii.length);
          const a = (Math.floor(i / radii.length) / inRing) * Math.PI * 2 + ring * 0.9 + f / (70 + ring * 20) * (ring % 2 ? -1 : 1);
          const p = spring({ frame: f - 14 - i * 4, fps, config: { damping: 12 } });
          const x = Math.cos(a) * r, y = Math.sin(a) * r * 0.62;
          return (
            <div key={i} style={{ position: "absolute", left: x - 38, top: y - 38, width: 76, height: 76, borderRadius: 38, padding: 3, background: RIM, transform: `scale(${p * (0.85 + 0.15 * Math.sin(a))})`, zIndex: Math.round(y + 400),
              boxShadow: `0 8px 24px ${T.shadow}` }}>
              <div style={{ width: "100%", height: "100%", borderRadius: 35, overflow: "hidden", background: "#fff", display: "flex", alignItems: "center", justifyContent: "center" }}>
                {it.src ? <Img src={it.src} style={{ width: "100%", height: "100%", objectFit: "cover" }} /> : <Icon name={it.icon || "user"} size={34} color={C.clay} />}
              </div>
            </div>
          );
        })}
      </div>
      {title ? <div style={{ position: "absolute", left: 0, right: 0, bottom: "6%" }}><Words text={title} delay={20} size={44} weight={800} color={T.ink} /></div> : null}
    </AbsoluteFill>
  );
};

/* ---------- typebar: a photo card, a white prompt bar types the line, a dot sends it ---------- */
const TypeBarT: React.FC<TplProps> = ({ src, text = "", kicker, dur }) => {
  const f = useCurrentFrame();
  const T = useTone();
  const card = useIn(0, 18, 110);
  const bar = useIn(10, 14, 140);
  const s = interpolate(f, [0, dur], [1.04, 1.14], clamp);
  return (
    <AbsoluteFill style={{ background: T.field, fontFamily: FONT, alignItems: "center", justifyContent: "center" }}>
      <Glow x="50%" y="100%" size={700} color={C.clay} o={T.glow} />
      <div style={{ position: "relative", width: "84%", height: "78%", borderRadius: 28, overflow: "hidden", transform: `scale(${0.92 + 0.08 * card})`, opacity: card,
        boxShadow: `0 0 0 2px rgba(240,180,154,0.5), 0 30px 80px ${T.shadow}` }}>
        {src ? <Img src={src} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", transform: `scale(${s})` }} /> : null}
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(31,30,29,0) 50%, rgba(31,30,29,0.55) 100%)" }} />
        {kicker ? <div style={{ position: "absolute", left: 28, top: 24, fontSize: 22, fontWeight: 700, color: C.cream, display: "flex", gap: 10, alignItems: "center" }}>
          <span style={{ width: 10, height: 10, borderRadius: 5, background: RIM }} />{kicker}</div> : null}
        <div style={{ position: "absolute", left: "50%", bottom: "9%", width: "80%", marginLeft: "-40%", transform: `translateY(${(1 - bar) * 60}px)`, opacity: bar }}>
          <div style={{ display: "flex", alignItems: "center", gap: 14, padding: "18px 18px 18px 30px", borderRadius: 99, background: "#fff", boxShadow: "0 20px 50px rgba(0,0,0,0.35)" }}>
            <div style={{ flex: 1, fontSize: text.length > 44 ? 22 : 28, fontWeight: 550, color: C.ink, whiteSpace: "nowrap", overflow: "hidden", display: "flex", justifyContent: "flex-end" }}><Typed text={text} delay={18} cps={26} /></div>
            <div style={{ width: 48, height: 48, borderRadius: 24, background: RIM, display: "flex", alignItems: "center", justifyContent: "center", flex: "none" }}><Icon name="arrow" size={24} color="#fff" /></div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ---------- ui3d: a product screen swings up from a 3D tilt, rows fill in, a side panel slides in,
   then the camera dives onto the call-to-action and the cursor taps it ---------- */
const UI3DT: React.FC<TplProps> = ({ app = "", title = "", rows = [], panel, cta = "", dur }) => {
  const f = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const T = useTone();
  const artH = W * height / width;
  const list = (rows as { label: string; value?: string; pct?: number }[]).slice(0, 4);
  const items = ((panel?.items || []) as string[]).slice(0, 4);
  const tilt = interpolate(f, [0, 30], [0, 1], { ...clamp, easing: ease });
  const dive = interpolate(f, [dur - 44, dur - 22], [0, 1], { ...clamp, easing: ease });
  const side = spring({ frame: f - 34, fps, config: { damping: 16 } });
  const tap = dur - 12;
  const row = T.dark ? "#33312E" : "#FAF6F1", track = T.dark ? "#4A4642" : "#EADBCB";
  return (
    <AbsoluteFill style={{ background: T.dark ? `radial-gradient(90% 90% at 70% 20%, #3A2A22 0%, ${C.coal} 60%)` : `radial-gradient(90% 90% at 70% 20%, ${C.sand} 0%, ${C.cream} 45%, #EADBCB 100%)`,
      fontFamily: FONT, overflow: "hidden" }}>
      <div style={{ position: "absolute", left: "50%", top: "50%", width: 980, height: 560, marginLeft: -490, marginTop: -280,
        transform: `perspective(1800px) translate(${-dive * 400}px, ${-dive * 390}px) scale(${0.82 + 0.12 * tilt + dive * 0.75}) rotateX(${lerp3(tilt, 58, 16) * (1 - dive)}deg) rotateZ(${lerp3(tilt, -22, -4) * (1 - dive)}deg)`,
        transformOrigin: "50% 50%", display: "flex", gap: 20 }}>
        <Card style={{ flex: 1, padding: 28, borderRadius: 22, display: "flex", flexDirection: "column", gap: 16, background: T.card }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, fontSize: 24, fontWeight: 800, color: T.ink }}>
            <div style={{ width: 34, height: 34, borderRadius: 10, background: RIM }} />{app}
          </div>
          <div style={{ fontSize: 30, fontWeight: 800, color: T.ink, letterSpacing: "-0.01em" }}>{title}</div>
          {list.map((r, i) => {
            const p = interpolate(f, [16 + i * 7, 30 + i * 7], [0, 1], { ...clamp, easing: ease });
            return (
              <div key={i} style={{ padding: "14px 18px", borderRadius: 14, background: row, border: `1px solid ${T.line}`, opacity: p, transform: `translateY(${(1 - p) * 20}px)` }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 20, fontWeight: 650, color: T.ink }}><span>{r.label}</span><span style={{ color: C.clay }}>{r.value}</span></div>
                <div style={{ marginTop: 10, height: 8, borderRadius: 4, background: track }}>
                  <div style={{ width: `${(r.pct ?? 60) * p}%`, height: "100%", borderRadius: 4, background: RIM }} />
                </div>
              </div>
            );
          })}
        </Card>
        {panel ? (
          <Card glow style={{ width: 330, padding: 24, borderRadius: 22, display: "flex", flexDirection: "column", gap: 12, background: T.card, transform: `translateX(${(1 - side) * 260}px)`, opacity: side }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 21, fontWeight: 800, color: T.ink }}><Icon name="sparkle" size={24} color={C.clay} />{panel.title}</div>
            {items.map((t, i) => {
              const p = interpolate(f, [44 + i * 6, 54 + i * 6], [0, 1], clamp);
              return <div key={i} style={{ fontSize: 18, color: T.sub, padding: "10px 14px", borderRadius: 12, background: row, opacity: p }}>{t}</div>;
            })}
            <div style={{ marginTop: "auto", alignSelf: "flex-start", padding: "12px 20px", borderRadius: 99, background: RIM, color: "#fff", fontSize: 19, fontWeight: 750,
              transform: `scale(${interpolate(f, [tap, tap + 4, tap + 10], [1, 0.9, 1], clamp)})` }}>{cta}</div>
          </Card>
        ) : null}
      </div>
      {panel ? <Cursor fromX={W * 0.8} fromY={artH + 60} x={W / 2 + 30} y={artH / 2 + 10} at={tap} /> : null}
    </AbsoluteFill>
  );
};
const lerp3 = (p: number, a: number, b: number) => a + (b - a) * p;

export const STUDIO: Record<string, React.FC<TplProps>> = {
  swipe: SwipeT, strips: StripsT, float: FloatT, bigtype: BigTypeT, pills: PillsT, orbit: OrbitT, typebar: TypeBarT, ui3d: UI3DT,
};
