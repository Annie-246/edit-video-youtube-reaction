import React from "react";
import { AbsoluteFill, Img, OffthreadVideo, interpolate, staticFile, useCurrentFrame } from "remotion";
import { ART_H, ART_W, BlobBg, Card, Cursor, FONT, GRAD, GradText, Kicker, L, Pill, Rings, Stage, Typed, Words, ease, lerp, useIn } from "./kit";
import { Icon, IconTile } from "./icons";
import { REEL } from "./reel";
import { MEDIA } from "./media";

type Any = Record<string, any>;
export type TplProps = Any & { dur: number; seed: number };

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const Title: React.FC<{ text?: string; delay?: number; size?: number; align?: "left" | "center" }> = ({ text, delay = 4, size = 52, align = "center" }) =>
  text ? <Words text={text} delay={delay} size={size} align={align} /> : null;

/* ---------- title: big statement, words blur in ---------- */
const TitleT: React.FC<TplProps> = ({ kicker, title, sub, seed }) => {
  const p = useIn(18 + (title || "").split(" ").length * 3);
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <div style={{ maxWidth: 1180 }}>
        <Words text={title || ""} delay={6} size={(title || "").length > 60 ? 58 : 72} />
      </div>
      {sub ? (
        <div style={{ opacity: p, transform: `translateY(${(1 - p) * 12}px)`, fontSize: 28, color: L.ink2, textAlign: "center", maxWidth: 1000, lineHeight: 1.4 }}>{sub}</div>
      ) : null}
    </Stage>
  );
};

