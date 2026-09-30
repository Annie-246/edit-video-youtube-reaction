import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Particles } from "./library/motion";
import { FONT } from "./theme";
import { Rise } from "./ui";
import {
  BarGrowth,
  DualLineTrend,
  BrowserAIFlow,
  ClockCycleTasks,
  TokenComparisonTable,
  AnthropicModelRoles,
  ExponentialCostSurge,
} from "./templates/MotionStandards";

/**
 * Card — a full-frame graphic that takes over a react video for a few seconds.
 *
 * Jobs:
 *   question        — a question the video is about to answer
 *   beat            — a punchline or a feeling; bigger, italic, room for one emoji
 *   chapter         — a section title plus a beat of silence between parts
 *   bars            — full-frame rising bar chart
 *   trend           — full-frame dual line trend chart
 *   system_flow     — full-frame browser & AI decision system flow
 *   clock_cycle     — full-frame 24/7 task clock cycle
 *   token_table     — 3-column comparison table for Input, Output, Cache Read
 *   anthropic_roles — 4 Anthropic models as company employee roles
 *   cost_surge      — skyrocketing token cost counter & money surge
 */

export type CardStyle =
  | "question"
  | "beat"
  | "chapter"
  | "bars"
  | "trend"
  | "system_flow"
  | "clock_cycle"
  | "token_table"
  | "anthropic_roles"
  | "cost_surge"
  | "illustration";

export type CardProps = {
  width: number;
  height: number;
  fps: number;
  secs: number;
  accent: string;
  bg: string;
  style: CardStyle;
  kicker?: string;
  title: string;
  sub?: string;
  emoji?: string;
  images?: string[];
};

export const CARD_DEFAULTS: CardProps = {
  width: 1920,
  height: 1080,
  fps: 30,
  secs: 3.6,
  accent: "#8B7CFF",
  bg: "#0B0B10",
  style: "question",
  kicker: "CÂU HỎI",
  title: "Vì sao càng mở nhiều AI, công việc của bạn lại càng chậm đi?",
  sub: "",
};

/** Wrap long Vietnamese so no line is left with one orphan word. */
const balance = (s: string): string => s;


/** Two slow blobs in the HOST video's accent colour.
 *  `Aurora` from the library is tied to this project's own palette, which turns a card
 *  orange inside a purple channel — a card must match the video it interrupts. */
const Glow: React.FC<{ accent: string; intensity: number }> = ({ accent, intensity }) => {
  const frame = useCurrentFrame();
  const a = frame * 0.0042;
  const blobs = [
    { x: 50 + Math.sin(a) * 22, y: 30 + Math.cos(a * 0.8) * 14, c: accent, s: 900, o: 0.2 * intensity },
    { x: 46 + Math.cos(a * 0.63 + 2) * 26, y: 66 + Math.sin(a * 0.9 + 1) * 16, c: "#4A3AFF", s: 760, o: 0.13 * intensity },
  ];
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      {blobs.map((b, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: `${b.x}%`,
            top: `${b.y}%`,
            width: b.s,
            height: b.s,
            marginLeft: -b.s / 2,
            marginTop: -b.s / 2,
            borderRadius: "50%",
            background: `radial-gradient(circle, ${b.c} 0%, transparent 66%)`,
            opacity: b.o,
            filter: "blur(40px)",
          }}
        />
      ))}
    </AbsoluteFill>
  );
};

