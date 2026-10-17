import React from "react";
import { Composition } from "remotion";
import { MAIN_DEFAULTS, Main, mainMeta, type MainProps } from "./light/Main";

/**
 * One composition for everything: the big main frame beside the presenter (any size, e.g.
 * 1440x920) and the full-frame cards (1920x1080). reactforge writes the props at render time
 * — size, fps and the scene list — so graphics always match the layout they sit in.
 */
export const RemotionRoot: React.FC = () => (
  <Composition
    id="Main"
    component={Main as unknown as React.FC<Record<string, unknown>>}
    defaultProps={MAIN_DEFAULTS as unknown as Record<string, unknown>}
    durationInFrames={120}
    fps={30}
    width={1440}
    height={920}
    calculateMetadata={({ props }) => mainMeta(props as unknown as MainProps)}
  />
);
