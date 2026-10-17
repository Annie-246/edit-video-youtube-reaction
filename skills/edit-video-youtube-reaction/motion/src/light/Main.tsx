import React from "react";
import { AbsoluteFill, Sequence, interpolate, useCurrentFrame } from "remotion";
import { ART_W, DarkCtx, themeVars } from "./kit";

// Light by default; a scene opts into the dark look with "dark": true.
const DARK_DEFAULT = new Set<string>();
import { TEMPLATES } from "./templates";
import { CUSTOM } from "../custom";

export type LightScene = { start: number; duration: number; template: string; props: Record<string, any> };
export type MainProps = { width: number; height: number; fps: number; scenes: LightScene[] };

export const MAIN_DEFAULTS: MainProps = {
  width: 1440,
  height: 920,
  fps: 30,
  scenes: [{ start: 0, duration: 4, template: "title", props: { kicker: "Thử", title: "Một câu *thật hay* để xem thử" } }],
};

const XFADE = 8;

const SceneWrap: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, XFADE], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const s = interpolate(f, [0, XFADE + 4], [1.025, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ opacity: o, transform: `scale(${s})` }}>{children}</AbsoluteFill>;
};

/** Plays the scene list back to back; each scene fades over the previous one. */
export const Main: React.FC<MainProps> = ({ width, height, fps, scenes }) => {
  // The artboard keeps its width and takes the frame's aspect, so taller frames get more room.
  const k = width / ART_W;
  const artH = Math.round(ART_W * height / width);
  return (
    <AbsoluteFill style={{ background: "#fff", overflow: "hidden" }}>
      {scenes.map((sc, i) => {
        const T = CUSTOM[sc.template] || TEMPLATES[sc.template] || TEMPLATES.title;
        const from = Math.round(sc.start * fps);
        const dur = Math.max(1, Math.round(sc.duration * fps)) + (i < scenes.length - 1 ? XFADE : 0);
        return (
          <Sequence key={i} from={from} durationInFrames={dur} layout="none">
            <SceneWrap>
              <DarkCtx.Provider value={sc.props.dark ?? DARK_DEFAULT.has(sc.template)}>
                <div style={{ position: "absolute", left: 0, top: 0, width: ART_W, height: artH, transform: `scale(${k})`, transformOrigin: "0 0", color: "var(--ink)",
                  ...themeVars(sc.props.dark ?? DARK_DEFAULT.has(sc.template)) }}>
                  <T {...sc.props} dur={dur} seed={i * 1.7} />
                </div>
              </DarkCtx.Provider>
            </SceneWrap>
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

export const mainMeta = (p: MainProps) => {
  const total = p.scenes.reduce((m, s) => Math.max(m, s.start + s.duration), 0);
  return { durationInFrames: Math.max(1, Math.ceil(total * p.fps)), fps: p.fps, width: p.width, height: p.height };
};
