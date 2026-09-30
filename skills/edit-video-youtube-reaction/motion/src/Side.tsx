import React from "react";
import {
  AbsoluteFill,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  Img,
} from "remotion";
import { GridFloor, Particles } from "./library/motion";
import { useCountUp, vn } from "./library/text";
import { FONT } from "./theme";
import { Rise } from "./ui";
import { CUSTOM } from "./custom";
import {
  BarGrowth,
  DualLineTrend,
  BrowserAIFlow,
  ClockCycleTasks,
} from "./templates/MotionStandards";

/**
 * Side — a tall 900x1016 animated composition taking over the left half of the
 * screen beside the talking-head presenter (reactforge).
 *
 * Perfect for multi-step roadmaps, vertical timelines, tall comparison cards,
 * full-height bar/trend charts, tech flow architectures, and high-res visual assets.
 */

export type SideScene = {
  start: number; // seconds from segment start
  duration: number;
  template:
    | "steps"
    | "image"
    | "bars"
    | "trend"
    | "system_flow"
    | "clock_cycle"
    | "card"
    | "bignumber"
    | "list"
    | "compare"
    | "flow"
    | "dashboard"
    | "quote"
    | "twoline"
    | "browser";
  props: Record<string, any>;
};

export type SideProps = {
  width: number;
  height: number;
  fps: number;
  accent: string;
  bg: string;
  scenes: SideScene[];
};

const COL = {
  text: "#F5F5F0",
  muted: "#A0A0A8",
  faint: "#2A2A33",
  card: "#15151C",
  border: "rgba(255, 255, 255, 0.08)",
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
          display: "inline-flex",
          alignItems: "center",
          gap: 8,
          color: accent,
          fontSize: 18,
          fontWeight: 700,
          letterSpacing: 3.5,
          textTransform: "uppercase",
          opacity: 0.95,
          marginBottom: 12,
        }}
      >
        <span
          style={{
            width: 8,
            height: 8,
            borderRadius: "50%",
            backgroundColor: accent,
            boxShadow: `0 0 10px ${accent}`,
          }}
        />
        {text}
      </div>
    </Rise>
  ) : null;

