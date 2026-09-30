import React from "react";
import { Composition } from "remotion";
import "./fonts";
import { CARD_DEFAULTS, Card, type CardProps } from "./Card";
import { PANEL_DEFAULTS, Panel, type PanelProps } from "./Panel";
import { SIDE_DEFAULTS, Side, type SideProps } from "./Side";

/**
 * Three compositions, all driven entirely by a props file that reactforge writes at
 * render time — size, fps, length, accent colour and the scene list all come from the
 * host video, so these graphics always match the layout they sit in.
 *
 *   Panel — the animated block in the bottom-left corner (900x478)
 *   Side  — the tall half-screen animated composition beside the presenter (900x1016)
 *   Card  — a full-frame graphic that takes the whole screen for a few seconds (1920x1080)
 */
export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="Side"
      component={Side as React.FC<Record<string, unknown>>}
      defaultProps={SIDE_DEFAULTS as unknown as Record<string, unknown>}
      durationInFrames={150}
      fps={30}
      width={900}
      height={1016}
      calculateMetadata={({ props }) => {
        const p = props as unknown as SideProps;
        const total = p.scenes.reduce((m, s) => Math.max(m, s.start + s.duration), 0);
        return {
          durationInFrames: Math.max(1, Math.ceil(total * p.fps)),
          fps: p.fps,
          width: p.width,
          height: p.height,
        };
      }}
    />
    <Composition
      id="Panel"
      component={Panel as React.FC<Record<string, unknown>>}
      defaultProps={PANEL_DEFAULTS as unknown as Record<string, unknown>}
      durationInFrames={150}
      fps={30}
      width={900}
      height={478}
      calculateMetadata={({ props }) => {
        const p = props as unknown as PanelProps;
        const total = p.scenes.reduce((m, s) => Math.max(m, s.start + s.duration), 0);
        return {
          durationInFrames: Math.max(1, Math.ceil(total * p.fps)),
          fps: p.fps,
          width: p.width,
          height: p.height,
        };
      }}
    />
    <Composition
      id="Card"
      component={Card as React.FC<Record<string, unknown>>}
      defaultProps={CARD_DEFAULTS as unknown as Record<string, unknown>}
      durationInFrames={108}
      fps={30}
      width={1920}
      height={1080}
      calculateMetadata={({ props }) => {
        const p = props as unknown as CardProps;
        return {
          durationInFrames: Math.max(1, Math.ceil(p.secs * p.fps)),
          fps: p.fps,
          width: p.width,
          height: p.height,
        };
      }}
    />
  </>
);
