import React from "react";
import { interpolate, random, useCurrentFrame, useVideoConfig } from "remotion";
import { C } from "../theme";

/**
 * Continuous-motion layer.
 *
 * The reason the first cut felt static: every element animated in once and then
 * froze for the rest of an 11-second scene. CSS keyframes push you toward that
 * — you fire an animation and it ends. Remotion doesn't have that limit: every
 * property is a function of the current frame, so motion can run for the whole
 * scene without ever looping visibly.
 *
 * Everything here is frame-derived and deterministic, and `random(seed)` keeps
 * particle layouts identical across renders.
 */

/** Slow drift, never repeating within a scene. Use on any element. */
export const useDrift = (seed: number, amount = 6, speed = 0.008) => {
  const frame = useCurrentFrame();
  return {
    x: Math.sin(frame * speed + seed * 1.7) * amount,
    y: Math.cos(frame * speed * 0.83 + seed * 2.3) * amount * 0.7,
  };
};

/** Subtle breathing scale — keeps hero type alive without drawing attention. */
export const useBreathe = (speed = 0.012, amount = 0.012) => {
  const frame = useCurrentFrame();
  return 1 + Math.sin(frame * speed) * amount;
};

/** Drifting dust. Depth is faked by size + opacity + parallax speed. */
export const Particles: React.FC<{ count?: number; seed?: number }> = ({
  count = 46,
  seed = 1,
}) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>
      {new Array(count).fill(0).map((_, i) => {
        const r1 = random(`p${seed}-${i}-x`);
        const r2 = random(`p${seed}-${i}-y`);
        const r3 = random(`p${seed}-${i}-d`);
        const depth = 0.35 + r3 * 0.65;
        const size = 1.5 + depth * 3.5;
        // Wrap with modulo so particles stream forever instead of running out.
        const x = (r1 * width + frame * depth * 0.35) % (width + 60) - 30;
        const y =
          (r2 * height - frame * depth * 0.22 + height * 3) % (height + 60) - 30;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: size,
              height: size,
              borderRadius: "50%",
              backgroundColor: i % 7 === 0 ? C.accent : "#FFFFFF",
              opacity: 0.05 + depth * 0.16,
            }}
          />
        );
      })}
    </div>
  );
};

/** Perspective floor grid that slides toward the viewer, forever. */
export const GridFloor: React.FC<{ opacity?: number }> = ({
  opacity = 0.16,
}) => {
  const frame = useCurrentFrame();
  const shift = (frame * 0.55) % 90;
  return (
    <div
      style={{
        position: "absolute",
        left: "-25%",
        right: "-25%",
        bottom: "-14%",
        height: "62%",
        opacity,
        transform: "perspective(680px) rotateX(66deg)",
        transformOrigin: "bottom center",
        backgroundImage: `linear-gradient(${C.accent} 1px, transparent 1px),
                          linear-gradient(90deg, ${C.accent} 1px, transparent 1px)`,
        backgroundSize: "90px 90px",
        backgroundPosition: `0px ${shift}px`,
        maskImage:
          "linear-gradient(to top, rgba(0,0,0,0.85) 0%, transparent 78%)",
        WebkitMaskImage:
          "linear-gradient(to top, rgba(0,0,0,0.85) 0%, transparent 78%)",
      }}
    />
  );
};

/** Two accent glows orbiting slowly behind the content. */
export const Aurora: React.FC<{ intensity?: number }> = ({
  intensity = 1,
}) => {
  const frame = useCurrentFrame();
  const a = frame * 0.0042;
  const blobs = [
    {
      x: 50 + Math.sin(a) * 26,
      y: 26 + Math.cos(a * 0.8) * 16,
      c: C.accent,
      s: 760,
      o: 0.12 * intensity,
    },
    {
      x: 46 + Math.cos(a * 0.63 + 2) * 30,
      y: 62 + Math.sin(a * 0.9 + 1) * 18,
      c: "#4A3AFF",
      s: 620,
      o: 0.09 * intensity,
    },
  ];
  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>
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
            background: `radial-gradient(circle, ${b.c} 0%, transparent 68%)`,
            opacity: b.o,
            filter: "blur(38px)",
          }}
        />
      ))}
    </div>
  );
};

/** Scan sweep — one slow pass of light across the frame per scene. */
export const Sweep: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const x = interpolate(frame, [0, fps * 9], [-width * 0.4, width * 1.4], {
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        bottom: 0,
        left: x,
        width: width * 0.28,
        background: `linear-gradient(90deg, transparent, ${C.accent}0F, transparent)`,
        pointerEvents: "none",
      }}
    />
  );
};

/** The full living backdrop used behind every scene. */
export const LivingBackdrop: React.FC<{ variant?: "full" | "soft" }> = ({
  variant = "full",
}) => (
  <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>
    <Aurora intensity={variant === "soft" ? 0.55 : 1} />
    <GridFloor opacity={variant === "soft" ? 0.08 : 0.16} />
    <Particles count={variant === "soft" ? 26 : 46} />
    <Sweep />
  </div>
);
