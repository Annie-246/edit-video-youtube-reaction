/**
 * Scene contract shared by the content files and the template library.
 *
 * A video is a JSON file listing scenes. Each scene names a template from the
 * library and supplies its props. Templates never hard-code copy — that is what
 * makes the library reusable across videos instead of being one video's markup.
 */

export type Word = { w: string; start: number; end: number };

/** Props accepted by each template, keyed by template id. */
export type TemplateProps = {
  /** One dominant figure. Use for a single striking number. */
  bignumber: {
    value: number;
    decimals?: number;
    unit?: string;
    headline: string;
    sub?: string;
    kicker?: string;
  };
  /** A claim that gets struck through — used to set up a reversal. */
  statement: {
    text: string;
    after?: string;
  };
  /** Two contrasting lines, the second in the accent colour. */
  twoline: {
    first: string;
    second: string;
  };
  /** Ranked list of short items. */
  list: {
    kicker?: string;
    items: string[];
  };
  /** Two percentages side by side. */
  statpair: {
    kicker?: string;
    headline: string;
    leftLabel: string;
    leftValue: number;
    rightLabel: string;
    rightValue: number;
    decimals?: number;
    suffix?: string;
  };
  /** Horizontal bars comparing 2-4 values on a common scale. */
  bars: {
    kicker?: string;
    headline: string;
    scaleMax: number;
    rows: { label: string; value: number; highlight?: boolean }[];
    suffix?: string;
  };
  /** Two vertical bars whose heights encode magnitude. */
  barpair: {
    kicker?: string;
    headline: string;
    leftLabel: string;
    leftValue: string;
    rightLabel: string;
    rightValue: string;
    /** Ratio of right bar to left bar, 0-1. */
    ratio: number;
    footnote?: string;
  };
  /**
   * 3D grid where a highlighted subset, and then a subset OF that subset, is
   * pulled out. Use when the point is containment — "X of those are also Y" —
   * which flat bars cannot express.
   */
  grid3d: {
    kicker?: string;
    kickerLate?: string;
    /** Highlight every Nth cube. */
    hitEvery: number;
    headline: string;
    sub?: string;
    lateHeadline: string;
    lateSub?: string;
    /** Seconds into the scene when the single cube pulls out. */
    pullAt: number;
  };
  /** Closing statement plus payoff line. */
  closing: {
    lead: string;
    quote: string;
    payoff: string;
  };
  /** Large title with no figure. The workhorse for connective beats. */
  headline: {
    kicker?: string;
    text: string;
    sub?: string;
    /** "center" (default) or "left" for a change of rhythm in long videos. */
    align?: "center" | "left";
  };
  /** A rule or line worth nailing down. Vertical accent bar on the left. */
  quote: {
    kicker?: string;
    text: string;
    attribution?: string;
  };
  /** Ordered steps joined by arrows — shows sequence, which a list cannot. */
  flow: {
    kicker?: string;
    headline?: string;
    steps: string[];
    /** Index of the step to emphasise, if any. */
    focus?: number;
  };
  /** Multi-row measurements. Use when 3+ figures share one frame. */
  table: {
    kicker?: string;
    headline?: string;
    rows: { label: string; value: string; note?: string }[];
  };
  /**
   * A solid of 100 cubes — one per percent — that breaks apart into groups
   * sized by real data. Shows composition physically: the pieces visibly came
   * from one block, which neither a donut nor bars can express.
   */
  blocks3d: {
    kicker?: string;
    headline?: string;
    segments: { label: string; value: number; highlight?: boolean }[];
    /** Seconds into the scene when the solid breaks apart. */
    explodeAt: number;
    unitNote?: string;
  };
  /**
   * A modelled figure in a glowing portal. Built from primitives rather than a
   * generated image, so it stays consistent and can actually move.
   */
  figure: {
    kicker?: string;
    headline: string;
    sub?: string;
    pose: "watching" | "typing" | "thinking" | "presenting" | "offering" | "climbing";
    /** Portal glow. Defaults to the accent; warm it for emotional beats. */
    portalColour?: string;
    note?: string;
  };
  /** A real captured image — screenshot, photo, or the project's own output. */
  shot: {
    kicker?: string;
    headline?: string;
    /** Path under public/, e.g. "shots/contact-sheet.png". */
    src: string;
    caption?: string;
    badge?: string;
    /** Attribution for photos that need it. */
    credit?: string;
  };
  /** Real talking-head clip beside the copy. Muted — the VO track carries sound. */
  talkinghead: {
    kicker?: string;
    headline: string;
    sub?: string;
    /** Path under public/, e.g. "heads/scene_00.mp4". */
    head: string;
  };
  /** Terminal window replaying output that really ran. */
  terminal: {
    kicker?: string;
    headline?: string;
    title: string;
    lines: { text: string; kind?: "cmd" | "out" | "ok" | "hi" }[];
  };
  /** Parts of one whole. Bars compare separate values; this splits a total. */
  donut: {
    kicker?: string;
    headline?: string;
    segments: { label: string; value: number; highlight?: boolean }[];
    centerLabel?: string;
  };
};

export type TemplateId = keyof TemplateProps;

export type Scene<T extends TemplateId = TemplateId> = {
  /** Which library template renders this beat. */
  template: T;
  /** What the narrator says. Drives this scene's exact duration. */
  narration: string;
  /**
   * Why this scene exists — must say something the narration cannot.
   * Not rendered; it exists to be reviewed and to justify keeping the scene.
   */
  reason: string;
  /** Source credit burned into the frame. Required whenever a figure is shown. */
  source?: string;
  props: TemplateProps[T];
};

export type VideoContent = {
  id: string;
  title: string;
  scenes: Scene[];
};

/** Written by scripts/tts.py after measuring each scene's real audio. */
export type Timings = {
  total: number;
  scenes: { id: string; start: number; duration: number; words: Word[] }[];
};

export type SceneRenderProps<T extends TemplateId> = TemplateProps[T] & {
  words: Word[];
  progress: number;
  source?: string;
};
