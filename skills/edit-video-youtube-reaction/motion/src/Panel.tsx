import React from "react";
import {
  AbsoluteFill,
  Sequence,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { GridFloor, Particles } from "./library/motion";
import { useCountUp, vn } from "./library/text";
import { FONT } from "./theme";
import { Rise } from "./ui";
import {
  BarGrowth,
  DualLineTrend,
  BrowserAIFlow,
  ClockCycleTasks,
} from "./templates/MotionStandards";
import { CUSTOM } from "./custom";

/**
 * Panel — a compact animated graphic for the bottom-left corner of a react
 * video (reactforge). One Panel = one presenter segment; it holds several
 * scenes laid end-to-end, each starting when the presenter reaches a phrase.
 *
 * Unlike `Explainer`, this composition is small (≈900×478), has no captions,
 * watermark or voice — those belong to the host video. Colours come from props
 * so the panel matches the host layout, not this project's theme.
 */

export type PanelScene = {
  start: number; // seconds from the start of the segment
  duration: number;
  template:
    | "card"
    | "bignumber"
    | "list"
    | "quote"
    | "compare"
    | "twoline"
    | "browser"
    | "dashboard"
    | "flow"
    | "bots"
    | "bars"
    | "trend"
    | "system_flow"
    | "clock_cycle";
  props: Record<string, any>;
};

export type PanelProps = {
  width: number;
  height: number;
  fps: number;
  accent: string;
  bg: string;
  scenes: PanelScene[];
};

const COL = {
  text: "#F5F5F0",
  muted: "#A0A0A8",
  faint: "#2A2A33",
  card: "#15151C",
};

const Kick: React.FC<{ text?: string; accent: string; delay?: number }> = ({
  text,
  accent,
  delay = 0,
}) =>
  text ? (
    <Rise delay={delay} distance={10}>
      <div
        style={{
          display: "inline-block",
          color: accent,
          fontSize: 17,
          fontWeight: 700,
          letterSpacing: 3.5,
          textTransform: "uppercase",
          opacity: 0.95,
        }}
      >
        {text}
      </div>
    </Rise>
  ) : null;

const Card: React.FC<any> = ({ kicker, title, sub, headline, text, line1, line2, accent }) => {
  const displayTitle = title || headline || text || line1 || kicker || "Tối Ưu Token";
  return (
    <div
      style={{
        backgroundColor: COL.card,
        border: `1.5px solid ${accent}55`,
        borderRadius: 16,
        padding: "26px 32px",
        boxShadow: `0 10px 30px rgba(0,0,0,0.5), 0 0 25px ${accent}22`,
      }}
    >
      <Kick text={kicker} accent={accent} />
      <div style={{ height: 10 }} />
      <Rise delay={6}>
        <div
          style={{
            fontSize: displayTitle.length > 40 ? 38 : displayTitle.length > 22 ? 46 : 56,
            fontWeight: 700,
            lineHeight: 1.15,
            letterSpacing: -0.5,
            background: `linear-gradient(90deg, #FFFFFF, ${accent}, #C4B5FD)`,
            WebkitBackgroundClip: "text",
            color: "transparent",
          }}
        >
          {displayTitle}
        </div>
      </Rise>
      {sub ? (
        <>
          <div style={{ height: 12 }} />
          <Rise delay={18}>
            <div style={{ fontSize: 22, color: "#D1D5DB", lineHeight: 1.35 }}>{sub}</div>
          </Rise>
        </>
      ) : null}
    </div>
  );
};

const BigNumber: React.FC<any> = ({
  kicker,
  value,
  decimals = 0,
  unit,
  headline,
  sub,
  accent,
}) => {
  const n = useCountUp(value, 36, 4);
  return (
    <div
      style={{
        backgroundColor: COL.card,
        border: `1.5px solid ${accent}55`,
        borderRadius: 16,
        padding: "22px 30px",
        boxShadow: `0 10px 30px rgba(0,0,0,0.5), 0 0 25px ${accent}22`,
      }}
    >
      <Kick text={kicker} accent={accent} />
      <div style={{ height: 4 }} />
      <div
        style={{
          fontSize: 104,
          fontWeight: 700,
          lineHeight: 1,
          color: accent,
          letterSpacing: -3,
          display: "flex",
          alignItems: "baseline",
          gap: 14,
          textShadow: `0 0 30px ${accent}55`,
        }}
      >
        {vn(n, decimals)}
        {unit ? (
          <span style={{ fontSize: 34, color: "#FFFFFF", letterSpacing: 0 }}>{unit}</span>
        ) : null}
      </div>
      <div style={{ height: 8 }} />
      <Rise delay={22}>
        <div style={{ fontSize: 28, fontWeight: 700, lineHeight: 1.2, color: "#FFFFFF" }}>{headline}</div>
      </Rise>
      {sub ? (
        <Rise delay={32}>
          <div style={{ fontSize: 20, color: "#9CA3AF", marginTop: 6 }}>{sub}</div>
        </Rise>
      ) : null}
    </div>
  );
};

const List: React.FC<any> = ({ kicker, title, items = [], accent }) => (
  <div
    style={{
      backgroundColor: COL.card,
      border: `1.5px solid ${accent}55`,
      borderRadius: 16,
      padding: "22px 28px",
      boxShadow: `0 10px 30px rgba(0,0,0,0.5), 0 0 25px ${accent}22`,
    }}
  >
    <Kick text={kicker ?? title} accent={accent} />
    <div style={{ height: 12 }} />
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      {(Array.isArray(items) && items.length > 0 ? items : ["Quy tắc 1", "Quy tắc 2", "Quy tắc 3"]).map((item: string, i: number) => (
        <Rise key={i} delay={8 + i * 14} distance={16}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 16,
              backgroundColor: "#1B1B24",
              border: `1px solid ${COL.faint}`,
              borderLeft: `4px solid ${accent}`,
              borderRadius: 10,
              padding: "12px 18px",
            }}
          >
            <span style={{ fontSize: 18, fontWeight: 700, color: accent, minWidth: 30 }}>
              {String(i + 1).padStart(2, "0")}
            </span>
            <span style={{ fontSize: 24, fontWeight: 700, lineHeight: 1.2, color: "#FFFFFF" }}>{item}</span>
          </div>
        </Rise>
      ))}
    </div>
  </div>
);