export const Card: React.FC<CardProps> = ({
  width,
  height,
  accent,
  bg,
  style,
  kicker,
  title,
  sub,
  emoji,
  images = [],
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const k = width / 1920;

  // Hold still in the middle; drift very slightly in and out so the card feels alive
  // without pulling the eye off the words.
  const scale = interpolate(frame, [0, durationInFrames], [1.0, 1.035], {
    extrapolateRight: "clamp",
  });

  const beat = style === "beat";
  const chapter = style === "chapter";
  const titleSize = (beat ? 84 : chapter ? 92 : 82) * k;

  if (style === "bars") {
    return (
      <AbsoluteFill style={{ background: bg, fontFamily: FONT, color: "#fff", overflow: "hidden" }}>
        <Glow accent={accent} intensity={1.2} />
        <BarGrowth accent={accent} kicker={kicker} headline={title} width={1200 * k} height={600 * k} />
      </AbsoluteFill>
    );
  }
  if (style === "trend") {
    return (
      <AbsoluteFill style={{ background: bg, fontFamily: FONT, color: "#fff", overflow: "hidden" }}>
        <Glow accent={accent} intensity={1.2} />
        <DualLineTrend accent={accent} kicker={kicker} headline={title} width={1280 * k} height={560 * k} />
      </AbsoluteFill>
    );
  }
  if (style === "system_flow") {
    return (
      <AbsoluteFill style={{ background: bg, fontFamily: FONT, color: "#fff", overflow: "hidden" }}>
        <Glow accent={accent} intensity={1.2} />
        <BrowserAIFlow accent={accent} kicker={kicker} headline={title} />
      </AbsoluteFill>
    );
  }
  if (style === "clock_cycle") {
    return (
      <AbsoluteFill style={{ background: bg, fontFamily: FONT, color: "#fff", overflow: "hidden" }}>
        <Glow accent={accent} intensity={1.2} />
        <ClockCycleTasks accent={accent} kicker={kicker} headline={title} />
      </AbsoluteFill>
    );
  }
  if (style === "token_table") {
    return (
      <AbsoluteFill style={{ background: bg, fontFamily: FONT, color: "#fff", overflow: "hidden" }}>
        <Glow accent={accent} intensity={1.2} />
        <TokenComparisonTable accent={accent} kicker={kicker} headline={title} />
      </AbsoluteFill>
    );
  }
  if (style === "anthropic_roles") {
    return (
      <AbsoluteFill style={{ background: bg, fontFamily: FONT, color: "#fff", overflow: "hidden" }}>
        <Glow accent={accent} intensity={1.2} />
        <AnthropicModelRoles accent={accent} kicker={kicker} headline={title} />
      </AbsoluteFill>
    );
  }
  if (style === "cost_surge") {
    return (
      <AbsoluteFill style={{ background: bg, fontFamily: FONT, color: "#fff", overflow: "hidden" }}>
        <Glow accent={accent} intensity={1.2} />
        <ExponentialCostSurge accent={accent} kicker={kicker} headline={title} />
      </AbsoluteFill>
    );
  }

  if (style === "illustration" || (images && images.length > 0)) {
    const safeImages = images && images.length > 0 ? images : [];
    const numImages = Math.max(1, safeImages.length);
    const framesPerImage = durationInFrames / numImages;
    const activeIndex = Math.min(numImages - 1, Math.floor(frame / framesPerImage));
    const nextIndex = Math.min(numImages - 1, activeIndex + 1);
    const progressInSegment = (frame % framesPerImage) / framesPerImage;

    const crossfadeFrames = Math.min(24, framesPerImage * 0.25);
    const framesFromEnd = framesPerImage - (frame % framesPerImage);
    const fadeOpacity = framesFromEnd < crossfadeFrames && activeIndex < numImages - 1
      ? 1 - (framesFromEnd / crossfadeFrames)
      : 0;

    const zoom = 1.0 + progressInSegment * 0.08;

    return (
      <AbsoluteFill style={{ backgroundColor: "#0B0B10", fontFamily: FONT, overflow: "hidden" }}>
        {safeImages.length > 0 && (
          <div
            style={{
              position: "absolute",
              inset: 0,
              transform: `scale(${zoom})`,
              transformOrigin: "center center",
            }}
          >
            <img
              src={safeImages[activeIndex]}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
              alt="illustration"
            />
          </div>
        )}

        {fadeOpacity > 0 && nextIndex !== activeIndex && (
          <div
            style={{
              position: "absolute",
              inset: 0,
              opacity: fadeOpacity,
              transform: `scale(1.0)`,
              transformOrigin: "center center",
            }}
          >
            <img
              src={safeImages[nextIndex]}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
              alt="next illustration"
            />
          </div>
        )}

        {/* Dark gradient vignettes for cinematic readability */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "linear-gradient(to top, rgba(11,11,16,0.95) 0%, rgba(11,11,16,0.4) 45%, transparent 75%)",
          }}
        />
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.65) 100%)",
          }}
        />
        <Particles count={25} seed={5} />

        {/* Glassmorphism Title Badge */}
        <div
          style={{
            position: "absolute",
            bottom: 60,
            left: "50%",
            transform: "translateX(-50%)",
            maxWidth: 1200,
            width: "90%",
            backgroundColor: "rgba(15, 15, 23, 0.88)",
            border: `1.5px solid ${accent}66`,
            borderRadius: 20,
            padding: "24px 36px",
            boxShadow: `0 20px 50px rgba(0,0,0,0.7), 0 0 30px ${accent}25`,
            backdropFilter: "blur(20px)",
            textAlign: "center",
          }}
        >
          {kicker ? (
            <div
              style={{
                fontSize: 16,
                fontWeight: 700,
                letterSpacing: 3,
                color: accent,
                textTransform: "uppercase",
                marginBottom: 8,
              }}
            >
              {kicker}
            </div>
          ) : null}
          <div
            style={{
              fontSize: title.length > 50 ? 32 : 38,
              fontWeight: 700,
              color: "#FFFFFF",
              lineHeight: 1.25,
              letterSpacing: -0.5,
            }}
          >
            {title}
          </div>
          {sub ? (
            <div
              style={{
                fontSize: 20,
                color: "#D1D5DB",
                marginTop: 8,
                lineHeight: 1.3,
              }}
            >
              {sub}
            </div>
          ) : null}
        </div>
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill style={{ background: bg, fontFamily: FONT, color: "#fff" }}>
      {/* chapter cards stay austere — they are a rest, not an event */}
      {!chapter && <Glow accent={accent} intensity={beat ? 1.25 : 1.0} />}
      <Particles count={chapter ? 16 : 58} seed={beat ? 7 : 3} />
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          padding: `0 ${120 * k}px`,
          transform: `scale(${scale})`,
        }}
      >
        {emoji ? (
          <Rise delay={2} distance={18 * k}>
            <div style={{ fontSize: 96 * k, marginBottom: 18 * k, textAlign: "center" }}>{emoji}</div>
          </Rise>
        ) : null}
        {kicker ? (
          <Rise delay={0} distance={12 * k}>
            <div
              style={{
                color: accent,
                fontSize: 26 * k,
                fontWeight: 700,
                letterSpacing: 7 * k,
                textTransform: "uppercase",
                marginBottom: 30 * k,
                textAlign: "center",
              }}
            >
              {kicker}
            </div>
          </Rise>
        ) : null}
        <Rise delay={5} distance={26 * k}>
          <div
            style={{
              fontSize: titleSize,
              fontWeight: 700,
              lineHeight: 1.16,
              textAlign: "center",
              maxWidth: 1460 * k,
              letterSpacing: -0.5 * k,
              fontStyle: beat ? "italic" : "normal",
              ...(chapter
                ? { color: "#fff" }
                : {
                    background: `linear-gradient(90deg,#ffffff 52%,${accent})`,
                    WebkitBackgroundClip: "text",
                    color: "transparent",
                  }),
            }}
          >
            {balance(title)}
          </div>
        </Rise>
        {chapter ? (
          <Rise delay={12} distance={10 * k}>
            <div
              style={{
                marginTop: 38 * k,
                width: 180 * k,
                height: 6 * k,
                borderRadius: 3 * k,
                background: `linear-gradient(90deg,${accent},#C4B5FD)`,
              }}
            />
          </Rise>
        ) : null}
        {sub ? (
          <Rise delay={14} distance={14 * k}>
            <div
              style={{
                marginTop: 34 * k,
                fontSize: 32 * k,
                color: "rgba(255,255,255,.76)",
                textAlign: "center",
                maxWidth: 1200 * k,
              }}
            >
              {sub}
            </div>
          </Rise>
        ) : null}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
