import React from "react";
import { AbsoluteFill, Easing, Sequence, interpolate, useCurrentFrame } from "remotion";
import { ART_W, CueCtx, DarkCtx, MorphCtx, themeVars } from "./kit";

// Whole-video theme: dark (charcoal + warm clay glow, like the reference). A scene can still pin
// the light look with "dark": false. With THEME = "light" the old per-template tones come back.
const THEME: "dark" | "light" = "dark";
const DARK_DEFAULT = new Set<string>();
// Studio / picture scenes come in a light and a dark look. Each has a natural tone (statement and
// showcase scenes dark, explaining scenes light); a scene's own "dark" wins. Only guard: a third
// unpinned scene in a row on the same tone flips, so the screen never sits on one look too long.
const TONED = new Set(["swipe", "strips", "float", "bigtype", "pills", "orbit", "typebar", "ui3d", "wall"]);
const DARK_NATURAL = new Set(["float", "orbit", "bigtype", "typebar"]);
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

// Scene to scene inside one list: a morph, not a cut. The two scenes overlap for MORPH frames; the
// leaving one gets MorphCtx "out" (its title floats up and shrinks, its cards draw in and fade), the
// arriving one "in" (its label lands out of the old title, its cards swell up) while it fades in over
// the same background, so the board stays put and one scene turns into the next.
const MORPH = 22;
const XFADE = MORPH;
const smooth = Easing.bezier(0.45, 0, 0.2, 1);
const cl = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const SceneWrap: React.FC<{ children: React.ReactNode; first: boolean; last: boolean; body: number }> = ({ children, first, last, body }) => {
  const f = useCurrentFrame();
  const pin = first ? 1 : interpolate(f, [0, MORPH], [0, 1], { ...cl, easing: smooth });
  const pout = last ? 0 : interpolate(f, [body, body + MORPH], [0, 1], { ...cl, easing: smooth });
  const o = first ? interpolate(f, [0, 8], [0, 1], cl) : interpolate(pin, [0, 0.55], [0, 1], cl);
  const s = first ? interpolate(f, [0, 12], [1.025, 1], cl) : 1;
  const morph = !first && pin < 1 ? { dir: "in" as const, p: pin } : pout > 0 ? { dir: "out" as const, p: pout } : { dir: null, p: 1 };
  return (
    <AbsoluteFill style={{ opacity: o, transform: s !== 1 ? `scale(${s})` : undefined }}>
      <MorphCtx.Provider value={morph}>{children}</MorphCtx.Provider>
    </AbsoluteFill>
  );
};

/** Plays the scene list back to back; each scene morphs into the next. */
export const Main: React.FC<MainProps> = ({ width, height, fps, scenes }) => {
  // The artboard keeps its width and takes the frame's aspect, so taller frames get more room.
  const k = width / ART_W;
  const artH = Math.round(ART_W * height / width);
  const tones: boolean[] = [];
  scenes.forEach((sc, i) => {
    if (THEME === "dark") { tones.push(sc.props.dark ?? true); return; }   // one look for the whole video
    let d: boolean = sc.props.dark ?? (TONED.has(sc.template) ? DARK_NATURAL.has(sc.template) : DARK_DEFAULT.has(sc.template));
    if (sc.props.dark === undefined && TONED.has(sc.template) && i >= 2 && tones[i - 1] === d && tones[i - 2] === d) d = !d;
    tones.push(d);
  });
  return (
    <AbsoluteFill style={{ background: THEME === "dark" ? "#1A1918" : "#fff", overflow: "hidden" }}>
      {scenes.map((sc, i) => {
        const T = CUSTOM[sc.template] || TEMPLATES[sc.template] || TEMPLATES.title;
        const from = Math.round(sc.start * fps);
        const body = Math.max(1, Math.round(sc.duration * fps));
        const last = i === scenes.length - 1;
        const dur = body + (last ? 0 : XFADE);
        return (
          <React.Fragment key={i}>
          <Sequence from={from} durationInFrames={dur} layout="none">
            <SceneWrap first={i === 0} last={last} body={body}>
              <CueCtx.Provider value={Array.isArray(sc.props.cue) ? sc.props.cue : undefined}>
              <DarkCtx.Provider value={tones[i]}>
                <div style={{ position: "absolute", left: 0, top: 0, width: ART_W, height: artH, transform: `scale(${k})`, transformOrigin: "0 0", color: "var(--ink)",
                  ...themeVars(tones[i]) }}>
                  <T {...sc.props} dur={dur} seed={i * 1.7} />
                </div>
              </DarkCtx.Provider>
              </CueCtx.Provider>
            </SceneWrap>
          </Sequence>
          </React.Fragment>
        );
      })}
    </AbsoluteFill>
  );
};

export const mainMeta = (p: MainProps) => {
  const total = p.scenes.reduce((m, s) => Math.max(m, s.start + s.duration), 0);
  return { durationInFrames: Math.max(1, Math.ceil(total * p.fps)), fps: p.fps, width: p.width, height: p.height };
};