/* ---------- tool: section opener "01 · Brag" ---------- */
const ToolT: React.FC<TplProps> = ({ num, name, tag, desc, icon, seed }) => {
  const f = useCurrentFrame();
  const p = useIn(0, 16);
  const q = useIn(10);
  const r = useIn(22);
  return (
    <Stage seed={seed}>
      <div style={{ display: "flex", alignItems: "center", gap: 46 }}>
        <div style={{ position: "relative", transform: `scale(${lerp(p, 0.7, 1)})`, opacity: p }}>
          <Rings w={230} h={230} delay={4} />
          <div style={{ position: "relative", width: 230, height: 230, borderRadius: 64, background: GRAD, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 24px 60px rgba(217,119,87,0.4)" }}>
            {icon ? <Icon name={icon} size={120} color="#fff" stroke={1.6} /> : <div style={{ fontSize: 120, fontWeight: 800, color: "#fff" }}>{num}</div>}
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 14, maxWidth: 760 }}>
          <div style={{ opacity: q, transform: `translateX(${(1 - q) * -20}px)`, fontSize: 30, fontWeight: 600, color: L.muted }}>Công cụ {num}/6</div>
          <div style={{ opacity: q, transform: `translateX(${(1 - q) * -30}px)`, fontSize: 104, fontWeight: 800, letterSpacing: "-0.03em", lineHeight: 1.1 }}>
            <GradText>{name}</GradText>
          </div>
          <div style={{ opacity: r, transform: `translateY(${(1 - r) * 12}px)`, fontSize: 30, color: L.ink2, lineHeight: 1.35 }}>{desc}</div>
          {tag ? (
            <div style={{ opacity: r, display: "flex", gap: 12, marginTop: 6 }}>
              {String(tag).split("·").map((t: string, i: number) => (
                <Pill key={i} style={{ fontSize: 20, padding: "8px 18px", transform: `translateY(${Math.sin(f / 20 + i) * 2}px)` }}>{t.trim()}</Pill>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </Stage>
  );
};

/* ---------- person: portrait + name card ---------- */
const PersonT: React.FC<TplProps> = ({ src, name, role, tags = [], seed, dur }) => {
  const f = useCurrentFrame();
  const p = useIn(0);
  const q = useIn(10);
  const zoom = interpolate(f, [0, dur], [1.04, 1.14], clamp);
  return (
    <Stage seed={seed}>
      <div style={{ display: "flex", alignItems: "center", gap: 56 }}>
        <Card glow style={{ width: 420, height: 520, overflow: "hidden", padding: 0, opacity: p, transform: `scale(${lerp(p, 0.9, 1)}) rotate(${lerp(p, -3, -1.5)}deg)` }}>
          {src ? <Img src={src} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${zoom})` }} /> : null}
        </Card>
        <div style={{ display: "flex", flexDirection: "column", gap: 16, maxWidth: 600 }}>
          <div style={{ opacity: q, fontSize: 84, fontWeight: 800, letterSpacing: "-0.03em", lineHeight: 1.12 }}>
            <GradText>{name}</GradText>
          </div>
          <div style={{ opacity: q, transform: `translateY(${(1 - q) * 12}px)`, fontSize: 32, color: L.ink2, lineHeight: 1.35 }}>{role}</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginTop: 8 }}>
            {(tags as string[]).map((t, i) => {
              const a = useIn(20 + i * 6);
              return <Pill key={i} active={i === 0} style={{ opacity: a, transform: `translateY(${(1 - a) * 14}px)` }}>{t}</Pill>;
            })}
          </div>
        </div>
      </div>
    </Stage>
  );
};

/* ---------- photo: Ken Burns sequence with caption chip ---------- */
const PhotoT: React.FC<TplProps> = ({ images = [], src, caption, kicker, dur }) => {
  const f = useCurrentFrame();
  const list: string[] = images.length ? images : src ? [src] : [];
  const each = dur / Math.max(1, list.length);
  const cp = useIn(8);
  return (
    <AbsoluteFill style={{ background: "#fff", overflow: "hidden" }}>
      {list.map((im, i) => {
        const lf = f - i * each;
        if (lf < -10 || lf > each + 12) return null;
        const o = interpolate(lf, [-10, 0], [0, 1], clamp);
        const s = interpolate(lf, [0, each + 12], [1.06, 1.16], clamp);
        const x = interpolate(lf, [0, each + 12], [i % 2 ? -20 : 20, i % 2 ? 20 : -20], clamp);
        return <Img key={i} src={im} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", opacity: o, transform: `scale(${s}) translateX(${x}px)` }} />;
      })}
      {caption ? (
        <div style={{ position: "absolute", left: 40, bottom: 36, opacity: cp, transform: `translateY(${(1 - cp) * 20}px)` }}>
          <Card style={{ padding: "16px 26px", borderRadius: 18, display: "flex", flexDirection: "column", gap: 4, maxWidth: 900 }}>
            {kicker ? <div style={{ fontSize: 18, fontWeight: 700, color: L.purple }}>{kicker}</div> : null}
            <div style={{ fontSize: 28, fontWeight: 650, lineHeight: 1.3, color: L.ink }}>{caption}</div>
          </Card>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

/* ---------- broll: the source screen recording, running ---------- */
const FOCI = ["20% 25%", "80% 30%", "50% 50%", "25% 75%", "75% 72%", "50% 20%"];
const BrollT: React.FC<TplProps> = ({ at = 0, caption, dur, seed }) => {
  const f = useCurrentFrame();
  // Source slides hold still for a long time: a slow push toward a different corner per shot
  // keeps each b-roll visibly new.
  const focus = FOCI[Math.round(Number(at) * 7 + seed * 3) % FOCI.length];
  const s = interpolate(f, [0, dur], [1.0, 1.16], { ...clamp, easing: ease });
  const cp = useIn(10);
  return (
    <AbsoluteFill style={{ background: "#111", overflow: "hidden" }}>
      {/* the frame is taller than 16:9: show the whole screen, fill the bands with a blurred copy */}
      <OffthreadVideo src={staticFile("screen.mp4")} startFrom={Math.round(Number(at) * 30)} muted style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", filter: "blur(28px) brightness(0.9)", transform: "scale(1.15)" }} />
      <OffthreadVideo src={staticFile("screen.mp4")} startFrom={Math.round(Number(at) * 30)} muted style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "contain", transform: `scale(${s})`, transformOrigin: focus }} />
      {caption ? (
        <div style={{ position: "absolute", left: 32, bottom: 30, opacity: cp, transform: `translateY(${(1 - cp) * 14}px)` }}>
          <Pill style={{ fontSize: 22, color: L.ink }}>
            <span style={{ width: 10, height: 10, borderRadius: 5, background: GRAD }} />
            {caption}
          </Pill>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

/* ---------- flow: nodes joined by a travelling line ---------- */
const FlowT: React.FC<TplProps> = ({ kicker, title, nodes = [], seed }) => {
  const f = useCurrentFrame();
  const n = nodes.length;
  const gap = 70;
  const w = Math.min(300, (ART_W - 140 - gap * (n - 1)) / n);
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <Title text={title} size={46} />
      <div style={{ display: "flex", alignItems: "stretch", gap, marginTop: 18, position: "relative" }}>
        {nodes.map((nd: Any, i: number) => {
          const d = 16 + i * 14;
          const p = useIn(d);
          const last = i === n - 1;
          const line = interpolate(f, [d + 6, d + 20], [0, 1], clamp);
          return (
            <div key={i} style={{ position: "relative", width: w }}>
              <Card glow={last} style={{ height: "100%", padding: "28px 22px", display: "flex", flexDirection: "column", alignItems: "center", gap: 14, textAlign: "center", opacity: p, transform: `translateY(${(1 - p) * 30}px) scale(${lerp(p, 0.92, 1)})` }}>
                <IconTile name={nd.icon} active={last} size={78} />
                <div style={{ fontSize: 28, fontWeight: 700, lineHeight: 1.25 }}>{last ? <GradText>{nd.label}</GradText> : nd.label}</div>
                {nd.sub ? <div style={{ fontSize: 23, color: L.ink2, lineHeight: 1.35 }}>{nd.sub}</div> : null}
              </Card>
              {i < n - 1 ? (
                <div style={{ position: "absolute", right: -gap + 8, top: "50%", width: gap - 16, height: 4, borderRadius: 2, background: "rgba(217,119,87,0.18)" }}>
                  <div style={{ width: `${line * 100}%`, height: "100%", borderRadius: 2, background: GRAD }} />
                  <div style={{ position: "absolute", right: -6, top: -6, width: 16, height: 16, borderRadius: 8, background: L.purple, opacity: line, boxShadow: "0 0 12px rgba(217,119,87,0.6)" }} />
                </div>
              ) : null}
            </div>
          );
        })}
      </div>
    </Stage>
  );
};

/* ---------- steps: numbered cards, cursor taps the last ---------- */
const StepsT: React.FC<TplProps> = ({ kicker, title, steps = [], seed }) => {
  const n = steps.length;
  const vertical = n > 4;
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <Title text={title} size={46} />
      <div style={{ display: "flex", flexDirection: vertical ? "column" : "row", gap: vertical ? 14 : 22, marginTop: 10, width: vertical ? 900 : undefined }}>
        {steps.map((s: Any, i: number) => {
          const p = useIn(14 + i * 12);
          const last = i === n - 1;
          return (
            <Card key={i} glow={last} style={{ width: vertical ? undefined : Math.min(330, (ART_W - 160) / n - 22), padding: vertical ? "16px 24px" : "26px 24px", display: "flex", flexDirection: vertical ? "row" : "column", alignItems: vertical ? "center" : "flex-start", gap: vertical ? 20 : 12, opacity: p, transform: `translateY(${(1 - p) * 26}px)` }}>
              <div style={{ width: 52, height: 52, borderRadius: 16, flex: "none", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 26, fontWeight: 800, color: "#fff", background: last ? GRAD : "#E9C6B3" }}>{i + 1}</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                <div style={{ fontSize: 28, fontWeight: 700, lineHeight: 1.25 }}>{s.title}</div>
                {s.sub ? <div style={{ fontSize: 24, color: L.ink2, lineHeight: 1.35 }}>{s.sub}</div> : null}
              </div>
            </Card>
          );
        })}
      </div>
    </Stage>
  );
};

/* ---------- compare: old way (muted) vs new way (gradient) ---------- */
const CompareT: React.FC<TplProps> = ({ kicker, title, left = {}, right = {}, seed }) => {
  const pl = useIn(10);
  const pr = useIn(26);
  const col = (side: Any, good: boolean, p: number) => (
    <Card glow={good} style={{ width: 515, padding: "30px 32px", display: "flex", flexDirection: "column", gap: 18, opacity: p, transform: `translateY(${(1 - p) * 30}px) scale(${good ? lerp(p, 0.94, 1.03) : 1})`, filter: good ? undefined : "saturate(0.6)" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <IconTile name={side.icon || (good ? "check" : "x")} active={good} size={60} />
        <div style={{ fontSize: 36, fontWeight: 750, lineHeight: 1.25 }}>{good ? <GradText>{side.title}</GradText> : <span style={{ color: L.ink2 }}>{side.title}</span>}</div>
      </div>
      {(side.items || []).map((t: string, i: number) => {
        const a = useIn((good ? 34 : 18) + i * 8);
        return (
          <div key={i} style={{ display: "flex", gap: 12, alignItems: "flex-start", fontSize: 28, lineHeight: 1.35, color: good ? L.ink : L.muted, opacity: a, transform: `translateX(${(1 - a) * 14}px)` }}>
            <Icon name={good ? "check" : "x"} size={26} color={good ? L.purple : "var(--faint)"} stroke={2.6} style={{ flex: "none", marginTop: 3 }} />
            <span>{t}</span>
          </div>
        );
      })}
    </Card>
  );
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <Title text={title} size={46} />
      <div style={{ display: "flex", gap: 40, alignItems: "stretch", marginTop: 8 }}>
        {col(left, false, pl)}
        {col(right, true, pr)}
      </div>
    </Stage>
  );
};

/* ---------- checklist: tilted 3D card with rows (sample 1) ---------- */
const ChecklistT: React.FC<TplProps> = ({ kicker, title, items = [], seed, side }) => {
  const f = useCurrentFrame();
  const p = useIn(0, 20);
  const tilt = lerp(p, 26, 12) + Math.sin(f / 40) * 1.5;
  return (
    <Stage seed={seed}>
      <div style={{ display: "flex", alignItems: "center", gap: 40, marginRight: 40 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 18, width: 380 }}>
          <Kicker text={kicker} />
          <Words text={title || ""} size={50} align="left" delay={6} />
          {side ? <div style={{ fontSize: 24, color: L.ink2, lineHeight: 1.4 }}>{side}</div> : null}
        </div>
        <div style={{ perspective: 1400 }}>
          <Card glow style={{ width: 580, padding: "26px 30px", transform: `rotateX(${tilt}deg) rotateY(-8deg) translateY(${(1 - p) * 80}px)`, opacity: p, display: "flex", flexDirection: "column", gap: 4 }}>
            {(items as Any[]).map((it, i) => {
              const a = useIn(16 + i * 10);
              const label = typeof it === "string" ? it : it.label;
              const val = typeof it === "string" ? "" : it.value;
              return (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 16, padding: "16px 8px", borderBottom: i < items.length - 1 ? "1px solid rgba(150,105,75,0.12)" : undefined, opacity: a, transform: `translateX(${(1 - a) * 20}px)` }}>
                  <div style={{ width: 12, height: 12, borderRadius: 6, background: GRAD, flex: "none" }} />
                  <div style={{ fontSize: 30, fontWeight: 650, lineHeight: 1.3, flex: 1 }}>{label}</div>
                  {val ? <div style={{ fontSize: 24, fontWeight: 700, color: L.purple }}>{val}</div> : null}
                </div>
              );
            })}
          </Card>
        </div>
      </div>
    </Stage>
  );
};

/* ---------- bignumber: count-up inside expanding rings ---------- */
const BigNumberT: React.FC<TplProps> = ({ kicker, prefix = "", value = 0, suffix = "", label, sub, seed, decimals = 0, sep = "." }) => {
  const f = useCurrentFrame();
  const t = interpolate(f, [8, 40], [0, 1], { ...clamp, easing: ease });
  const v = Number(value) * t;
  const s = v.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, sep);
  const p = useIn(30);
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <div style={{ position: "relative", padding: "10px 40px" }}>
        <Rings w={520} h={210} delay={4} />
        <div style={{ position: "relative", fontSize: 150, fontWeight: 800, letterSpacing: "-0.04em", lineHeight: 1.15 }}>
          <GradText>
            {prefix}
            {s}
            {suffix}
          </GradText>
        </div>
      </div>
      {label ? <div style={{ position: "relative", fontSize: 40, fontWeight: 700, opacity: p, transform: `translateY(${(1 - p) * 10}px)`, textAlign: "center" }}>{label}</div> : null}
      {sub ? <div style={{ position: "relative", fontSize: 26, color: L.ink2, opacity: p, textAlign: "center", maxWidth: 1000, lineHeight: 1.4 }}>{sub}</div> : null}
    </Stage>
  );
};

/* ---------- chat: message bubbles typing in ---------- */
const ChatT: React.FC<TplProps> = ({ kicker, title, messages = [], seed }) => {
  let delay = 10;
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <Title text={title} size={42} />
      <div style={{ display: "flex", flexDirection: "column", gap: 18, width: 940 }}>
        {(messages as Any[]).map((m, i) => {
          const d = delay;
          delay += Math.min(50, 12 + m.text.length * 0.8);
          const p = useIn(d);
          const me = m.from === "me";
          return (
            <div key={i} style={{ display: "flex", justifyContent: me ? "flex-end" : "flex-start", alignItems: "flex-end", gap: 12, opacity: p, transform: `translateY(${(1 - p) * 20}px)` }}>
              {!me ? <IconTile name={m.icon || "user"} size={52} /> : null}
              <div
                style={{
                  maxWidth: 720,
                  padding: "20px 26px",
                  borderRadius: 26,
                  borderBottomRightRadius: me ? 8 : 26,
                  borderBottomLeftRadius: me ? 26 : 8,
                  fontSize: 27,
                  lineHeight: 1.4,
                  color: me ? "#fff" : L.ink,
                  background: me ? GRAD : "var(--card)",
                  boxShadow: me ? "0 14px 34px rgba(217,119,87,0.32)" : "0 12px 30px rgba(80,50,30,0.12), 0 0 0 1px rgba(150,105,75,0.1)",
                }}
              >
                <Typed text={m.text} delay={d + 4} cps={60} caret={false} />
              </div>
              {me ? <IconTile name={m.icon || "user"} size={52} active /> : null}
            </div>
          );
        })}
      </div>
    </Stage>
  );
};

/* ---------- search: query typed into a bar, result cards drop in ---------- */
const SearchT: React.FC<TplProps> = ({ kicker, query, results = [], seed, platforms = [] }) => {
  const qlen = String(query || "").length;
  const typedEnd = 10 + (qlen / 30) * 30;
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <Card glow style={{ width: 1000, padding: "22px 28px", display: "flex", alignItems: "center", gap: 18 }}>
        <Icon name="search" size={36} color={L.purple} stroke={2.4} />
        <div style={{ fontSize: 32, fontWeight: 500, flex: 1 }}>
          <Typed text={query || ""} delay={10} cps={30} style={{ color: L.purple }} />
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          {(platforms as string[]).map((p, i) => (
            <Pill key={i} style={{ fontSize: 18, padding: "6px 14px" }}>{p}</Pill>
          ))}
        </div>
      </Card>
      <div style={{ display: "flex", flexDirection: "column", gap: 14, width: 1000 }}>
        {(results as Any[]).map((r, i) => {
          const p = useIn(typedEnd + 6 + i * 10);
          return (
            <Card key={i} style={{ padding: "18px 26px", display: "flex", alignItems: "center", gap: 18, opacity: p, transform: `translateY(${(1 - p) * 24}px)` }}>
              <IconTile name={r.icon || "chat"} size={54} active={i === 0} />
              <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                <div style={{ fontSize: 18, fontWeight: 700, color: L.purple }}>{r.src}</div>
                <div style={{ fontSize: 26, lineHeight: 1.35 }}>{r.text}</div>
              </div>
            </Card>
          );
        })}
      </div>
    </Stage>
  );
};

/* ---------- quote: one line that should land ---------- */
const QuoteT: React.FC<TplProps> = ({ kicker, text, author, seed }) => {
  const p = useIn(30 + String(text || "").length * 0.6);
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <Card glow style={{ maxWidth: 1080, padding: "44px 56px", display: "flex", flexDirection: "column", gap: 20 }}>
        <div style={{ fontSize: 110, lineHeight: 0.6, height: 50, fontWeight: 800 }}>
          <GradText>“</GradText>
        </div>
        <div style={{ fontSize: 44, fontWeight: 650, lineHeight: 1.35, letterSpacing: "-0.01em" }}>
          <Typed text={text || ""} delay={8} cps={42} />
        </div>
        {author ? <div style={{ fontSize: 24, color: L.ink2, opacity: p }}>— {author}</div> : null}
      </Card>
    </Stage>
  );
};

/* ---------- filter: N tiles, some drop out, the rest light up ---------- */
const FilterT: React.FC<TplProps> = ({ kicker, title, total = 8, keep = [], seed }) => {
  const f = useCurrentFrame();
  const keepSet: string[] = keep;
  const tiles = Array.from({ length: total }, (_, i) => (i < keepSet.length ? keepSet[i] : null));
  const order = [0, 6, 1, 2, 7, 3, 4, 5];
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <Title text={title} size={46} />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 245px)", gap: 18, marginTop: 10 }}>
        {order.slice(0, total).map((idx, k) => {
          const name = tiles[idx];
          const p = useIn(10 + k * 4);
          const out = name === null ? interpolate(f, [52, 66], [0, 1], clamp) : 0;
          const lit = name !== null ? interpolate(f, [62 + k * 3, 74 + k * 3], [0, 1], clamp) : 0;
          return (
            <div key={k} style={{ opacity: p * (1 - out * 0.85), transform: `translateY(${(1 - p) * 20 + out * 30}px) scale(${1 - out * 0.12})` }}>
              <Card glow={lit > 0.5} style={{ height: 120, display: "flex", alignItems: "center", justifyContent: "center", gap: 12, padding: "0 16px", background: name === null ? "var(--tile)" : "#fff" }}>
                <Icon name={name === null ? "x" : lit > 0.5 ? "check" : "code"} size={30} color={name === null ? "var(--faint)" : L.purple} stroke={2.4} />
                <div style={{ fontSize: 26, fontWeight: 700, color: name === null ? "var(--faint)" : L.ink }}>
                  {name === null ? "Repo" : lit > 0.5 ? <GradText>{name}</GradText> : `Repo ${idx + 1}`}
                </div>
              </Card>
            </div>
          );
        })}
      </div>
    </Stage>
  );
};

/* ---------- questions: an idea card, the AI keeps asking ---------- */
const QuestionsT: React.FC<TplProps> = ({ kicker, idea, questions = [], seed }) => {
  const p = useIn(4);
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <div style={{ display: "flex", gap: 44, alignItems: "center" }}>
        <Card glow style={{ width: 380, padding: "30px 30px", display: "flex", flexDirection: "column", gap: 14, opacity: p, transform: `scale(${lerp(p, 0.9, 1)})` }}>
          <IconTile name="sparkle" active size={64} />
          <div style={{ fontSize: 20, fontWeight: 700, color: L.purple }}>Ý tưởng</div>
          <div style={{ fontSize: 30, fontWeight: 700, lineHeight: 1.3 }}>{idea}</div>
        </Card>
        <div style={{ display: "flex", flexDirection: "column", gap: 14, width: 640 }}>
          {(questions as string[]).map((q, i) => {
            const a = useIn(18 + i * 16);
            return (
              <div key={i} style={{ display: "flex", gap: 14, alignItems: "center", opacity: a, transform: `translateX(${(1 - a) * 40}px)` }}>
                <IconTile name="bot" size={52} active={i === questions.length - 1} />
                <Card style={{ padding: "16px 22px", borderRadius: 20, fontSize: 25, lineHeight: 1.35, flex: 1 }}>{q}</Card>
              </div>
            );
          })}
        </div>
      </div>
    </Stage>
  );
};

/* ---------- equation: a × b = result ---------- */
const EquationT: React.FC<TplProps> = ({ kicker, a, op = "×", b, result, note, seed }) => {
  const pa = useIn(6);
  const pb = useIn(18);
  const pr = useIn(32, 14);
  const pn = useIn(46);
  const box = (txt: string, p: number, sub?: string) => (
    <Card style={{ padding: "24px 30px", opacity: p, transform: `translateY(${(1 - p) * 24}px)`, textAlign: "center" }}>
      <div style={{ fontSize: 46, fontWeight: 800, letterSpacing: "-0.02em", whiteSpace: "nowrap" }}>{txt}</div>
      {sub ? <div style={{ fontSize: 20, color: L.ink2, marginTop: 4 }}>{sub}</div> : null}
    </Card>
  );
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <div style={{ display: "flex", alignItems: "center", gap: 22 }}>
        {box(a, pa)}
        <div style={{ fontSize: 52, fontWeight: 700, color: L.muted, opacity: pb }}>{op}</div>
        {box(b, pb)}
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 22, marginTop: 6 }}>
        <div style={{ fontSize: 52, fontWeight: 700, color: L.muted, opacity: pr }}>=</div>
        <div style={{ position: "relative", opacity: pr, transform: `scale(${lerp(pr, 0.8, 1)})` }}>
          <Rings w={420} h={140} delay={32} />
          <div style={{ position: "relative", padding: "20px 44px", borderRadius: 999, background: GRAD, color: "#fff", fontSize: 58, fontWeight: 800, whiteSpace: "nowrap", boxShadow: "0 18px 46px rgba(217,119,87,0.4)" }}>{result}</div>
        </div>
      </div>
      {note ? <div style={{ fontSize: 26, color: L.ink2, opacity: pn, marginTop: 10, textAlign: "center", maxWidth: 1000, lineHeight: 1.4 }}>{note}</div> : null}
    </Stage>
  );
};

/* ---------- bars: gradient columns growing ---------- */
const BarsT: React.FC<TplProps> = ({ kicker, title, bars = [], seed }) => {
  const f = useCurrentFrame();
  const max = Math.max(...(bars as Any[]).map((b) => Number(b.value) || 0), 1);
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <Title text={title} size={44} />
      <div style={{ display: "flex", alignItems: "flex-end", gap: 50, height: 430, marginTop: 6 }}>
        {(bars as Any[]).map((b, i) => {
          const t = interpolate(f, [14 + i * 10, 44 + i * 10], [0, 1], { ...clamp, easing: ease });
          const h = 280 * (Number(b.value) / max) * t;
          const hi = i === bars.length - 1 || b.hi;
          return (
            <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12, width: 230 }}>
              <div style={{ fontSize: 28, fontWeight: 800, opacity: t, whiteSpace: "nowrap" }}>{hi ? <GradText>{b.display || b.value}</GradText> : <span style={{ color: L.ink2 }}>{b.display || b.value}</span>}</div>
              <div style={{ width: 150, height: Math.max(8, h), borderRadius: 22, background: hi ? GRAD : "var(--bar)", boxShadow: hi ? "0 18px 40px rgba(217,119,87,0.35)" : undefined }} />
              <div style={{ fontSize: 24, fontWeight: 600, color: L.ink2, textAlign: "center", lineHeight: 1.3 }}>{b.label}</div>
            </div>
          );
        })}
      </div>
    </Stage>
  );
};

/* ---------- formats: vertical / landscape / square frames ---------- */
const FormatsT: React.FC<TplProps> = ({ kicker, title, items = [], seed }) => {
  const f = useCurrentFrame();
  const dims: Record<string, [number, number]> = { "9:16": [180, 320], "16:9": [380, 214], "1:1": [260, 260] };
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <Title text={title} size={46} />
      <div style={{ display: "flex", alignItems: "flex-end", gap: 54, marginTop: 10 }}>
        {(items as Any[]).map((it, i) => {
          const [w, h] = dims[it.ratio] || [260, 260];
          const p = useIn(12 + i * 10);
          const active = Math.floor((f - 40) / 25) % items.length === i && f > 40;
          return (
            <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16, opacity: p, transform: `translateY(${(1 - p) * 30}px)` }}>
              <div style={{ width: w, height: h, borderRadius: 22, background: active ? GRAD : "var(--card)", boxShadow: active ? "0 18px 44px rgba(217,119,87,0.38)" : "0 12px 30px rgba(80,50,30,0.12), 0 0 0 2px rgba(217,119,87,0.25)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Icon name="play" size={64} color={active ? "#fff" : L.purple} />
              </div>
              <div style={{ fontSize: 28, fontWeight: 700 }}>{it.label}</div>
              <div style={{ fontSize: 22, color: L.muted, marginTop: -10 }}>{it.ratio}</div>
            </div>
          );
        })}
      </div>
    </Stage>
  );
};

/* ---------- commands: slash commands in an editor card ---------- */
const CommandsT: React.FC<TplProps> = ({ kicker, title, commands = [], seed }) => {
  const f = useCurrentFrame();
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <Title text={title} size={44} />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 510px)", gap: 22, marginTop: 6 }}>
        {(commands as Any[]).map((c, i) => {
          const p = useIn(12 + i * 12);
          const glow = Math.floor((f - 20) / 30) % commands.length === i && f > 20;
          return (
            <Card key={i} glow={glow} style={{ padding: "22px 26px", display: "flex", flexDirection: "column", gap: 10, opacity: p, transform: `translateY(${(1 - p) * 24}px)` }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <IconTile name={c.icon || "wand"} size={50} active={glow} />
                <div style={{ fontSize: 32, fontWeight: 750, fontFamily: "Consolas, 'Cascadia Mono', monospace" }}>
                  <GradText>{c.cmd}</GradText>
                </div>
              </div>
              <div style={{ fontSize: 23, color: L.ink2, lineHeight: 1.38 }}>{c.desc}</div>
            </Card>
          );
        })}
      </div>
    </Stage>
  );
};

/* ---------- form: a free tool that shows the result before asking for email ---------- */
const FormT: React.FC<TplProps> = ({ kicker, title, rows = [], result, cta, seed }) => {
  const f = useCurrentFrame();
  const p = useIn(4);
  const pr = useIn(40);
  const pc = useIn(70);
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <div style={{ display: "flex", gap: 40, alignItems: "center" }}>
        <Card glow style={{ width: 540, padding: "28px 30px", display: "flex", flexDirection: "column", gap: 14, opacity: p, transform: `translateY(${(1 - p) * 30}px)` }}>
          <div style={{ fontSize: 30, fontWeight: 750 }}>{title}</div>
          {(rows as Any[]).map((r, i) => {
            const a = useIn(12 + i * 8);
            const sel = interpolate(f, [30 + i * 6, 38 + i * 6], [0, 1], clamp);
            return (
              <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "14px 18px", borderRadius: 14, fontSize: 24, opacity: a, background: i === 1 ? `rgba(217,119,87,${0.1 * sel})` : "var(--tile)", boxShadow: i === 1 && sel > 0.5 ? "inset 0 0 0 2px rgba(217,119,87,0.5)" : undefined }}>
                <span>{r.label}</span>
                <span style={{ fontWeight: 700, color: L.purple }}>{r.value}</span>
              </div>
            );
          })}
        </Card>
        <div style={{ display: "flex", flexDirection: "column", gap: 20, width: 460 }}>
          <Card style={{ padding: "24px 28px", opacity: pr, transform: `translateX(${(1 - pr) * 30}px)` }}>
            <div style={{ fontSize: 20, fontWeight: 700, color: L.purple }}>Kết quả xem ngay</div>
            <div style={{ fontSize: 34, fontWeight: 800, marginTop: 6 }}>
              <GradText>{result}</GradText>
            </div>
          </Card>
          <div style={{ opacity: pc, transform: `translateY(${(1 - pc) * 20}px)`, position: "relative" }}>
            <div style={{ padding: "22px 30px", borderRadius: 999, background: GRAD, color: "#fff", fontSize: 28, fontWeight: 700, textAlign: "center", boxShadow: "0 16px 40px rgba(217,119,87,0.4)" }}>{cta}</div>
          </div>
        </div>
      </div>
      <Cursor fromX={1100} fromY={660} x={880} y={470} at={92} />
    </Stage>
  );
};

/* ---------- recap: grid of all tools, highlighting one by one ---------- */
const RecapT: React.FC<TplProps> = ({ kicker, title, items = [], seed, dur }) => {
  const f = useCurrentFrame();
  const n = items.length;
  const per = Math.max(20, (dur - 20) / Math.max(1, n));
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <Title text={title} size={44} />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 350px)", gap: 18 }}>
        {(items as Any[]).map((it, i) => {
          const p = useIn(8 + i * 5);
          const on = f >= 20 + i * per;
          return (
            <Card key={i} glow={on} style={{ padding: "20px 22px", display: "flex", gap: 16, alignItems: "center", opacity: p * (on ? 1 : 0.55), transform: `scale(${on ? 1 : 0.97})` }}>
              <IconTile name={it.icon} size={60} active={on} />
              <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                <div style={{ fontSize: 28, fontWeight: 750 }}>{on ? <GradText>{it.name}</GradText> : it.name}</div>
                <div style={{ fontSize: 19, color: L.ink2, lineHeight: 1.3 }}>{it.desc}</div>
              </div>
            </Card>
          );
        })}
      </div>
    </Stage>
  );
};

export const TEMPLATES: Record<string, React.FC<TplProps>> = {
  title: TitleT,
  tool: ToolT,
  person: PersonT,
  photo: PhotoT,
  broll: BrollT,
  flow: FlowT,
  steps: StepsT,
  compare: CompareT,
  checklist: ChecklistT,
  bignumber: BigNumberT,
  chat: ChatT,
  search: SearchT,
  quote: QuoteT,
  filter: FilterT,
  questions: QuestionsT,
  equation: EquationT,
  bars: BarsT,
  formats: FormatsT,
  commands: CommandsT,
  form: FormT,
  recap: RecapT,
  ...REEL,
  ...MEDIA,
};

export { ART_W, ART_H, FONT, BlobBg };
