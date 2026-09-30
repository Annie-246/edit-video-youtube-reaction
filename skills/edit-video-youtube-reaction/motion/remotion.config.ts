import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
// "angle" is what Remotion recommends when WebGL/Three.js scenes are added.
// Harmless for the current 2D scenes; keeps the config ready for 3D.
Config.setChromiumOpenGlRenderer("angle");
// Long renders spawn fresh tabs part-way through, and each one reloads the
// bundled fonts. The 28s default timed out at frame 2376 of an 8-minute video.
Config.setDelayRenderTimeoutInMilliseconds(120000);
