import React from "react";
import { Img, interpolate, useCurrentFrame } from "remotion";
import { Card, FONT, GRAD, GradText, Kicker, L, Pill, Stage, Typed, Words, cueAt, ease, lerp, useDark, useIn } from "./kit";
import { Icon, IconTile } from "./icons";
import type { TplProps } from "./templates";

/**
 * Learned set: motion graphics taken from a long-form "edited by Claude + Remotion" YouTube video
 * (see references/tu-duy-dung-motion.md). All full-frame scenes (MOTION: / FULL:), clay palette.
 *   pricecut   old price struck out, new price counts down to its value
 *   receipt    line items, the total counts up and fills
 *   calendar   month grid, one day circled, the days after it dim out
 *   countdown  days / hours / minutes / seconds ticking
 *   lock       product card, a padlock drops onto it and the card dims
 *   tracker    row of step cards: done ones ticked, current one lit, optional time under each
 *   hub        inputs flow into a centre, outputs flow out of it
 *   folder     a folder opens into sub-folders, then a big count of what is inside
 *   transcript words appear one by one, pauses shown as struck-out chips
 *   scriptclip script lines on the left (one highlighted), the matching picture on the right
 *   reveal     two cards, the second hidden behind "?" until it flips
 *   linechart  a line drawing itself, one point called out
 *   beforeafter small greyed "before" beside a big "after"
 *   promptui   an app window; each prompt line types in and a card pops up beside it
 *   progress   a bar fills to 100 % and turns into a done tick
 *   doctilt    a document screenshot on a tilted plane with a name pill
 *   comments   a wall of message cards drifting, a big claim on top
 */

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
type Any = Record<string, any>;

const fmt = (v: number, decimals = 0, sep = ".") => v.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, sep);

/** Number that counts from `from` to `to` between frames a and b. */
const useCount = (from: number, to: number, a: number, b: number) => {
  const f = useCurrentFrame();
  return lerp(interpolate(f, [a, b], [0, 1], { ...clamp, easing: ease }), from, to);
};

const Head: React.FC<{ kicker?: string; title?: string; size?: number }> = ({ kicker, title, size = 46 }) => (
  <>
    <Kicker text={kicker} />
    {title ? <Words text={title} delay={4} size={size} /> : null}
  </>
);

/* ---------- pricecut ---------- */
const PriceCutT: React.FC<TplProps> = ({ kicker, title, old, oldNote, from, value = 0, prefix = "", suffix = "", note, decimals = 0, sep = ".", seed }) => {
  const f = useCurrentFrame();
  const a = useIn(6);
  const strike = interpolate(f, [26, 36], [0, 1], { ...clamp, easing: ease });
  const dim = interpolate(f, [36, 46], [1, 0.4], clamp);
  const b = useIn(40);
  const n = useCount(Number(from ?? value), Number(value), 42, 72);
  return (
    <Stage seed={seed}>
      <Head kicker={kicker} title={title} size={40} />
      <Card style={{ padding: "34px 70px", display: "flex", flexDirection: "column", alignItems: "center", gap: 6, minWidth: 520 }}>
        <div style={{ position: "relative", opacity: a * dim, transform: `translateY(${(1 - a) * 14}px)`, fontSize: 54, fontWeight: 700, color: L.ink2 }}>
          {old}
          {oldNote ? <span style={{ fontSize: 24, fontWeight: 500, marginLeft: 10 }}>{oldNote}</span> : null}
          <div style={{ position: "absolute", left: -8, top: "52%", height: 5, borderRadius: 3, background: L.ink2, width: `calc(${strike * 100}% + 16px)` }} />
        </div>
        <div style={{ opacity: b, transform: `scale(${lerp(b, 0.8, 1)})`, fontSize: 132, fontWeight: 850, letterSpacing: "-0.04em", lineHeight: 1.12 }}>
          <GradText>{prefix}{fmt(n, decimals, sep)}{suffix}</GradText>
        </div>
        {note ? <div style={{ opacity: b, fontSize: 26, color: L.ink2 }}>{note}</div> : null}
      </Card>
    </Stage>
  );
};

/* ---------- receipt ---------- */
const ReceiptT: React.FC<TplProps> = ({ kicker, title = "Chi phí", tag, items = [], total = {}, seed }) => {
  const list = items as Any[];
  const tStart = 10 + list.length * 6 + 6;
  const n = useCount(0, Number(total.value || 0), tStart, tStart + 30);
  const fill = useIn(tStart + 30);
  const c = useIn(2);
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <Card style={{ width: 640, padding: "30px 38px", opacity: c, transform: `translateY(${(1 - c) * 24}px)` }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 16 }}>
          <div style={{ fontSize: 32, fontWeight: 750 }}>{title}</div>
          <div style={{ fontSize: 17, letterSpacing: "0.12em", color: L.muted, textTransform: "uppercase" }}>{tag || "Hoá đơn"}</div>
        </div>
        {list.map((it, i) => {
          const p = useIn(cueAt(i, 10 + i * 6));
          return (
            <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "9px 0", borderBottom: `1px dashed ${L.line}`, opacity: p, transform: `translateX(${(1 - p) * -16}px)` }}>
              <span style={{ fontSize: 23, color: L.ink2 }}>{it.label}</span>
              <span style={{ fontSize: 20, fontWeight: 700, color: "var(--ink)", background: "var(--pill)", boxShadow: "var(--pillshadow)", borderRadius: 999, padding: "5px 16px" }}>{it.value}</span>
            </div>
          );
        })}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 16, padding: "14px 18px", borderRadius: 16,
          background: `rgba(217,119,87,${0.16 * fill})`, boxShadow: `inset 0 0 0 ${2 * fill}px rgba(217,119,87,0.5)` }}>
          <span style={{ fontSize: 28, fontWeight: 750 }}>{total.label || "Tổng"}</span>
          <span style={{ fontSize: 40, fontWeight: 850 }}>
            <GradText>{total.prefix || ""}{fmt(n, total.decimals || 0)}{total.suffix || ""}</GradText>
          </span>
        </div>
      </Card>
    </Stage>
  );
};

