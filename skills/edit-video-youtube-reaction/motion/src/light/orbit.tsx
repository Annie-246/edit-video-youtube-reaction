import React from "react";
import { AbsoluteFill, Img, interpolate, useCurrentFrame } from "remotion";

/**
 * Pictures circling the presenter on a tilted 3D ring, rendered as a transparent layer.
 * The same ring is drawn twice: layer "back" keeps the cards on the far half (they pass behind the
 * presenter's cut-out), layer "front" the near half (they pass in front). render.py stacks
 * background → back → presenter cut-out → front. Cards swap layers at the ring's sides, where the
 * presenter is not, so the hand-over never shows.
 */
export type OrbitProps = {
  width: number; height: number; fps: number; total: number;
  layer: "back" | "front" | "all";
  images: string[];
  cx?: number; cy?: number;       // ring centre (fraction of the frame)
  rx?: number; ry?: number;       // ring radii (fraction of width / height); ry tilts the ring
  speed?: number;                 // degrees per second
  card?: number;                  // card width (px at 1920)
};

const cl = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const W = 1920, H = 1080;

export const Orbit: React.FC<OrbitProps> = ({ width, fps, total, layer, images, cx = 0.5, cy = 0.7, rx = 0.4, ry = 0.17, speed = 22, card = 380 }) => {
  const f = useCurrentFrame();
  const end = Math.round(total * fps);
  const grow = interpolate(f, [0, 18], [0, 1], { ...cl, easing: (t) => 1 - Math.pow(1 - t, 3) });
  const fade = interpolate(f, [end - 10, end], [1, 0], cl);
  const n = Math.max(1, images.length);
  const cards = images.map((src, i) => {
    const th = ((i * 360) / n + (speed * f) / fps + 90 * (1 - grow)) * (Math.PI / 180);
    const z = Math.cos(th);                                  // 1 = nearest the camera
    return { src, i, z, x: W * cx + W * rx * grow * Math.sin(th), y: H * cy + H * ry * z, turn: Math.sin(th) * 50 };
  });
  const shown = cards
    .filter((c) => layer === "all" || (layer === "back" ? c.z < 0 : c.z >= 0))
    .sort((a, b) => a.z - b.z);
  return (
    <AbsoluteFill style={{ backgroundColor: "transparent" }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: W, height: H, transform: `scale(${width / W})`, transformOrigin: "0 0", perspective: 1600 }}>
        {shown.map((c) => {
          const s = interpolate(c.z, [-1, 1], [0.62, 1.12]);
          const h = card * 0.62;
          return (
            <div key={c.i} style={{ position: "absolute", left: c.x - card / 2, top: c.y - h / 2, width: card, height: h, borderRadius: 18, overflow: "hidden",
              transform: `scale(${s * grow}) rotateY(${c.turn}deg)`, opacity: fade * interpolate(c.z, [-1, 1], [0.78, 1]),
              filter: c.z < 0 ? `blur(${(-c.z) * 2.2}px) brightness(${1 - (-c.z) * 0.18})` : "none",
              boxShadow: "0 0 0 4px #fff, 0 22px 50px rgba(0,0,0,0.35)" }}>
              <Img src={c.src} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export const ORBIT_DEFAULTS: OrbitProps = { width: 1920, height: 1080, fps: 30, total: 4, layer: "all", images: [] };
export const orbitMeta = (p: OrbitProps) => ({ durationInFrames: Math.max(1, Math.ceil(p.total * p.fps)), fps: p.fps, width: p.width, height: p.height });
