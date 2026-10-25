import React from "react";
import { AbsoluteFill, Easing, Sequence, interpolate, useCurrentFrame } from "remotion";
import { FONT } from "./kit";

/**
 * Keyword captions for FACE talks, rendered as a transparent layer over the presenter.
 *   line  — one bold line across the frame (may run wider than the presenter), keywords in clay
 *   stack — small context line, the keyword huge underneath (numbers, short punchlines)
 * Words fade in from a blur as they are spoken; the phrase blurs out at its end.
 * Gradient text is painted only inside its own box, so every gradient span carries padding
 * for Vietnamese stacked diacritics (ầ, ễ, ỗ) and descenders — without it they get cut off.
 */
export type KeyWord = { w: string; t: number; hl: boolean };
export type KeyPhrase = { s: number; e: number; style: "line" | "stack"; words: KeyWord[] };
export type KeysProps = { width: number; height: number; fps: number; total: number; phrases: KeyPhrase[]; overs?: Over[] };

const GRAD = "linear-gradient(180deg, #FFBE9C 0%, #F0875E 50%, #D97757 100%)";
// Lifting the words off a busy picture (a white shirt is the worst case) takes both: a soft black
// band rising from the bottom while a phrase is up, and a tight shadow stack hugging each glyph.
const SHADOW = "0 0 3px rgba(0,0,0,.55), 0 2px 8px rgba(0,0,0,.6), 0 6px 24px rgba(0,0,0,.55), 0 14px 60px rgba(0,0,0,.5)";
const GRAD_SHADOW = "drop-shadow(0 0 2px rgba(0,0,0,.65)) drop-shadow(0 3px 10px rgba(0,0,0,.6)) drop-shadow(0 10px 36px rgba(0,0,0,.5))";
const cl = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const EXPO = Easing.bezier(0.16, 1, 0.3, 1);
const W = 1920, H = 1080, SIDE = 80;   // design space; scaled to the output size

/** Width estimate for Inter heavy (fonts load async, so no DOM measuring): ~0.6 em per char. */
const fit = (text: string, size: number, em = 0.6) => Math.min(size, (W - 2 * SIDE) / Math.max(1, text.length * em));

const Grad: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  // padding keeps diacritics / descenders inside the painted box; negative margin cancels it
  <span style={{ display: "inline-block", padding: "0.28em 0.08em 0.22em", margin: "-0.28em -0.08em -0.22em", backgroundImage: GRAD,
    WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent", textShadow: "none",
    filter: GRAD_SHADOW, ...style }}>{children}</span>
);

/** A black gradient from the bottom edge, in and out with the phrase. */
const Band: React.FC<{ len: number; tall: boolean }> = ({ len, tall }) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 8, len - 8, len], [0, 1, 1, 0], cl);
  return <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: tall ? "58%" : "46%", opacity: o,
    background: "linear-gradient(0deg, rgba(0,0,0,.72) 0%, rgba(0,0,0,.45) 38%, rgba(0,0,0,.14) 72%, rgba(0,0,0,0) 100%)" }} />;
};

const useWord = (at: number, len: number) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [at, at + 7], [0, 1], { ...cl, easing: EXPO });
  const out = interpolate(f, [len - 6, len], [1, 0], cl);
  return { opacity: p * out, filter: `blur(${(1 - p) * 12 + (1 - out) * 10}px)`, transform: `translateY(${(1 - p) * 26}px)` };
};

const Word: React.FC<{ w: KeyWord; fps: number; len: number; pop?: boolean }> = ({ w, fps, len, pop }) => {
  const f = useCurrentFrame();
  const st = useWord(Math.round(w.t * fps), len);
  const sc = pop ? interpolate(f, [Math.round(w.t * fps), Math.round(w.t * fps) + 10], [1.18, 1], { ...cl, easing: EXPO }) : 1;
  return (
    <span style={{ display: "inline-block", whiteSpace: "pre", ...st, transform: `${st.transform} scale(${sc})` }}>
      {w.hl ? <Grad>{w.w}</Grad> : w.w}
    </span>
  );
};

const Line: React.FC<{ p: KeyPhrase; fps: number; len: number }> = ({ p, fps, len }) => {
  const text = p.words.map((w) => w.w).join(" ");
  const size = fit(text, 112, 0.58);
  return (
    <div style={{ position: "absolute", left: SIDE, right: SIDE, bottom: 150, display: "flex", justifyContent: "center", gap: "0.26em",
      fontFamily: FONT, fontWeight: 800, fontSize: size, letterSpacing: "-0.025em", lineHeight: 1.15, color: "#fff", textShadow: SHADOW, whiteSpace: "nowrap" }}>
      {p.words.map((w, i) => <Word key={i} w={w} fps={fps} len={len} pop={w.hl} />)}
    </div>
  );
};

