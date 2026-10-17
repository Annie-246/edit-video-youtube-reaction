import type React from "react";

/**
 * Custom templates Claude writes for a specific script (diagrams, text motion, anything the
 * built-in light set doesn't cover).
 *
 * This folder lives in the plugin data dir and rf.py never overwrites it on plugin updates.
 * Register each component by name; it then works in both places:
 *   SIDE: @"câu" my_tpl {...}            → main frame scene
 *   FULL: @"câu" {"tpl":"my_tpl", ...}   → full-frame card
 * The component gets the script props plus `dur` (frames) and `seed`, and draws on the
 * 1180-wide artboard using ../light/kit (Stage, Card, Words, GradText, Pill, Cursor…).
 * A custom name overrides a built-in template of the same name.
 */
export const CUSTOM: Record<string, React.FC<any>> = {};