/** 1. Vertical Multi-Step Roadmap (Bước 1 -> Bước 2 -> Bước 3) */
const StepsTemplate: React.FC<{
  kicker?: string;
  headline?: string;
  steps?: { title: string; desc?: string; tag?: string }[];
  accent: string;
}> = ({
  kicker = "QUY TRÌNH",
  headline = "Các Bước Thực Hiện",
  steps = [
    { title: "Bước 1: Bóc băng tự động", desc: "Whisper AI nhận diện văn bản chính xác", tag: "AI" },
    { title: "Bước 2: Cắt bỏ đoạn lặp & vấp", desc: "Giữ lại ý cuối hoàn chỉnh nhất", tag: "Claude" },
    { title: "Bước 3: Dựng Motion Graphic", desc: "Mỗi 10s có 1 visual trực quan mới", tag: "React" },
    { title: "Bước 4: Xuất bản hoàn chỉnh", desc: "Cân bằng âm thanh, video 60fps", tag: "FFmpeg" },
  ],
  accent,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", justifyContent: "center" }}>
      <Kick text={kicker} accent={accent} />
      <Rise delay={4}>
        <div style={{ fontSize: 52, fontWeight: 700, color: COL.text, letterSpacing: -1, lineHeight: 1.15, marginBottom: 40 }}>
          {headline}
        </div>
      </Rise>

      <div style={{ display: "flex", flexDirection: "column", gap: 20, position: "relative" }}>
        {/* Glow connector line */}
        <div
          style={{
            position: "absolute",
            left: 24,
            top: 30,
            bottom: 30,
            width: 3,
            background: `linear-gradient(180deg, ${accent} 0%, rgba(255,255,255,0.1) 100%)`,
            zIndex: 0,
          }}
        />

        {steps.map((st, i) => {
          const delay = 8 + i * 8;
          const s = spring({ frame: frame - delay, fps, config: { damping: 14 } });
          const active = i === 1;

          return (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "flex-start",
                gap: 20,
                opacity: interpolate(s, [0, 1], [0, 1]),
                transform: `translateX(${interpolate(s, [0, 1], [-20, 0])}px)`,
                zIndex: 1,
              }}
            >
              {/* Step indicator node */}
              <div
                style={{
                  width: 50,
                  height: 50,
                  borderRadius: 16,
                  backgroundColor: active ? accent : "#1A1A24",
                  border: `2px solid ${active ? "#FFFFFF" : accent}44`,
                  color: active ? "#0B0B10" : COL.text,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 22,
                  fontWeight: 800,
                  boxShadow: active ? `0 0 24px ${accent}88` : "none",
                  flexShrink: 0,
                }}
              >
                0{i + 1}
              </div>

              {/* Step content card */}
              <div
                style={{
                  flex: 1,
                  background: active ? `linear-gradient(135deg, ${accent}22 0%, #15151C 100%)` : "#15151C",
                  border: `1px solid ${active ? accent + "66" : COL.border}`,
                  borderRadius: 16,
                  padding: "16px 22px",
                  backdropFilter: "blur(12px)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div style={{ fontSize: 24, fontWeight: 700, color: COL.text }}>{st.title}</div>
                  {st.tag && (
                    <span
                      style={{
                        fontSize: 13,
                        fontWeight: 700,
                        padding: "4px 10px",
                        borderRadius: 8,
                        backgroundColor: active ? accent : "rgba(255,255,255,0.06)",
                        color: active ? "#0B0B10" : accent,
                        letterSpacing: 1,
                      }}
                    >
                      {st.tag}
                    </span>
                  )}
                </div>
                {st.desc && (
                  <div style={{ fontSize: 17, color: COL.muted, marginTop: 6, lineHeight: 1.4 }}>
                    {st.desc}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

/** 2. Image / Visual Illustration Card (Gemini generated visual or B-roll mock) */
const ImageTemplate: React.FC<{
  kicker?: string;
  headline?: string;
  src?: string;
  caption?: string;
  tags?: string[];
  accent: string;
}> = ({ kicker = "MINH HOẠ", headline = "Visual Concept", src, caption, tags = ["AI Generated", "Trực quan 4K"], accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - 6, fps, config: { damping: 14 } });

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", justifyContent: "center" }}>
      <Kick text={kicker} accent={accent} />
      <Rise delay={4}>
        <div style={{ fontSize: 48, fontWeight: 700, color: COL.text, letterSpacing: -1, lineHeight: 1.15, marginBottom: 24 }}>
          {headline}
        </div>
      </Rise>

      <div
        style={{
          borderRadius: 24,
          overflow: "hidden",
          border: `1px solid ${accent}55`,
          background: "#12121A",
          boxShadow: `0 20px 50px rgba(0,0,0,0.6), 0 0 30px ${accent}22`,
          opacity: interpolate(s, [0, 1], [0, 1]),
          transform: `scale(${interpolate(s, [0, 1], [0.94, 1])})`,
        }}
      >
        {src ? (
          <Img
            src={src}
            style={{
              width: "100%",
              height: 480,
              objectFit: "cover",
              display: "block",
            }}
          />
        ) : (
          <div
            style={{
              width: "100%",
              height: 480,
              background: `radial-gradient(circle at 50% 50%, ${accent}33 0%, #151520 80%)`,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: 16,
            }}
          >
            <div style={{ fontSize: 64 }}>🎨</div>
            <div style={{ fontSize: 22, fontWeight: 600, color: COL.muted }}>Hình ảnh minh họa</div>
          </div>
        )}

        <div style={{ padding: "20px 26px", backgroundColor: "#15151E" }}>
          {caption && (
            <div style={{ fontSize: 20, color: COL.text, fontWeight: 500, lineHeight: 1.4, marginBottom: 14 }}>
              {caption}
            </div>
          )}
          <div style={{ display: "flex", gap: 10 }}>
            {tags.map((tg, idx) => (
              <span
                key={idx}
                style={{
                  fontSize: 14,
                  fontWeight: 600,
                  padding: "5px 12px",
                  borderRadius: 10,
                  backgroundColor: "rgba(255,255,255,0.06)",
                  color: accent,
                  border: `1px solid ${accent}33`,
                }}
              >
                #{tg}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

/** 3. Tall BigNumber Card with Extra Insights */
const BigNumberTemplate: React.FC<{
  kicker?: string;
  value: number;
  decimals?: number;
  unit?: string;
  headline: string;
  sub?: string;
  insights?: string[];
  accent: string;
}> = ({ kicker, value, decimals = 0, unit, headline, sub, insights = [], accent }) => {
  const current = useCountUp(value, 20);
  const formatted = decimals > 0 ? current.toFixed(decimals) : vn(Math.round(current));

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", justifyContent: "center" }}>
      <Kick text={kicker} accent={accent} />
      <div style={{ display: "flex", alignItems: "baseline", gap: 14, marginTop: 12 }}>
        <span
          style={{
            fontSize: 120,
            fontWeight: 800,
            letterSpacing: -4,
            lineHeight: 0.95,
            color: COL.text,
            textShadow: `0 0 35px ${accent}44`,
          }}
        >
          {formatted}
        </span>
        {unit && (
          <span style={{ fontSize: 36, fontWeight: 600, color: accent, letterSpacing: -0.5 }}>
            {unit}
          </span>
        )}
      </div>

      <Rise delay={8}>
        <div style={{ fontSize: 44, fontWeight: 700, color: COL.text, marginTop: 24, lineHeight: 1.15 }}>
          {headline}
        </div>
      </Rise>

      {sub && (
        <Rise delay={12}>
          <div style={{ fontSize: 24, color: COL.muted, marginTop: 12, lineHeight: 1.4 }}>
            {sub}
          </div>
        </Rise>
      )}

      {insights.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 36 }}>
          {insights.map((ins, i) => (
            <Rise key={i} delay={16 + i * 6}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 14,
                  padding: "14px 20px",
                  borderRadius: 14,
                  backgroundColor: "#161622",
                  border: `1px solid ${COL.border}`,
                }}
              >
                <span style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: accent }} />
                <span style={{ fontSize: 20, color: COL.text }}>{ins}</span>
              </div>
            </Rise>
          ))}
        </div>
      )}
    </div>
  );
};

/** 4. Rich List Template (takes advantage of 1016px height) */
const ListTemplate: React.FC<{
  kicker?: string;
  headline?: string;
  items: string[];
  accent: string;
}> = ({ kicker, headline = "Danh Sách Trọng Tâm", items = [], accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", justifyContent: "center" }}>
      <Kick text={kicker} accent={accent} />
      <Rise delay={4}>
        <div style={{ fontSize: 50, fontWeight: 700, color: COL.text, letterSpacing: -1, lineHeight: 1.15, marginBottom: 36 }}>
          {headline}
        </div>
      </Rise>

      <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
        {items.map((it, i) => {
          const s = spring({ frame: frame - (8 + i * 6), fps, config: { damping: 14 } });
          return (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 18,
                padding: "20px 24px",
                borderRadius: 18,
                backgroundColor: "#151520",
                border: `1px solid ${COL.border}`,
                opacity: interpolate(s, [0, 1], [0, 1]),
                transform: `translateX(${interpolate(s, [0, 1], [-20, 0])}px)`,
                boxShadow: "0 8px 24px rgba(0,0,0,0.3)",
              }}
            >
              <div
                style={{
                  width: 38,
                  height: 38,
                  borderRadius: 12,
                  backgroundColor: `${accent}22`,
                  border: `1px solid ${accent}`,
                  color: accent,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 18,
                  fontWeight: 800,
                  flexShrink: 0,
                }}
              >
                ✓
              </div>
              <div style={{ fontSize: 24, fontWeight: 600, color: COL.text, lineHeight: 1.35 }}>
                {it}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

/** 5. Compare Template (Before vs After / AI vs Traditional) */
const CompareTemplate: React.FC<{
  kicker?: string;
  leftTitle: string;
  leftItems: string[];
  rightTitle: string;
  rightItems: string[];
  accent: string;
}> = ({
  kicker = "SO SÁNH",
  leftTitle = "Thủ công",
  leftItems = ["Mất 4-6 giờ cắt gọt", "Dễ sót lỗi vấp từ", "Chi phí nhân sự cao"],
  rightTitle = "Antigravity AI",
  rightItems = ["Tự động cắt sạch trong 10s", "Giữ ý cuối hoàn chỉnh", "Motion Graphic sinh bằng code"],
  accent,
}) => {
  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", justifyContent: "center" }}>
      <Kick text={kicker} accent={accent} />
      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: 24, marginTop: 12 }}>
        {/* Bad / Old Way */}
        <div
          style={{
            padding: "24px 28px",
            borderRadius: 20,
            backgroundColor: "#161418",
            border: "1px solid rgba(239, 68, 68, 0.3)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 26, fontWeight: 700, color: "#EF4444", marginBottom: 16 }}>
            <span>✕</span> {leftTitle}
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {leftItems.map((item, i) => (
              <div key={i} style={{ fontSize: 19, color: COL.muted, display: "flex", gap: 10 }}>
                <span style={{ color: "#EF4444" }}>•</span> {item}
              </div>
            ))}
          </div>
        </div>

        {/* Good / New Way */}
        <div
          style={{
            padding: "24px 28px",
            borderRadius: 20,
            backgroundColor: "#131A1E",
            border: `1px solid ${accent}88`,
            boxShadow: `0 10px 30px ${accent}22`,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 26, fontWeight: 700, color: accent, marginBottom: 16 }}>
            <span>✓</span> {rightTitle}
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {rightItems.map((item, i) => (
              <div key={i} style={{ fontSize: 20, color: COL.text, fontWeight: 500, display: "flex", gap: 10 }}>
                <span style={{ color: accent }}>•</span> {item}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const TEMPLATES: Record<string, React.FC<any>> = {
  steps: StepsTemplate,
  image: ImageTemplate,
  bignumber: BigNumberTemplate,
  list: ListTemplate,
  compare: CompareTemplate,
  bars: BarGrowth,
  trend: DualLineTrend,
  system_flow: BrowserAIFlow,
  clock_cycle: ClockCycleTasks,
};

const SideSceneRenderer: React.FC<{ scene: SideScene; accent: string }> = ({ scene, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const T = CUSTOM[scene.template] ?? TEMPLATES[scene.template] ?? StepsTemplate;

  const scale = 1 + Math.min(frame, fps * 40) * 0.00002;
  const fadeIn = interpolate(frame, [0, fps * 0.25], [0, 1], { extrapolateRight: "clamp" });

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        padding: "48px 52px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        opacity: fadeIn,
        transform: `scale(${scale})`,
        transformOrigin: "center center",
      }}
    >
      <T {...scene.props} accent={accent} />
    </div>
  );
};

export const Side: React.FC<SideProps> = ({ accent, bg, scenes }) => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: bg, fontFamily: FONT, color: COL.text, overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(800px 900px at 20% 10%, ${accent}26 0%, transparent 75%)`,
        }}
      />
      <GridFloor opacity={0.08} />
      <Particles count={24} seed={9} />
      {scenes.map((sc, i) => (
        <Sequence
          key={i}
          from={Math.round(sc.start * fps)}
          durationInFrames={Math.max(1, Math.round(sc.duration * fps))}
          name={`${i}-${sc.template}`}
        >
          <SideSceneRenderer scene={sc} accent={accent} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const SIDE_DEFAULTS: SideProps = {
  width: 900,
  height: 1016,
  fps: 30,
  accent: "#8B7CFF",
  bg: "#0B0B10",
  scenes: [
    {
      start: 0,
      duration: 5,
      template: "steps",
      props: {
        kicker: "TỔNG QUAN",
        headline: "Quy trình Dựng Video",
      },
    },
  ],
};