const Stack: React.FC<{ p: KeyPhrase; fps: number; len: number }> = ({ p, fps, len }) => {
  const ctx = p.words.filter((w) => !w.hl);
  const key = p.words.filter((w) => w.hl);
  const keyText = key.map((w) => w.w).join(" ");
  const big = fit(keyText, 200, 0.62);
  const small = fit(ctx.map((w) => w.w).join(" "), 66, 0.56);
  // reading order: a phrase that opens on its keyword ("*CapCut* PC") puts the keyword on top
  const keyFirst = p.words[0]?.hl;
  const ctxLine = ctx.length ? (
    <div style={{ display: "flex", gap: "0.26em", fontWeight: 700, fontSize: small, letterSpacing: "-0.015em", lineHeight: 1.2,
      [keyFirst ? "marginTop" : "marginBottom"]: big * 0.04 }}>
      {ctx.map((w, i) => <Word key={i} w={w} fps={fps} len={len} />)}
    </div>
  ) : null;
  const keyLine = (
    <div style={{ display: "flex", gap: "0.22em", fontWeight: 900, fontSize: big, letterSpacing: "-0.035em", lineHeight: 1.12 }}>
      {key.map((w, i) => <Word key={i} w={w} fps={fps} len={len} pop />)}
    </div>
  );
  return (
    <div style={{ position: "absolute", left: SIDE, right: SIDE, bottom: 96, display: "flex", flexDirection: "column", alignItems: "center",
      fontFamily: FONT, color: "#fff", textShadow: SHADOW, whiteSpace: "nowrap" }}>
      {keyFirst ? <>{keyLine}{ctxLine}</> : <>{ctxLine}{keyLine}</>}
    </div>
  );
};

/* ---------- OVER: graphics laid over the presenter (FACE only) ---------- */
// stats     two or three numbers under the chest, counting up together, the last frame flashes clay
// dots      step dots 1-2-3 with a line of text; pills from earlier steps stack above
// status    a small pill with a label (e.g. "6 giờ", "Đang dựng…") near the top
// blurtitle a big title over the presenter; render.py blurs the face underneath for its span

export type Over = { s: number; e: number; tpl: string; props: Record<string, any> };

const useFade = (len: number) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [0, 9], [0, 1], { ...cl, easing: EXPO });
  const out = interpolate(f, [len - 7, len], [1, 0], cl);
  return { p, o: p * out, blur: (1 - p) * 12 + (1 - out) * 10 };
};

const Stats: React.FC<{ props: Record<string, any>; len: number }> = ({ props, len }) => {
  const f = useCurrentFrame();
  const { o, blur, p } = useFade(len);
  const items = (props.items || []) as Record<string, any>[];
  const t = interpolate(f, [4, 40], [0, 1], { ...cl, easing: EXPO });
  const flash = interpolate(f, [40, 44, 56], [0, 1, 0], cl);
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 120, display: "flex", justifyContent: "center", gap: 260, opacity: o, filter: `blur(${blur}px)`, transform: `translateY(${(1 - p) * 24}px)` }}>
      {items.map((it, i) => {
        const v = Number(it.value || 0) * t;
        const s = v.toFixed(Number(it.decimals || 0)).replace(/\B(?=(\d{3})+(?!\d))/g, it.sep || ".");
        return (
          <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", fontFamily: FONT, color: "#fff", textShadow: SHADOW }}>
            <div style={{ fontSize: 40, fontWeight: 650, opacity: 0.9 }}>{it.label}</div>
            <div style={{ fontSize: 150, fontWeight: 850, letterSpacing: "-0.03em", lineHeight: 1.1, color: flash > 0.05 ? `rgb(${255 - 38 * flash},${255 - 136 * flash},${255 - 168 * flash})` : "#fff" }}>
              {it.prefix || ""}{s}<span style={{ fontSize: 52, fontWeight: 700, marginLeft: 10 }}>{it.suffix || ""}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
};

const Dots: React.FC<{ props: Record<string, any>; len: number }> = ({ props, len }) => {
  const { o, blur, p } = useFade(len);
  const n = Number(props.n || 3), act = Number(props.active || 1);
  const pills = (props.pills || []) as string[];
  return (
    <div style={{ position: "absolute", left: SIDE, right: SIDE, bottom: 110, display: "flex", flexDirection: "column", alignItems: "center", gap: 22, fontFamily: FONT,
      opacity: o, filter: `blur(${blur}px)`, transform: `translateY(${(1 - p) * 20}px)` }}>
      {pills.length ? (
        <div style={{ display: "flex", gap: 14 }}>
          {pills.slice(0, act).map((t, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, padding: "14px 30px", borderRadius: 999, background: "rgba(255,255,255,0.94)", color: "#141413", fontSize: 38, fontWeight: 750,
              boxShadow: "0 8px 24px rgba(0,0,0,0.3)" }}>
              <span style={{ width: 18, height: 18, borderRadius: 9, background: i === act - 1 ? "#D97757" : "#B9B4C6" }} />{t}
            </div>
          ))}
        </div>
      ) : null}
      <div style={{ display: "flex", gap: 12 }}>
        {Array.from({ length: n }, (_, i) => (
          <div key={i} style={{ width: 64, height: 64, borderRadius: 16, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 34, fontWeight: 800,
            background: i + 1 === act ? "#D97757" : "rgba(255,255,255,0.22)", color: "#fff", boxShadow: i + 1 === act ? "0 8px 24px rgba(217,119,87,0.5)" : "none" }}>{i + 1}</div>
        ))}
      </div>
      {props.text ? <div style={{ fontSize: 88, fontWeight: 800, letterSpacing: "-0.02em", color: "#fff", textShadow: SHADOW, whiteSpace: "nowrap" }}>{props.text}</div> : null}
    </div>
  );
};

const Status: React.FC<{ props: Record<string, any>; len: number }> = ({ props, len }) => {
  const { o, blur, p } = useFade(len);
  const f = useCurrentFrame();
  const spin = props.spin ? (f * 8) % 360 : 0;
  return (
    <div style={{ position: "absolute", left: props.side === "right" ? undefined : 120, right: props.side === "right" ? 120 : undefined, top: 110, opacity: o, filter: `blur(${blur}px)`,
      transform: `translateY(${(1 - p) * -16}px)`, display: "flex", alignItems: "center", gap: 16, padding: "18px 36px", borderRadius: 999, background: "rgba(255,255,255,0.95)",
      boxShadow: "0 10px 30px rgba(0,0,0,0.3)", fontFamily: FONT, fontSize: 44, fontWeight: 750, color: "#141413" }}>
      <span style={{ width: 22, height: 22, borderRadius: 11, border: "4px solid #D97757", borderTopColor: props.spin ? "transparent" : "#D97757", transform: `rotate(${spin}deg)` }} />
      {props.text}
    </div>
  );
};

const BlurTitle: React.FC<{ props: Record<string, any>; len: number }> = ({ props, len }) => {
  const f = useCurrentFrame();
  const out = interpolate(f, [len - 7, len], [1, 0], cl);
  const words = String(props.title || "").split(/\s+/).filter(Boolean);
  let on = false;
  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 20, fontFamily: FONT, opacity: out }}>
      {props.kicker ? <div style={{ fontSize: 40, fontWeight: 600, color: "rgba(255,255,255,0.85)", textShadow: SHADOW }}>{props.kicker}</div> : null}
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "0 0.26em", maxWidth: 1500, fontSize: 120, fontWeight: 850, letterSpacing: "-0.025em", lineHeight: 1.15, color: "#fff", textShadow: SHADOW }}>
        {words.map((raw, i) => {
          let w = raw;
          if (w.startsWith("*")) { on = true; w = w.slice(1); }
          const close = /\*[^\p{L}\p{N}]*$/u.test(w);
          w = w.replace(/\*/g, "");
          const hl = on;
          if (close) on = false;
          const t = interpolate(f, [4 + i * 3, 11 + i * 3], [0, 1], { ...cl, easing: EXPO });
          return <span key={i} style={{ display: "inline-block", opacity: t, filter: `blur(${(1 - t) * 12}px)`, transform: `translateY(${(1 - t) * 22}px)` }}>{hl ? <Grad>{w}</Grad> : w}</span>;
        })}
      </div>
    </div>
  );
};

