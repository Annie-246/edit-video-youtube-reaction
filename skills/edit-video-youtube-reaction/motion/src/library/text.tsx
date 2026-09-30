import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { C } from "../theme";
import type { SceneRenderProps } from "../types";
import { Frame, Hi, Kicker, Rise } from "../ui";

/** Ease-out count-up, frame-driven so renders stay deterministic. */
export const useCountUp = (to: number, durationInFrames = 34, delay = 4) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - delay, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return to * (1 - Math.pow(1 - p, 3));
};

export const vn = (n: number, decimals = 0) =>
  n.toLocaleString("vi-VN", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

export const BigNumber: React.FC<SceneRenderProps<"bignumber">> = ({
  value,
  decimals = 0,
  unit,
  headline,
  sub,
  kicker,
  words,
  progress,
  source,
}) => {
  const n = useCountUp(value, 40);
  return (
    <Frame source={source} words={words} progress={progress}>
      {kicker ? <Kicker>{kicker}</Kicker> : null}
      <div style={{ height: 40 }} />
      <div
        style={{
          fontSize: 260,
          fontWeight: 700,
          lineHeight: 1,
          color: C.accent,
          letterSpacing: -6,
        }}
      >
        {vn(n, decimals)}
        {unit ? <span style={{ fontSize: 120 }}> {unit}</span> : null}
      </div>
      <div style={{ height: 28 }} />
      <Rise delay={26}>
        <div style={{ fontSize: 46, fontWeight: 700 }}>
          <Hi text={headline} />
        </div>
      </Rise>
      {sub ? (
        <>
          <div style={{ height: 18 }} />
          <Rise delay={38}>
            <div style={{ fontSize: 34, color: C.muted }}>{sub}</div>
          </Rise>
        </>
      ) : null}
    </Frame>
  );
};

export const Statement: React.FC<SceneRenderProps<"statement">> = ({
  text,
  after,
  words,
  progress,
  source,
}) => {
  const frame = useCurrentFrame();
  const strike = interpolate(frame, [30, 52], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  // The strike-through is a single horizontal bar, so the claim has to stay on
  // one line — on two lines it reads as an underline, not a negation. Scale the
  // type down as the sentence grows instead of letting it wrap.
  const fontSize = text.length <= 28 ? 82 : text.length <= 46 ? 60 : 46;
  return (
    <Frame source={source} words={words} progress={progress}>
      <Rise>
        <div style={{ position: "relative", display: "inline-block" }}>
          <div
            style={{
              fontSize,
              fontWeight: 700,
              lineHeight: 1.15,
              whiteSpace: "nowrap",
            }}
          >
            {text}
          </div>
          <div
            style={{
              position: "absolute",
              top: "52%",
              left: 0,
              height: 7,
              width: `${strike * 100}%`,
              backgroundColor: C.accent,
            }}
          />
        </div>
      </Rise>
      {after ? (
        <>
          <div style={{ height: 34 }} />
          <Rise delay={48}>
            <div style={{ fontSize: 44, color: C.muted }}>{after}</div>
          </Rise>
        </>
      ) : null}
    </Frame>
  );
};

export const TwoLine: React.FC<SceneRenderProps<"twoline">> = ({
  first,
  second,
  words,
  progress,
  source,
}) => (
  <Frame source={source} words={words} progress={progress}>
    <Rise>
      <div style={{ fontSize: 96, fontWeight: 700, lineHeight: 1.2 }}>
        {first}
      </div>
    </Rise>
    <div style={{ height: 12 }} />
    <Rise delay={26}>
      <div
        style={{
          fontSize: 96,
          fontWeight: 700,
          lineHeight: 1.2,
          color: C.accent,
        }}
      >
        {second}
      </div>
    </Rise>
  </Frame>
);

export const Closing: React.FC<SceneRenderProps<"closing">> = ({
  lead,
  quote,
  payoff,
  words,
  progress,
  source,
}) => (
  <Frame source={source} words={words} progress={progress}>
    <Rise>
      <div style={{ fontSize: 46, color: C.muted, fontWeight: 700 }}>{lead}</div>
    </Rise>
    <div style={{ height: 14 }} />
    <Rise delay={18}>
      <div style={{ fontSize: 62, fontWeight: 700 }}>
        <Hi text={quote} />
      </div>
    </Rise>
    <div style={{ height: 46 }} />
    <Rise delay={60}>
      <div style={{ fontSize: 72, fontWeight: 700, color: C.accent }}>
        {payoff}
      </div>
    </Rise>
  </Frame>
);
