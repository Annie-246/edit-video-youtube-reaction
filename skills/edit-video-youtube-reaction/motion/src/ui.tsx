import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { LivingBackdrop } from "./library/motion";
import { BRAND, C, CREDITS, FONT } from "./theme";

/** Fade + rise, driven purely by frame → deterministic across renders. */
export const Rise: React.FC<{
  delay?: number;
  children: React.ReactNode;
  distance?: number;
}> = ({ delay = 0, children, distance = 28 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 200 } });
  return (
    <div
      style={{
        opacity: s,
        transform: `translateY(${interpolate(s, [0, 1], [distance, 0])}px)`,
      }}
    >
      {children}
    </div>
  );
};

/**
 * Renders copy with `*starred*` fragments in the accent colour, so content
 * files can control emphasis without templates hard-coding which words matter.
 */
export const Hi: React.FC<{ text: string; color?: string }> = ({
  text,
  color = C.accent,
}) => (
  <>
    {text.split(/(\*[^*]+\*)/g).map((part, i) =>
      part.startsWith("*") && part.endsWith("*") && part.length > 2 ? (
        <span key={i} style={{ color }}>
          {part.slice(1, -1)}
        </span>
      ) : (
        <React.Fragment key={i}>{part}</React.Fragment>
      ),
    )}
  </>
);

export const Kicker: React.FC<{ children: React.ReactNode; delay?: number }> = ({
  children,
  delay = 0,
}) => (
  <Rise delay={delay} distance={14}>
    <div
      style={{
        display: "inline-block",
        border: `2px solid ${C.accent}`,
        color: C.accent,
        borderRadius: 999,
        padding: "10px 26px",
        fontSize: 26,
        fontWeight: 700,
        letterSpacing: 4,
        textTransform: "uppercase",
      }}
    >
      {children}
    </div>
  </Rise>
);

/** Word-level captions driven by real ElevenLabs timings. */
export const Captions: React.FC<{
  words: { w: string; start: number; end: number }[];
}> = ({ words }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  // Show a short chunk, not the whole sentence. A full paragraph in a pill
  // grows to three lines and swallows the frame; the reference video keeps
  // roughly half a dozen words on screen at a time.
  const CHUNK = 7;
  let cursor = words.findIndex((w) => t < w.end + 0.12);
  if (cursor === -1) cursor = words.length - 1;
  const start = Math.max(0, Math.floor(cursor / CHUNK) * CHUNK);
  const visible = words.slice(start, start + CHUNK);

  return (
    <div
      style={{
        position: "absolute",
        bottom: 96,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        padding: "0 180px",
      }}
    >
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        alignItems: "center",
        gap: "0 12px",
        fontSize: 34,
        fontWeight: 700,
        backgroundColor: "rgba(10,10,12,0.82)",
        borderRadius: 16,
        padding: "16px 30px",
        maxWidth: 1500,
        whiteSpace: "nowrap",
      }}
    >
      <span style={{ color: C.accent, marginRight: 6 }}>▶</span>
      {visible.map((word, i) => {
        const on = t >= word.start - 0.05;
        const active = t >= word.start - 0.05 && t <= word.end + 0.12;
        return (
          <span
            key={i}
            style={{
              color: active ? C.accent : on ? C.text : C.faint,
              transition: "none",
            }}
          >
            {word.w}
          </span>
        );
      })}
    </div>
    </div>
  );
};

/**
 * Colour panel that sweeps off at the top of every scene, so cuts land as a
 * wipe rather than a hard jump. Frame-driven and short enough not to eat the
 * scene's opening beat.
 */
const WipeIn: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const dur = fps * 0.42;
  if (frame > dur) return null;
  const p = interpolate(frame, [0, dur], [0, 1], { extrapolateRight: "clamp" });
  const eased = 1 - Math.pow(1 - p, 3);
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        transform: `translateX(${eased * width}px) skewX(-8deg)`,
        backgroundColor: C.accent,
        opacity: 0.9,
      }}
    />
  );
};

/**
 * Slow push-in plus a hair of drift, running the whole scene. Frame-derived, so
 * it never loops or lands back where it started — the eye keeps reading motion
 * even while the copy stays put.
 */
const useCameraMove = () => {
  const frame = useCurrentFrame();
  return {
    scale: 1 + frame * 0.00028,
    x: Math.sin(frame * 0.0055) * 5,
    y: Math.cos(frame * 0.0041) * 3.5,
  };
};

/** Shared chrome: background, watermark, source credit, progress bar. */
export const Frame: React.FC<{
  children: React.ReactNode;
  source?: string;
  words?: { w: string; start: number; end: number }[];
  progress: number;
  /** Full-bleed layer painted behind the content — e.g. a 3D canvas. */
  bg?: React.ReactNode;
}> = ({ children, source, words, progress, bg }) => {
  const cam = useCameraMove();
  return (
  <div
    style={{
      width: "100%",
      height: "100%",
      backgroundColor: C.bg,
      fontFamily: FONT,
      color: C.text,
      position: "relative",
      overflow: "hidden",
    }}
  >
    <div
      style={{
        position: "absolute",
        inset: 0,
        background:
          `radial-gradient(1200px 700px at 50% 12%, ${C.bgAlt} 0%, ${C.bg} 70%)`,
      }}
    />
    {/* Never-still backdrop. Without it, a scene freezes the moment its
        entrance animation ends — which is what made the first cut feel dead. */}
    <LivingBackdrop variant={bg ? "soft" : "full"} />
    <WipeIn />
    {bg ? (
      <div style={{ position: "absolute", inset: 0 }}>{bg}</div>
    ) : null}
    <div
      style={{
        position: "absolute",
        top: 46,
        right: 64,
        fontSize: 22,
        color: C.muted,
        letterSpacing: 2,
      }}
    >
      <span style={{ color: C.accent }}>●</span> {BRAND}
    </div>

    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        // Bottom padding reserves the caption strip, so no scene's content can
        // collide with it. Caught by a still-frame review of the list scene.
        padding: "40px 160px 230px",
        textAlign: "center",
        transform: `scale(${cam.scale}) translate(${cam.x}px, ${cam.y}px)`,
      }}
    >
      {children}
    </div>

    <div
      style={{
        position: "absolute",
        bottom: 22,
        left: 64,
        fontSize: 16,
        color: "#4A4A50",
        lineHeight: 1.5,
      }}
    >
      {CREDITS.map((line) => (
        <div key={line}>{line}</div>
      ))}
    </div>

    {source ? (
      <div
        style={{
          position: "absolute",
          bottom: 92,
          left: 64,
          fontSize: 19,
          color: C.muted,
          letterSpacing: 2,
        }}
      >
        {source}
      </div>
    ) : null}

    {words ? <Captions words={words} /> : null}

    <div
      style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        height: 5,
        width: `${progress * 100}%`,
        backgroundColor: C.accent,
      }}
    />
  </div>
  );
};