const Quote: React.FC<any> = ({ kicker, text, title, sub, accent }) => {
  const quoteText = text || title || "";
  return (
    <div
      style={{
        backgroundColor: COL.card,
        border: `1.5px solid ${accent}55`,
        borderRadius: 16,
        padding: "24px 30px",
        boxShadow: `0 10px 30px rgba(0,0,0,0.5), 0 0 25px ${accent}22`,
      }}
    >
      <Kick text={kicker} accent={accent} />
      <div style={{ height: 14 }} />
      <Rise delay={6}>
        <div
          style={{
            borderLeft: `6px solid ${accent}`,
            paddingLeft: 22,
            fontSize: quoteText.length > 60 ? 32 : 42,
            fontWeight: 700,
            lineHeight: 1.2,
            color: "#FFFFFF",
          }}
        >
          “{quoteText}”
        </div>
      </Rise>
      {sub ? (
        <Rise delay={20}>
          <div style={{ fontSize: 22, color: "#9CA3AF", marginTop: 14, paddingLeft: 28 }}>{sub}</div>
        </Rise>
      ) : null}
    </div>
  );
};

const Compare: React.FC<any> = ({
  kicker,
  headline,
  rows,
  leftTitle,
  rightTitle,
  leftDesc,
  rightDesc,
  footnote,
  accent,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (leftTitle || rightTitle) {
    return (
      <div
        style={{
          backgroundColor: COL.card,
          border: `1.5px solid ${accent}55`,
          borderRadius: 16,
          padding: "22px 28px",
          boxShadow: `0 10px 30px rgba(0,0,0,0.5), 0 0 25px ${accent}22`,
        }}
      >
        <Kick text={kicker} accent={accent} />
        <div style={{ height: 8 }} />
        {headline ? (
          <Rise delay={4}>
            <div style={{ fontSize: 26, fontWeight: 700, marginBottom: 12, color: "#FFFFFF" }}>{headline}</div>
          </Rise>
        ) : null}
        <div style={{ display: "flex", gap: 14 }}>
          <Rise delay={8} distance={12} style={{ flex: 1 }}>
            <div
              style={{
                backgroundColor: "#1B1B24",
                border: `1px solid ${COL.faint}`,
                borderLeft: "4px solid #EF4444",
                borderRadius: 12,
                padding: "16px 18px",
                height: "100%",
                boxSizing: "border-box",
              }}
            >
              <div
                style={{
                  fontSize: 16,
                  color: "#EF4444",
                  fontWeight: 700,
                  letterSpacing: 2,
                  textTransform: "uppercase",
                  marginBottom: 8,
                }}
              >
                {leftTitle}
              </div>
              <div style={{ fontSize: 22, fontWeight: 600, color: "#D1D5DB", lineHeight: 1.3 }}>
                {leftDesc}
              </div>
            </div>
          </Rise>
          <Rise delay={16} distance={12} style={{ flex: 1 }}>
            <div
              style={{
                backgroundColor: "#1B1B24",
                border: `2px solid ${accent}`,
                borderRadius: 12,
                padding: "16px 18px",
                height: "100%",
                boxSizing: "border-box",
                boxShadow: `0 0 20px ${accent}33`,
              }}
            >
              <div
                style={{
                  fontSize: 16,
                  color: accent,
                  fontWeight: 700,
                  letterSpacing: 2,
                  textTransform: "uppercase",
                  marginBottom: 8,
                }}
              >
                {rightTitle}
              </div>
              <div style={{ fontSize: 22, fontWeight: 700, color: "#C4B5FD", lineHeight: 1.3 }}>
                {rightDesc}
              </div>
            </div>
          </Rise>
        </div>
      </div>
    );
  }

  const safeRows = Array.isArray(rows) && rows.length > 0 ? rows : [];
  const max = safeRows.length > 0 ? Math.max(...safeRows.map((r: any) => r.value || 1)) : 1;

  return (
    <div
      style={{
        backgroundColor: COL.card,
        border: `1.5px solid ${accent}55`,
        borderRadius: 16,
        padding: "22px 28px",
        boxShadow: `0 10px 30px rgba(0,0,0,0.5), 0 0 25px ${accent}22`,
      }}
    >
      <Kick text={kicker} accent={accent} />
      <div style={{ height: 8 }} />
      <Rise delay={4}>
        <div style={{ fontSize: 28, fontWeight: 700, lineHeight: 1.2, color: "#FFFFFF" }}>{headline}</div>
      </Rise>
      <div style={{ height: 16 }} />
      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {safeRows.map((r: any, i: number) => {
          const grow = interpolate(frame - (14 + i * 12), [0, fps * 0.8], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const eased = 1 - Math.pow(1 - grow, 3);
          const w = Math.max(0.04, (r.value || 1) / max) * eased;
          return (
            <div key={i}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  fontSize: 22,
                  marginBottom: 6,
                  color: r.highlight ? COL.text : COL.muted,
                }}
              >
                <span>{r.label}</span>
                <span style={{ fontWeight: 700, color: r.highlight ? accent : COL.text }}>
                  {r.display}
                </span>
              </div>
              <div style={{ height: 22, backgroundColor: COL.faint, borderRadius: 6, overflow: "hidden" }}>
                <div
                  style={{
                    height: "100%",
                    width: `${w * 100}%`,
                    backgroundColor: r.highlight ? accent : "#5B5B6B",
                    borderRadius: 6,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
      {footnote ? (
        <Rise delay={40}>
          <div style={{ fontSize: 20, color: COL.muted, marginTop: 14 }}>{footnote}</div>
        </Rise>
      ) : null}
    </div>
  );
};

const TwoLine: React.FC<any> = ({ kicker, first, second, line1, line2, title, headline, sub, text, accent }) => {
  const t1 = first ?? line1 ?? kicker ?? "TỐI ƯU HOÁ";
  const t2 = second ?? line2 ?? title ?? headline ?? text ?? sub ?? "Cơ chế hoạt động";
  return (
    <div
      style={{
        backgroundColor: COL.card,
        border: `1.5px solid ${accent}55`,
        borderRadius: 16,
        padding: "26px 32px",
        boxShadow: `0 10px 30px rgba(0,0,0,0.5), 0 0 25px ${accent}22`,
      }}
    >
      <Kick text={kicker} accent={accent} />
      <div style={{ height: 10 }} />
      <Rise delay={4}>
        <div style={{ fontSize: 36, fontWeight: 600, color: "#D1D5DB", lineHeight: 1.25 }}>
          {t1}
        </div>
      </Rise>
      <div style={{ height: 12 }} />
      <Rise delay={20}>
        <div
          style={{
            fontSize: 42,
            fontWeight: 700,
            lineHeight: 1.2,
            background: `linear-gradient(90deg, #FFFFFF, ${accent}, #C4B5FD)`,
            WebkitBackgroundClip: "text",
            color: "transparent",
          }}
        >
          {t2}
        </div>
      </Rise>
    </div>
  );
};

/* ── Drawn illustrations ──────────────────────────────────────────────────────
   Screenshots of the source only show the viewer what they just watched. These
   draw the idea instead, so a talk about a concept has a picture of the concept. */

/** A window with tiles, one lighting up — "the thing lives on this screen, here". */
const Browser: React.FC<any> = ({ kicker, caption, tiles = 6, highlight = 1, accent }) => {
  const frame = useCurrentFrame();
  const pulse = 0.55 + 0.45 * Math.sin(frame * 0.13);
  return (
    <>
      <Kick text={kicker} accent={accent} />
      <div style={{ height: 12 }} />
      <Rise delay={4}>
        <div style={{ border: `2px solid ${COL.faint}`, borderRadius: 12, overflow: "hidden", background: COL.card }}>
          <div style={{ display: "flex", gap: 7, padding: "10px 14px", borderBottom: `2px solid ${COL.faint}` }}>
            {[0, 1, 2].map((i) => (
              <span key={i} style={{ width: 10, height: 10, borderRadius: 5, background: COL.faint }} />
            ))}
            <span style={{ flex: 1, height: 10, borderRadius: 5, background: COL.faint, marginLeft: 10 }} />
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 12, padding: 18 }}>
            {new Array(tiles).fill(0).map((_, i) => {
              const on = i === highlight;
              return (
                <div
                  key={i}
                  style={{
                    width: 148,
                    height: 62,
                    borderRadius: 9,
                    background: on ? `${accent}22` : "#1B1B24",
                    border: on ? `2px solid ${accent}` : `2px solid ${COL.faint}`,
                    opacity: on ? 1 : 0.5,
                    boxShadow: on ? `0 0 ${18 * pulse}px ${accent}66` : "none",
                  }}
                />
              );
            })}
          </div>
        </div>
      </Rise>
      {caption ? (
        <Rise delay={18}>
          <div style={{ fontSize: 24, fontWeight: 700, marginTop: 14, lineHeight: 1.25 }}>{caption}</div>
        </Rise>
      ) : null}
    </>
  );
};

/** A line that climbs while you talk about something climbing. */
const Dashboard: React.FC<any> = ({ kicker, headline, points = [8, 18, 14, 34, 46, 62, 84], rows = [], accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const W = 470;
  const H = 150;
  const grow = interpolate(frame, [6, fps * 1.6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const max = Math.max(...(points as number[]));
  const pts = (points as number[]).map((v, i) => {
    const x = (i / (points.length - 1)) * W;
    const y = H - (v / max) * H;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  const len = 1400;
  return (
    <>
      <Kick text={kicker} accent={accent} />
      <div style={{ height: 10 }} />
      {headline ? (
        <Rise delay={4}>
          <div style={{ fontSize: 28, fontWeight: 700, marginBottom: 12, lineHeight: 1.2 }}>{headline}</div>
        </Rise>
      ) : null}
      <Rise delay={6}>
        <div style={{ background: COL.card, border: `1px solid ${COL.faint}`, borderRadius: 12, padding: "16px 18px" }}>
          <svg width={W} height={H} style={{ display: "block", overflow: "visible" }}>
            {[0.25, 0.5, 0.75].map((g) => (
              <line key={g} x1={0} x2={W} y1={H * g} y2={H * g} stroke={COL.faint} strokeWidth={1} />
            ))}
            <polyline
              points={pts.join(" ")}
              fill="none"
              stroke={accent}
              strokeWidth={4}
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeDasharray={len}
              strokeDashoffset={len * (1 - grow)}
            />
          </svg>
        </div>
      </Rise>
      {(rows as any[]).length ? (
        <div style={{ display: "flex", gap: 26, marginTop: 14 }}>
          {(rows as any[]).map((r, i) => (
            <Rise key={i} delay={22 + i * 8}>
              <div>
                <div style={{ fontSize: 13, letterSpacing: 2, color: COL.muted, textTransform: "uppercase" }}>{r.label}</div>
                <div style={{ fontSize: 30, fontWeight: 700, color: i === 0 ? accent : COL.text }}>{r.value}</div>
              </div>
            </Rise>
          ))}
        </div>
      ) : null}
    </>
  );
};

/** Steps appearing one after another — for "first this, then this, then this". */
const Flow: React.FC<any> = ({ kicker, steps = [], accent }) => (
  <>
    <Kick text={kicker} accent={accent} />
    <div style={{ height: 16 }} />
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      {(steps as string[]).map((st, i) => (
        <React.Fragment key={i}>
          {i > 0 ? (
            <Rise delay={10 + i * 16} distance={0}>
              <div style={{ color: accent, fontSize: 26, fontWeight: 700, opacity: 0.8 }}>→</div>
            </Rise>
          ) : null}
          <Rise delay={6 + i * 16} distance={14}>
            <div
              style={{
                flex: 1,
                minWidth: 150,
                background: COL.card,
                border: `2px solid ${i === steps.length - 1 ? accent : COL.faint}`,
                borderRadius: 12,
                padding: "18px 16px",
                fontSize: 23,
                fontWeight: 700,
                lineHeight: 1.22,
                textAlign: "center",
              }}
            >
              {st}
            </div>
          </Rise>
        </React.Fragment>
      ))}
    </div>
  </>
);

const BotGlyph: React.FC<{ color: string; dim: boolean }> = ({ color, dim }) => (
  <svg width={70} height={70} viewBox="0 0 100 100" style={{ opacity: dim ? 0.38 : 1 }}>
    <rect x="14" y="24" width="72" height="60" rx="16" fill="none" stroke={color} strokeWidth={6} />
    <circle cx="36" cy="50" r="7" fill={color} />
    <circle cx="64" cy="50" r="7" fill={color} />
    <line x1="50" y1="10" x2="50" y2="24" stroke={color} strokeWidth={6} />
    <circle cx="50" cy="8" r="6" fill={color} />
  </svg>
);

/** A row of agents wired together, with the bottleneck named underneath. */
const Bots: React.FC<any> = ({ kicker, count = 5, headline, sub, you, accent }) => {
  const frame = useCurrentFrame();
  return (
    <>
      <Kick text={kicker} accent={accent} />
      <div style={{ height: 14 }} />
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        {new Array(count).fill(0).map((_, i) => (
          <React.Fragment key={i}>
            {i > 0 ? (
              <div
                style={{
                  width: 30,
                  height: 4,
                  borderRadius: 2,
                  background: `linear-gradient(90deg,${COL.faint},${accent})`,
                  opacity: interpolate(frame, [8 + i * 6, 20 + i * 6], [0, 0.9], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
                }}
              />
            ) : null}
            <Rise delay={4 + i * 6} distance={12}>
              <BotGlyph color={i === 0 ? accent : "#5B5570"} dim={i !== 0} />
            </Rise>
          </React.Fragment>
        ))}
      </div>
      {you ? (
        <Rise delay={10 + count * 6}>
          <div
            style={{
              marginTop: 14,
              alignSelf: "flex-start",
              border: `2px solid ${accent}`,
              borderRadius: 11,
              padding: "9px 18px",
              fontSize: 21,
              fontWeight: 700,
            }}
          >
            {you}
          </div>
        </Rise>
      ) : null}
      {headline ? (
        <Rise delay={16 + count * 6}>
          <div style={{ fontSize: 28, fontWeight: 700, marginTop: 14, lineHeight: 1.2 }}>{headline}</div>
        </Rise>
      ) : null}
      {sub ? (
        <Rise delay={24 + count * 6}>
          <div style={{ fontSize: 21, color: COL.muted, marginTop: 6 }}>{sub}</div>
        </Rise>
      ) : null}
    </>
  );
};


const TEMPLATES: Record<PanelScene["template"], React.FC<any>> = {
  card: Card,
  bignumber: BigNumber,
  list: List,
  quote: Quote,
  compare: Compare,
  twoline: TwoLine,
  browser: Browser,
  dashboard: Dashboard,
  flow: Flow,
  bots: Bots,
  bars: BarGrowth,
  trend: DualLineTrend,
  system_flow: BrowserAIFlow,
  clock_cycle: ClockCycleTasks,
};

const Scene: React.FC<{ scene: PanelScene; accent: string }> = ({ scene, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const T = CUSTOM[scene.template] ?? TEMPLATES[scene.template] ?? Card;
  // gentle push-in over the scene so nothing ever sits perfectly still
  // capped at +2.4% over 40s: a bigger push-in walks wide content off the right edge
  const scale = 1 + Math.min(frame, fps * 40) * 0.00002;
  const fadeIn = interpolate(frame, [0, fps * 0.25], [0, 1], { extrapolateRight: "clamp" });
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        padding: "34px 40px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        opacity: fadeIn,
        transform: `scale(${scale})`,
        transformOrigin: "left center",
      }}
    >
      <T {...scene.props} accent={accent} />
    </div>
  );
};

export const Panel: React.FC<PanelProps> = ({ accent, bg, scenes }) => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: bg, fontFamily: FONT, color: COL.text, overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(900px 500px at 20% 0%, ${accent}22 0%, transparent 70%)`,
        }}
      />
      <GridFloor opacity={0.07} />
      <Particles count={18} seed={7} />
      {scenes.map((sc, i) => (
        <Sequence
          key={i}
          from={Math.round(sc.start * fps)}
          durationInFrames={Math.max(1, Math.round(sc.duration * fps))}
          name={`${i}-${sc.template}`}
        >
          <Scene scene={sc} accent={accent} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const PANEL_DEFAULTS: PanelProps = {
  width: 900,
  height: 478,
  fps: 30,
  accent: "#8B7CFF",
  bg: "#0B0B10",
  scenes: [
    {
      start: 0,
      duration: 4,
      template: "bignumber",
      props: { kicker: "MẪU", value: 250, unit: "triệu đô/năm", headline: "16 doanh nghiệp", sub: "gần 18 tỷ mỗi ngày" },
    },
  ],
};