/* ---------- calendar ---------- */
const CalendarT: React.FC<TplProps> = ({ kicker, title, month = "Tháng 11", year = "2026", days = 30, start = 0, mark = 15, tag, dimAfter = true, seed }) => {
  const f = useCurrentFrame();
  const c = useIn(2);
  const ring = interpolate(f, [24, 38], [0, 1], { ...clamp, easing: ease });
  const dim = dimAfter ? interpolate(f, [40, 56], [0, 1], clamp) : 0;
  const t = useIn(44);
  const heads = ["CN", "T2", "T3", "T4", "T5", "T6", "T7"];
  const cells: (number | null)[] = [...Array(Number(start)).fill(null), ...Array.from({ length: Number(days) }, (_, i) => i + 1)];
  return (
    <Stage seed={seed}>
      <Head kicker={kicker} title={title} size={40} />
      <Card style={{ width: 600, padding: "26px 30px", opacity: c, transform: `translateY(${(1 - c) * 24}px) scale(${lerp(c, 0.96, 1)})` }}>
        <div style={{ fontSize: 30, fontWeight: 750, marginBottom: 14 }}>{month} <span style={{ color: L.muted, fontWeight: 500 }}>{year}</span></div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", rowGap: 10, textAlign: "center" }}>
          {heads.map((h) => <div key={h} style={{ fontSize: 15, color: L.muted, fontWeight: 600 }}>{h}</div>)}
          {cells.map((d, i) => {
            const on = d === Number(mark);
            const after = d !== null && d > Number(mark);
            return (
              <div key={i} style={{ position: "relative", height: 46, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 21, fontWeight: on ? 800 : 500,
                opacity: after ? 1 - 0.7 * dim : 1, color: on ? "#C15F3C" : L.ink }}>
                {d ?? ""}
                {on ? <div style={{ position: "absolute", width: 48, height: 48, borderRadius: 24, border: "3px solid #D97757", transform: `scale(${lerp(ring, 1.6, 1)})`, opacity: ring }} /> : null}
              </div>
            );
          })}
        </div>
      </Card>
      {tag ? <div style={{ opacity: t, transform: `translateY(${(1 - t) * 10}px)`, fontSize: 24, fontWeight: 700, color: "#E8916F" }}>{mark}/{String(month).replace(/\D/g, "") || ""} · {tag}</div> : null}
    </Stage>
  );
};

