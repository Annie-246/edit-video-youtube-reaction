import { BOLD_B64, REGULAR_B64 } from "./fontData";

/**
 * Fonts are embedded as base64 and injected as CSS. Deliberately NO
 * delayRender() here.
 *
 * History, so nobody reintroduces it:
 *  - `loadFont()` from @remotion/fonts + delayRender worked for 40-55s videos
 *    but killed an 8-minute render three times, at frames 2376, 8695 and 8578.
 *  - Raising the timeout only moved the failure later.
 *  - A `setTimeout` backstop never fires: Remotion controls timers mid-render.
 *  - Embedding the bytes removed the network hop, and the promise STILL stalled
 *    in tabs spawned part-way through the render.
 *
 * With a data: URI there is nothing to fetch, so letting the browser own font
 * loading is safe. `font-display: block` keeps it from painting a fallback face
 * while the bytes are parsed.
 */
const css = `
@font-face {
  font-family: "BeVietnamPro";
  font-style: normal;
  font-weight: 400;
  font-display: block;
  src: url(data:font/ttf;base64,${REGULAR_B64}) format("truetype");
}
@font-face {
  font-family: "BeVietnamPro";
  font-style: normal;
  font-weight: 700;
  font-display: block;
  src: url(data:font/ttf;base64,${BOLD_B64}) format("truetype");
}
`;

if (typeof document !== "undefined") {
  const style = document.createElement("style");
  style.setAttribute("data-fonts", "be-vietnam-pro");
  style.textContent = css;
  document.head.appendChild(style);
}
