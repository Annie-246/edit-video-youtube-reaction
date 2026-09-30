import type React from "react";

/**
 * Custom templates Claude writes for a specific script (text motion, icon motion,
 * diagrams… anything the built-in set doesn't cover).
 *
 * This folder lives in the plugin data dir and rf.py never overwrites it on plugin
 * updates. Register each component by name; the name then works everywhere:
 *   GFX:  @"câu" my_tpl {...}      → Panel (900x478), gets {...props, accent}
 *   SIDE: @"câu" my_tpl {...}      → Side  (900x1016), gets {...props, accent}
 *   FULL: @"câu" {"style":"my_tpl", ...} → Card (1920x1080), gets all card props
 * A custom name overrides a built-in template of the same name.
 */
export const CUSTOM: Record<string, React.FC<any>> = {};