/* ---------- countdown ---------- */
const CountdownT: React.FC<TplProps> = ({ kicker, title, days = 20, hours = 11, mins = 42, secs = 35, labels = ["ngày", "giờ", "phút", "giây"], seed }) => {
  const f = useCurrentFrame();
  const left = Math.max(0, Number(days) * 86400 + Number(hours) * 3600 + Number(mins) * 60 + Number(secs) - Math.floor(f / 30));
  const parts = [Math.floor(left / 86400), Math.floor(left / 3600) % 24, Math.floor(left / 60) % 60, left % 60];
  const c = useIn(4);
  return (
    <Stage seed={seed}>
      <Head kicker={kicker} title={title} size={44} />
      <div style={{ display: "flex", gap: 22, opacity: c, transform: `translateY(${(1 - c) * 20}px)` }}>
        {parts.map((v, i) => (
          <Card key={i} glow={i === 0} style={{ width: 170, padding: "22px 0 16px", display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div style={{ fontSize: 88, fontWeight: 850, letterSpacing: "-0.03em", lineHeight: 1.1, fontVariantNumeric: "tabular-nums" }}>
              {i === 0 ? <GradText>{String(v).padStart(2, "0")}</GradText> : String(v).padStart(2, "0")}
            </div>
            <div style={{ fontSize: 20, color: L.muted, fontWeight: 600 }}>{labels[i]}</div>
          </Card>
        ))}
      </div>
    </Stage>
  );
};

/* ---------- lock ---------- */
const LockT: React.FC<TplProps> = ({ kicker, name, sub, src, icon = "rocket", label, seed }) => {
  const f = useCurrentFrame();
  const c = useIn(2);
  const drop = interpolate(f, [16, 30], [0, 1], { ...clamp, easing: (t: number) => 1 - Math.pow(1 - t, 3) });
  const settle = interpolate(f, [30, 36, 42], [0, 1, 0], clamp);
  const dim = interpolate(f, [40, 54], [0, 1], clamp);
  const l = useIn(48);
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <div style={{ position: "relative", opacity: c, transform: `scale(${lerp(c, 0.92, 1)})` }}>
        <Card glow style={{ width: 560, height: 300, paddingBottom: 46, boxSizing: "border-box", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 14,
          background: "linear-gradient(160deg, #2A2927 0%, #1F1E1D 60%, #3A2A22 100%)", filter: `saturate(${1 - dim * 0.8}) brightness(${1 - dim * 0.35})` }}>
          {src ? <Img src={src} style={{ height: 110, objectFit: "contain" }} /> : <Icon name={icon} size={96} color="#F0B49A" />}
          <div style={{ fontSize: 46, fontWeight: 850, color: "#FAF9F5" }}>{name}</div>
          {sub ? <div style={{ fontSize: 20, color: "#C9C5BC" }}>{sub}</div> : null}
        </Card>
        <div style={{ position: "absolute", left: "50%", top: lerp(drop, -260, 254) + settle * -10, marginLeft: -46, width: 92, height: 92, borderRadius: 26, background: "#FAF9F5",
          display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 16px 40px rgba(0,0,0,0.35)", opacity: drop > 0 ? 1 : 0 }}>
          <Icon name="lock" size={54} color="#141413" stroke={2.2} />
        </div>
      </div>
      {label ? <div style={{ marginTop: 40, opacity: l, fontSize: 26, fontWeight: 700, color: "#E8916F" }}>{label}</div> : null}
    </Stage>
  );
};

/* ---------- tracker ---------- */
const TrackerT: React.FC<TplProps> = ({ kicker, title, steps = [], current = 0, seed }) => {
  const f = useCurrentFrame();
  const list = steps as Any[];
  const cur = Number(current);
  const showTimes = list.some((s) => s.time);
  const w = Math.min(150, Math.floor((1100 - (list.length - 1) * 14) / Math.max(1, list.length)));
  return (
    <Stage seed={seed}>
      <Head kicker={kicker} title={title} size={42} />
      <div style={{ display: "flex", gap: 14 }}>
        {list.map((s, i) => {
          const p = useIn(cueAt(i, 4 + i * 3));
          const done = i < cur;
          const on = i === cur;
          const tick = interpolate(f, [16 + i * 4, 24 + i * 4], [0, 1], clamp);
          const lift = on ? useIn(18) : 0;
          return (
            <div key={i} style={{ display: "flex", flexDirection: "column", gap: 12, opacity: p, transform: `translateY(${(1 - p) * 24 - lift * 14}px) scale(${1 + lift * 0.06})` }}>
              <Card glow={on} style={{ width: w, height: w * 1.45, padding: 14, display: "flex", flexDirection: "column", justifyContent: "space-between", opacity: done || on ? 1 : 0.55 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div style={{ fontSize: 26, fontWeight: 800, color: on ? "#C15F3C" : L.muted }}>{String(i + 1).padStart(2, "0")}</div>
                  {done ? <div style={{ width: 30, height: 30, borderRadius: 15, background: GRAD, display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${tick})` }}>
                    <Icon name="check" size={20} color="#fff" stroke={3} /></div> : null}
                </div>
                {s.icon ? <div style={{ alignSelf: "center" }}><IconTile name={s.icon} size={w * 0.42} active={on} /></div> : null}
                <div style={{ fontSize: 18, fontWeight: 700, lineHeight: 1.25 }}>{s.label}</div>
              </Card>
              {showTimes ? (
                <div style={{ height: 52, borderRadius: 14, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22, fontWeight: 800,
                  background: "var(--pill)", boxShadow: "0 0 0 1px rgba(150,105,75,0.14)", opacity: done || on ? interpolate(f, [24 + i * 4, 32 + i * 4], [0, 1], clamp) : 0.35 }}>
                  {done || on ? s.time : ""}
                </div>
              ) : null}
            </div>
          );
        })}
      </div>
    </Stage>
  );
};

/* ---------- hub: inputs → centre → outputs ---------- */
const HubT: React.FC<TplProps> = ({ kicker, title, inputs = [], center = {}, outputs = [], seed }) => {
  const f = useCurrentFrame();
  const ins = inputs as Any[];
  const outs = outputs as Any[];
  const c = useIn(14, 14);
  const W = 1100, H = 400, cx = W / 2, cy = H / 2;
  const ys = (n: number) => Array.from({ length: n }, (_, i) => (n === 1 ? cy : 40 + (i * (H - 80)) / (n - 1)));
  const iy = ys(ins.length), oy = ys(outs.length);
  const flowIn = interpolate(f, [8, 30], [0, 1], { ...clamp, easing: ease });
  const flowOut = interpolate(f, [34, 56], [0, 1], { ...clamp, easing: ease });
  const dash = -f * 1.6;
  const path = (x1: number, y1: number, x2: number, y2: number) => `M${x1},${y1} C${(x1 + x2) / 2},${y1} ${(x1 + x2) / 2},${y2} ${x2},${y2}`;
  const Node: React.FC<{ it: Any; x: number; y: number; d: number; right?: boolean }> = ({ it, x, y, d, right }) => {
    const p = useIn(d);
    return (
      <div style={{ position: "absolute", left: x, top: y, transform: `translate(${right ? 0 : -100}%, -50%) translateX(${(1 - p) * (right ? 20 : -20)}px)`, opacity: p }}>
        <Card style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 20px" }}>
          <IconTile name={it.icon} size={46} />
          <div style={{ fontSize: 21, fontWeight: 700, whiteSpace: "nowrap" }}>{it.label}</div>
        </Card>
      </div>
    );
  };
  return (
    <Stage seed={seed}>
      <Head kicker={kicker} title={title} size={42} />
      <div style={{ position: "relative", width: W, height: H }}>
        <svg width={W} height={H} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
          {iy.map((y, i) => <path key={"i" + i} d={path(300, y, cx - 80, cy)} fill="none" stroke="#D97757" strokeWidth={2.5} strokeDasharray="6 8" strokeDashoffset={dash} opacity={flowIn} />)}
          {oy.map((y, i) => <path key={"o" + i} d={path(cx + 80, cy, W - 300, y)} fill="none" stroke="#D97757" strokeWidth={2.5} strokeDasharray="6 8" strokeDashoffset={dash} opacity={flowOut} />)}
        </svg>
        {ins.map((it, i) => <Node key={i} it={it} x={300} y={iy[i]} d={cueAt(i, 2 + i * 4)} />)}
        {outs.map((it, i) => <Node key={i} it={it} x={W - 300} y={oy[i]} d={cueAt(ins.length + i, 34 + i * 5)} right />)}
        <div style={{ position: "absolute", left: cx, top: cy, transform: `translate(-50%,-50%) scale(${c})`, display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
          <div style={{ width: 150, height: 150, borderRadius: 44, background: "linear-gradient(180deg, #E3876A 0%, #D97757 50%, #C8643F 100%)", display: "flex", alignItems: "center", justifyContent: "center",
            boxShadow: `inset 0 1px 0 rgba(255,255,255,0.2), 0 0 ${40 + Math.sin(f / 8) * 12}px rgba(217,119,87,0.45), 0 16px 34px rgba(0,0,0,0.35)` }}>
            {center.src ? <Img src={center.src} style={{ width: 96, height: 96, objectFit: "contain" }} /> : <Icon name={center.icon || "brain"} size={86} color="#fff" stroke={1.7} />}
          </div>
          {center.label ? <div style={{ fontSize: 24, fontWeight: 800 }}>{center.label}</div> : null}
        </div>
      </div>
    </Stage>
  );
};

/* ---------- folder ---------- */
const FolderT: React.FC<TplProps> = ({ kicker, name = "Thư mục", items = [], count, unit = "mục", seed }) => {
  const f = useCurrentFrame();
  const a = useIn(2);
  const open = interpolate(f, [18, 32], [0, 1], { ...clamp, easing: ease });
  const list = (items as string[]).slice(0, 6);
  const g = interpolate(f, [56, 70], [0, 1], { ...clamp, easing: ease });
  const n = useCount(0, Number(count || 0), 58, 88);
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <div style={{ position: "relative", width: 900, height: 440 }}>
        <div style={{ position: "absolute", left: "50%", top: "50%", transform: `translate(-50%,-50%) scale(${lerp(a, 0.6, 1) * (1 - open * 0.6)})`, opacity: a * (1 - open),
          display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
          <Icon name="folder" size={210} color="#D97757" stroke={1.4} />
          <div style={{ fontSize: 30, fontWeight: 750 }}>{name}</div>
        </div>
        <Card style={{ position: "absolute", inset: 0, padding: 26, opacity: open * (1 - g * 0.85), transform: `scale(${lerp(open, 0.85, 1)})` }}>
          <div style={{ display: "flex", gap: 8, marginBottom: 18 }}>
            {["#E8916F", "#F4DDCB", "#DCC3AF"].map((c) => <div key={c} style={{ width: 13, height: 13, borderRadius: 7, background: c }} />)}
            <div style={{ marginLeft: 14, fontSize: 18, fontWeight: 700, color: L.ink2 }}>{name}</div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 22 }}>
            {list.map((t, i) => {
              const c0 = cueAt(i, 30 + i * 4);
              const p = interpolate(f, [c0, c0 + 10], [0, 1], { ...clamp, easing: ease });
              return (
                <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6, opacity: p, transform: `translateY(${(1 - p) * 12}px)` }}>
                  <Icon name="folder" size={86} color="#D97757" stroke={1.5} />
                  <div style={{ fontSize: 19, fontWeight: 600, textAlign: "center" }}>{t}</div>
                </div>
              );
            })}
          </div>
        </Card>
        {count ? (
          <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", opacity: g, transform: `scale(${lerp(g, 0.85, 1)})` }}>
            <div style={{ fontSize: 150, fontWeight: 850, letterSpacing: "-0.04em", lineHeight: 1.1 }}><GradText>{fmt(n)}</GradText></div>
            <div style={{ fontSize: 34, fontWeight: 700 }}>{unit}</div>
          </div>
        ) : null}
      </div>
    </Stage>
  );
};

/* ---------- transcript: words + struck pauses ---------- */
const TranscriptT: React.FC<TplProps> = ({ kicker, title, text = "", seed }) => {
  const f = useCurrentFrame();
  // "{1.4s}" marks a pause the cut removes
  const toks = String(text).split(/\s+/).filter(Boolean);
  return (
    <Stage seed={seed}>
      <Head kicker={kicker} title={title} size={40} />
      <Card style={{ width: 1000, padding: "30px 36px" }}>
        <div style={{ fontSize: 15, letterSpacing: "0.14em", color: L.muted, fontWeight: 700, marginBottom: 14 }}>TRANSCRIPT · TỪNG CHỮ</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "10px 10px", alignItems: "center" }}>
          {toks.map((t, i) => {
            const p = interpolate(f, [6 + i * 2.2, 12 + i * 2.2], [0, 1], { ...clamp, easing: ease });
            const m = t.match(/^\{(.+)\}$/);
            if (m) {
              const cut = interpolate(f, [16 + i * 2.2, 24 + i * 2.2], [0, 1], clamp);
              return (
                <span key={i} style={{ opacity: p * (1 - cut * 0.45), fontSize: 18, fontWeight: 700, color: "#B5532F", padding: "4px 12px", borderRadius: 999,
                  background: "rgba(217,119,87,0.14)", textDecoration: cut > 0.5 ? "line-through" : "none" }}>Nghỉ {m[1]}</span>
              );
            }
            return <span key={i} style={{ opacity: p, filter: `blur(${(1 - p) * 6}px)`, fontSize: 30, fontWeight: 600 }}>{t}</span>;
          })}
        </div>
      </Card>
    </Stage>
  );
};

/* ---------- scriptclip ---------- */
const ScriptClipT: React.FC<TplProps> = ({ kicker, lines = [], active = 0, src, label, seed }) => {
  const f = useCurrentFrame();
  const list = lines as string[];
  const hi = interpolate(f, [16, 28], [0, 1], { ...clamp, easing: ease });
  const m = useIn(20);
  return (
    <Stage seed={seed}>
      <Kicker text={kicker} />
      <div style={{ display: "flex", gap: 36, alignItems: "center" }}>
        <Card style={{ width: 520, padding: "26px 28px", display: "flex", flexDirection: "column", gap: 16 }}>
          {list.map((t, i) => {
            const p = useIn(2 + i * 4);
            const on = i === Number(active);
            return (
              <div key={i} style={{ fontSize: 21, lineHeight: 1.4, color: on ? L.ink : L.muted, opacity: p * (on ? 1 : 0.7), padding: "10px 14px", borderRadius: 12,
                boxShadow: on ? `inset 0 0 0 ${2 * hi}px #D97757` : "none", background: on ? `rgba(217,119,87,${0.08 * hi})` : "transparent", fontWeight: on ? 650 : 450 }}>{t}</div>
            );
          })}
        </Card>
        <div style={{ display: "flex", flexDirection: "column", gap: 10, opacity: m, transform: `translateX(${(1 - m) * 30}px)` }}>
          {label ? <div style={{ fontSize: 17, color: L.muted, fontWeight: 600 }}>{label}</div> : null}
          <div style={{ width: 460, height: 260, borderRadius: 18, overflow: "hidden", boxShadow: "0 0 0 3px var(--ring), var(--deepshadow)", background: "#1F1E1D" }}>
            {src ? <Img src={src} style={{ width: "100%", height: "100%", objectFit: "cover" }} /> : null}
          </div>
        </div>
      </div>
    </Stage>
  );
};

/* ---------- reveal: second card hidden behind "?" ---------- */
const RevealT: React.FC<TplProps> = ({ kicker, title, items = [], at = 0.5, dur, seed }) => {
  const f = useCurrentFrame();
  const list = (items as Any[]).slice(0, 2);
  const flipAt = Math.round((dur || 120) * Number(at));
  const flip = interpolate(f, [flipAt, flipAt + 14], [0, 1], { ...clamp, easing: ease });
  return (
    <Stage seed={seed}>
      <Head kicker={kicker} title={title} size={44} />
      <div style={{ display: "flex", gap: 40 }}>
        {list.map((it, i) => {
          const p = useIn(6 + i * 6);
          const hidden = i === 1 && flip < 0.5;
          const rot = i === 1 ? (flip < 0.5 ? flip * 180 : (1 - flip) * -180) : 0;
          const on = i === 0 ? 1 - flip * 0.45 : flip;
          return (
            <Card key={i} glow={i === 1 && flip > 0.5} style={{ position: "relative", width: 380, height: 300, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 14,
              opacity: p * lerp(on, 0.55, 1), transform: `translateY(${(1 - p) * 24}px) perspective(900px) rotateY(${rot}deg)` }}>
              <div style={{ position: "absolute", left: 18, top: 16, width: 34, height: 34, borderRadius: 17, background: GRAD, color: "#fff", fontWeight: 800, fontSize: 18, display: "flex", alignItems: "center", justifyContent: "center" }}>{i + 1}</div>
              {hidden ? <div style={{ fontSize: 120, fontWeight: 800, color: L.muted }}>?</div> : (
                <>
                  <IconTile name={it.icon} size={96} active={i === 1} />
                  <div style={{ fontSize: 32, fontWeight: 800, textAlign: "center" }}>{it.title}</div>
                  {it.sub ? <div style={{ fontSize: 19, color: L.ink2, textAlign: "center", padding: "0 24px", lineHeight: 1.35 }}>{it.sub}</div> : null}
                </>
              )}
            </Card>
          );
        })}
      </div>
    </Stage>
  );
};

/* ---------- linechart ---------- */
const LineChartT: React.FC<TplProps> = ({ kicker, title, points = [], base = [], labels = [], highlight, note, seed }) => {
  const f = useCurrentFrame();
  const pts = (points as number[]).map(Number);
  const rl = (base as number[]).map(Number);
  const all = [...pts, ...rl];
  const lo = Math.min(...all, 0), hi = Math.max(...all, 1);
  const W = 860, H = 320;
  const xy = (arr: number[]) => arr.map((v, i) => [(i * W) / Math.max(1, arr.length - 1), H - ((v - lo) / (hi - lo)) * H]);
  const d = (arr: number[]) => xy(arr).map(([x, y], i) => `${i ? "L" : "M"}${x},${y}`).join(" ");
  const draw = interpolate(f, [8, 44], [0, 1], { ...clamp, easing: ease });
  const hiI = highlight === undefined ? pts.length - 1 : Number(highlight);
  const [hx, hy] = xy(pts)[hiI] || [0, 0];
  const dot = useIn(44);
  return (
    <Stage seed={seed}>
      <Head kicker={kicker} title={title} size={42} />
      <Card style={{ padding: "30px 40px 22px" }}>
        <svg width={W} height={H} style={{ overflow: "visible" }}>
          {[0.25, 0.5, 0.75].map((k) => <line key={k} x1={0} x2={W} y1={H * k} y2={H * k} stroke="rgba(150,105,75,0.15)" />)}
          {rl.length ? <path d={d(rl)} fill="none" stroke="#B9B4C6" strokeWidth={3} strokeDasharray="10 10" opacity={draw} /> : null}
          <path d={d(pts)} fill="none" stroke="#D97757" strokeWidth={5} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - draw} />
          <circle cx={hx} cy={hy} r={12 * dot} fill="#D97757" />
          <circle cx={hx} cy={hy} r={12 + 22 * dot} fill="none" stroke="#D97757" strokeWidth={2} opacity={1 - dot * 0.6} />
        </svg>
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 10, fontSize: 17, color: L.muted }}>
          {(labels as string[]).map((t, i) => <span key={i}>{t}</span>)}
        </div>
      </Card>
      {note ? <div style={{ opacity: dot, fontSize: 26, color: L.ink2 }}>{note}</div> : null}
    </Stage>
  );
};

/* ---------- beforeafter ---------- */
const BeforeAfterT: React.FC<TplProps> = ({ kicker, title, before = {}, after = {}, seed }) => {
  const b = useIn(4);
  const a = useIn(18);
  const box = (it: Any, big: boolean, p: number, grey: boolean) => (
    <div style={{ display: "flex", flexDirection: "column", gap: 10, opacity: p, transform: `translateY(${(1 - p) * 26}px)` }}>
      <div style={{ fontSize: big ? 34 : 26, fontWeight: 800 }}>{big ? <GradText>{it.label || "Sau"}</GradText> : it.label || "Trước"}</div>
      <div style={{ width: big ? 600 : 340, height: big ? 360 : 230, borderRadius: 20, overflow: "hidden", background: "#2A2927",
        boxShadow: big ? "0 0 0 4px var(--ring), 0 0 40px rgba(217,119,87,0.3), var(--deepshadow)" : "0 0 0 3px var(--ring), var(--deepshadow)" }}>
        {it.src ? <Img src={it.src} style={{ width: "100%", height: "100%", objectFit: "cover", filter: grey ? "grayscale(1) brightness(0.85)" : "none" }} /> : null}
      </div>
      {it.sub ? <div style={{ fontSize: 19, color: L.ink2 }}>{it.sub}</div> : null}
    </div>
  );
  return (
    <Stage seed={seed}>
      <Head kicker={kicker} title={title} size={40} />
      <div style={{ display: "flex", gap: 36, alignItems: "flex-end" }}>
        {box(before, false, b, true)}
        {box(after, true, a, false)}
      </div>
    </Stage>
  );
};

/* ---------- promptui: prompt lines type in, a card pops beside each ---------- */
const PromptUiT: React.FC<TplProps> = ({ app = "Claude Code", greet = "Chào bạn", lines = [], per = 40, seed }) => {
  const f = useCurrentFrame();
  const list = lines as Any[];
  const step = Number(per);
  const cur = Math.min(list.length - 1, Math.max(0, Math.floor((f - 10) / step)));
  const w = useIn(2);
  const card = list[cur]?.card;
  const cp = interpolate((f - 10) % step, [8, 20], [0, 1], { ...clamp, easing: ease });
  return (
    <Stage seed={seed}>
      <div style={{ display: "flex", gap: 34, alignItems: "center" }}>
        <div style={{ width: 640, borderRadius: 20, background: "#262624", boxShadow: "0 30px 70px rgba(0,0,0,0.35)", padding: "16px 24px 26px", opacity: w, transform: `translateY(${(1 - w) * 20}px)`, color: "#FAF9F5" }}>
          <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 22 }}>
            {["#5A5550", "#5A5550", "#5A5550"].map((c, i) => <div key={i} style={{ width: 11, height: 11, borderRadius: 6, background: c }} />)}
            <div style={{ flex: 1, textAlign: "center", fontSize: 14, color: "#9A968E" }}>{app}</div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12, justifyContent: "center", fontSize: 30, fontFamily: "Georgia, serif", marginBottom: 20 }}>
            <Icon name="sparkle" size={30} color="#D97757" />{greet}
          </div>
          <div style={{ background: "#30302E", borderRadius: 16, padding: "16px 18px", display: "flex", flexDirection: "column", gap: 10, boxShadow: "inset 0 0 0 1px rgba(255,255,255,0.08)" }}>
            {list.map((it, i) => {
              const start = 10 + i * step;
              if (f < start) return null;
              const on = i === cur;
              return (
                <div key={i} style={{ display: "flex", gap: 10, alignItems: "flex-start", fontSize: 19, lineHeight: 1.4, color: on ? "#FAF9F5" : "#9A968E" }}>
                  <div style={{ width: 22, height: 22, borderRadius: 11, flex: "none", marginTop: 2, background: on ? "#D97757" : "#4A4642", fontSize: 13, fontWeight: 800, display: "flex", alignItems: "center", justifyContent: "center" }}>{i + 1}</div>
                  {on ? <Typed text={it.text} delay={start} cps={40} /> : <span>{it.text}</span>}
                </div>
              );
            })}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 6, fontSize: 14, color: "#9A968E" }}>
              <span>+ · Chat · Cowork · <span style={{ color: "#FAF9F5" }}>Code</span></span>
              <div style={{ width: 30, height: 30, borderRadius: 8, background: "#D97757", display: "flex", alignItems: "center", justifyContent: "center" }}><Icon name="arrow" size={18} color="#fff" stroke={2.4} /></div>
            </div>
          </div>
        </div>
        <div style={{ width: 360, minHeight: 260, display: "flex", alignItems: "center", justifyContent: "center" }}>
          {card ? (
            <Card style={{ width: 340, padding: 24, display: "flex", flexDirection: "column", alignItems: "center", gap: 14, opacity: cp, transform: `translateY(${(1 - cp) * 24}px) scale(${lerp(cp, 0.9, 1)})` }}>
              {card.src ? <Img src={card.src} style={{ width: 290, height: 170, objectFit: "cover", borderRadius: 12 }} /> : <IconTile name={card.icon} size={110} active />}
              <div style={{ fontSize: 22, fontWeight: 750, textAlign: "center" }}>{card.label}</div>
            </Card>
          ) : null}
        </div>
      </div>
    </Stage>
  );
};