const OVERS: Record<string, React.FC<{ props: Record<string, any>; len: number }>> = { stats: Stats, dots: Dots, status: Status, blurtitle: BlurTitle };

export const Keys: React.FC<KeysProps> = ({ width, fps, phrases, overs = [] }) => (
  <AbsoluteFill style={{ backgroundColor: "transparent" }}>
    <div style={{ position: "absolute", left: 0, top: 0, width: W, height: H, transform: `scale(${width / W})`, transformOrigin: "0 0" }}>
      {overs.map((ov, i) => {
        const T = OVERS[ov.tpl];
        if (!T) return null;
        const len = Math.max(8, Math.round((ov.e - ov.s) * fps));
        return (
          <Sequence key={"o" + i} from={Math.round(ov.s * fps)} durationInFrames={len} layout="none">
            <T props={ov.props} len={len} />
          </Sequence>
        );
      })}
      {phrases.map((p, i) => {
        const from = Math.round(p.s * fps);
        const len = Math.max(8, Math.round((p.e - p.s) * fps));
        // word times are absolute; shift them into the phrase's own sequence
        const local = { ...p, words: p.words.map((w) => ({ ...w, t: Math.max(0, w.t - p.s) })) };
        return (
          <Sequence key={i} from={from} durationInFrames={len} layout="none">
            <Band len={len} tall={p.style === "stack"} />
            {p.style === "stack" ? <Stack p={local} fps={fps} len={len} /> : <Line p={local} fps={fps} len={len} />}
          </Sequence>
        );
      })}
    </div>
  </AbsoluteFill>
);

export const KEYS_DEFAULTS: KeysProps = {
  width: 1920, height: 1080, fps: 30, total: 3,
  phrases: [{ s: 0.2, e: 2.8, style: "stack", words: [{ w: "đôi", t: 0.2, hl: false }, { w: "dép", t: 0.4, hl: false }, { w: "20", t: 0.7, hl: true }, { w: "nghìn", t: 0.9, hl: true }] }],
};

export const keysMeta = (p: KeysProps) => ({ durationInFrames: Math.max(1, Math.ceil(p.total * p.fps)), fps: p.fps, width: p.width, height: p.height });
