export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;

export const C = {
  bg: "#0E0E10",
  bgAlt: "#141417",
  accent: "#FF6B1A",
  accentDim: "#B04A12",
  text: "#F5F5F0",
  muted: "#8A8A85",
  faint: "#3A3A3E",
  good: "#3DD68C",
} as const;

export const FONT = "BeVietnamPro, -apple-system, sans-serif";

/** Watermark shown on every frame. Change this one line to rebrand the output. */
export const BRAND = ""; // watermark của kênh bạn, Panel/Card không dùng

/**
 * Small print, bottom-left. Naming the tools and licences is both honest and a
 * mark of care — the reference video does the same.
 */
// Tools only — never data sources. This line shows on EVERY video, so naming a
// specific dataset here credits it on videos that never used it. Per-scene
// `source` is where a figure names its origin.
export const CREDITS: string[] = []; // Panel/Card không dùng

/** Source credit shown on every scene that puts a number on screen. */