/* ---------- progress: bar fills, turns into a tick ---------- */
const ProgressT: React.FC<TplProps> = ({ kicker, title, label = "Đang xuất", done = "Xong", from = "", to = "", seed, dur }) => {
  const f = useCurrentFrame();
  const end = Math.max(40, Math.round((dur || 90) * 0.6));
  const p = interpolate(f, [8, end], [0, 1], { ...clamp, easing: ease });
  const ok = interpolate(f, [end, end + 10], [0, 1], clamp);
  const c = useIn(2);
  return (
    <Stage seed={seed}>
      <Head kicker={kicker} title={title} size={46} />
      <Card style={{ width: 760, padding: "26px 30px", opacity: c, transform: `translateY(${(1 - c) * 20}px)` }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <div style={{ fontSize: 24, fontWeight: 700 }}>{ok > 0.5 ? done : label}</div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontSize: 24, fontWeight: 800, fontVariantNumeric: "tabular-nums" }}>{Math.round(p * 100)}%</span>
            <div style={{ width: 40, height: 40, borderRadius: 20, background: GRAD, display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${ok})` }}>
              <Icon name="check" size={24} color="#fff" stroke={3} />
            </div>
          </div>
        </div>
        <div style={{ height: 18, borderRadius: 9, background: "var(--bar)", overflow: "hidden" }}>
          <div style={{ width: `${p * 100}%`, height: "100%", borderRadius: 9, background: GRAD }} />
        </div>
        {from || to ? (
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 12, fontSize: 18, color: L.muted, fontWeight: 600 }}><span>{from}</span><span>{to}</span></div>
        ) : null}
      </Card>
    </Stage>
  );
};

/* ---------- doctilt ---------- */
const DocTiltT: React.FC<TplProps> = ({ src, label, seed }) => {
  const f = useCurrentFrame();
  const a = useIn(2, 20);
  const drift = interpolate(f, [0, 150], [0, 1], clamp);
  const l = useIn(14);
  return (
    <Stage seed={seed}>
      {label ? <div style={{ opacity: l, transform: `translateY(${(1 - l) * -10}px)` }}><Kicker text={label} /></div> : null}
      <div style={{ perspective: 1400 }}>
        <div style={{ width: 920, height: 500, borderRadius: 18, overflow: "hidden", background: "#fff", boxShadow: "var(--deepshadow)",
          transform: `rotateX(${lerp(a, 30, 18)}deg) rotateZ(${lerp(drift, -6, -3)}deg) translateY(${(1 - a) * 60}px) scale(${lerp(drift, 0.98, 1.04)})`, opacity: a }}>
          {src ? <Img src={src} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "top" }} /> : null}
        </div>
      </div>
    </Stage>
  );
};

/* ---------- comments: drifting wall of messages + a big claim ---------- */
const CommentsT: React.FC<TplProps> = ({ items = [], big, sub, seed }) => {
  const f = useCurrentFrame();
  const list = items as Any[];
  const cols = 4;
  const b = useIn(16);
  const dark = useDark();
  return (
    <Stage seed={seed} pad={0}>
      <div style={{ position: "absolute", inset: -40, display: "flex", gap: 20, transform: "rotate(-4deg)", filter: big ? "blur(2.5px)" : "none", opacity: big ? 0.75 : 1 }}>
        {Array.from({ length: cols }, (_, c) => (
          <div key={c} style={{ flex: 1, display: "flex", flexDirection: "column", gap: 18, transform: `translateY(${(c % 2 ? -1 : 1) * (f * 0.6) - 120}px)` }}>
            {Array.from({ length: 6 }, (_, r) => {
              const it = list[(c * 6 + r) % Math.max(1, list.length)] || {};
              return (
                <Card key={r} style={{ padding: "16px 18px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                    <div style={{ width: 30, height: 30, borderRadius: 15, background: "var(--tile)" }} />
                    <div style={{ fontSize: 16, fontWeight: 700 }}>{it.name}</div>
                  </div>
                  <div style={{ fontSize: 16, color: L.ink2, lineHeight: 1.4 }}>{it.text}</div>
                </Card>
              );
            })}
          </div>
        ))}
      </div>
      {big ? (
        <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 8,
          background: dark ? "radial-gradient(60% 50% at 50% 50%, rgba(26,25,24,0.94) 0%, rgba(26,25,24,0) 100%)" : "radial-gradient(60% 50% at 50% 50%, rgba(247,243,236,0.92) 0%, rgba(247,243,236,0) 100%)", opacity: b }}>
          <div style={{ fontFamily: FONT, fontSize: 110, fontWeight: 850, letterSpacing: "-0.04em", transform: `scale(${lerp(b, 0.85, 1)})` }}><GradText>{big}</GradText></div>
          {sub ? <div style={{ fontFamily: FONT, fontSize: 32, fontWeight: 650, color: L.ink }}>{sub}</div> : null}
        </div>
      ) : null}
    </Stage>
  );
};

/* ---------- chapters: the video's chapter list ----------
 * mode "intro": rows blur in, then light up one by one as each chapter is named (`times` = second of
 *               each mention from the scene start, else every `per` frames)
 * mode "focus": the list comes back at a new chapter: done rows ticked, the camera pushes in on row
 *               `focus`, which gets the clay glow while the rest dim and soften
 */
const ChaptersT: React.FC<TplProps> = ({ kicker = "Trong video này", items = [], mode = "intro", focus = 0, per = 14, times, dur, seed }) => {
  const f = useCurrentFrame();
  const list = items as Any[];
  const n = list.length;
  const ROW = 62, GAP = 12, Wd = 860;
  const listH = n * (ROW + GAP) - GAP;
  const intro = mode !== "focus";
  const fo = Math.max(0, Math.min(n - 1, Number(focus)));
  const at = (i: number) => (Array.isArray(times) && times[i] !== undefined ? Math.round(Number(times[i]) * 30) : cueAt(i, 14 + i * Number(per)));
  const push = intro ? 0 : interpolate(f, [6, 28], [0, 1], { ...clamp, easing: ease });
  const drift = interpolate(f, [0, dur || 120], [0, 1], clamp);
  // push in on the focused row: scale up and slide it towards the middle of the frame
  const rowY = fo * (ROW + GAP) + ROW / 2 - listH / 2;
  const scale = 1 + push * 0.07 + drift * 0.02;
  const ty = -rowY * push * 0.85;
  const head = useIn(0);
  return (
    <Stage seed={seed} pad={0}>
      <div style={{ position: "absolute", left: "50%", top: "50%", width: Wd, transform: `translate(-50%, -50%) translateY(${ty}px) scale(${scale})`, transformOrigin: "50% 50%" }}>
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 15, fontWeight: 700, letterSpacing: "0.16em", textTransform: "uppercase", color: L.muted,
          marginBottom: 16, opacity: head * (1 - push * 0.6) }}>
          <span style={{ display: "flex", alignItems: "center", gap: 8 }}><span style={{ width: 7, height: 7, borderRadius: 4, background: "#D97757" }} />{kicker}</span>
          <span>{n} chương</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: GAP }}>
          {list.map((it, i) => {
            const enter = interpolate(f, intro ? [2 + i * 3, 12 + i * 3] : [0, 6], [0, 1], { ...clamp, easing: ease });
            const lit = intro ? interpolate(f, [at(i), at(i) + 8], [0, 1], clamp) : i <= fo ? 1 : 0;
            const sweep = intro ? interpolate(f, [at(i), at(i) + 14], [-30, 130], clamp) : -30;
            const on = !intro && i === fo;
            const done = !intro && i < fo;
            const dim = !intro && !on ? push : 0;
            const glow = on ? push : 0;
            const spin = (f * 9) % 360;
            return (
              // each row is a raised card (top-lit fill, hairline, soft drop shadow); the focused one
              // steps forward: a touch wider, warmer fill, clay rim and glow
              <div key={i} style={{ position: "relative", height: ROW, borderRadius: 16, display: "flex", alignItems: "center", gap: 20, padding: "0 22px", overflow: "hidden",
                background: on ? `linear-gradient(180deg, rgba(64,52,46,${glow}) 0%, rgba(40,35,32,${glow}) 100%), var(--deepcard)` : "var(--deepcard)",
                boxShadow: on && glow > 0.05
                  ? `inset 0 1px 0 rgba(255,255,255,0.12), 0 0 0 ${1 + glow}px rgba(217,119,87,${0.3 + 0.6 * glow}), 0 0 ${44 * glow}px rgba(217,119,87,${0.45 * glow}), 0 30px 70px rgba(0,0,0,0.6)`
                  : "var(--deepshadowcard)",
                opacity: enter * (1 - dim * 0.6), filter: `blur(${(1 - enter) * 8 + dim * 2.6}px)`,
                transform: `translateY(${(1 - enter) * 14}px) scale(${1 + 0.04 * glow})` }}>
                <div style={{ position: "absolute", top: 0, bottom: 0, left: `${sweep}%`, width: "30%", background: "linear-gradient(90deg, rgba(240,180,154,0) 0%, rgba(240,180,154,0.16) 50%, rgba(240,180,154,0) 100%)" }} />
                <div style={{ width: 40, fontSize: 26, fontWeight: 500, letterSpacing: "-0.01em", color: on ? "#E8916F" : L.ink, opacity: 0.35 + 0.65 * lit, fontVariantNumeric: "tabular-nums" }}>{String(i + 1).padStart(2, "0")}</div>
                <div style={{ width: 92, height: 52, borderRadius: 10, overflow: "hidden", flex: "none", display: "flex", alignItems: "center", justifyContent: "center",
                  background: on ? "linear-gradient(180deg, #E8916F 0%, #C15F3C 100%)" : "var(--tile)",
                  boxShadow: on ? "inset 0 1px 0 rgba(255,255,255,0.35), 0 6px 16px rgba(0,0,0,0.45)" : "var(--tileshadow)", opacity: 0.45 + 0.55 * lit }}>
                  {it.src ? <Img src={it.src} style={{ width: "100%", height: "100%", objectFit: "cover", filter: on ? "none" : `grayscale(${1 - lit})` }} /> : <Icon name={it.icon || "play"} size={28} color={on ? "#fff" : "var(--tileic)"} />}
                </div>
                <div style={{ flex: 1, fontSize: 24, fontWeight: on ? 700 : 600, letterSpacing: "-0.01em", color: L.ink, opacity: 0.3 + 0.7 * lit, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{it.title}</div>
                <div style={{ width: 28, display: "flex", justifyContent: "center", opacity: 0.4 + 0.6 * lit }}>
                  {on ? <div style={{ width: 22, height: 22, borderRadius: 11, border: "3px solid #E8916F", borderTopColor: "transparent", transform: `rotate(${spin}deg)` }} />
                    : done ? <Icon name="check" size={24} color="#E8916F" stroke={2.8} /> : <Icon name="lock" size={22} color={L.ink2} stroke={2.2} />}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Stage>
  );
};

export const LEARN: Record<string, React.FC<TplProps>> = {
  chapters: ChaptersT,
  pricecut: PriceCutT,
  receipt: ReceiptT,
  calendar: CalendarT,
  countdown: CountdownT,
  lock: LockT,
  tracker: TrackerT,
  hub: HubT,
  folder: FolderT,
  transcript: TranscriptT,
  scriptclip: ScriptClipT,
  reveal: RevealT,
  linechart: LineChartT,
  beforeafter: BeforeAfterT,
  promptui: PromptUiT,
  progress: ProgressT,
  doctilt: DocTiltT,
  comments: CommentsT,
};
