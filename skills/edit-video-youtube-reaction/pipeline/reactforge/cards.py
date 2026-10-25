"""Full-frame cards, rendered by the Remotion `Main` composition at 1920x1080 with one scene.

  FULL:  any light template as a full-frame card        → {"tpl": "...", ...}
  BEAT:  one line that should land                       → dark `title`
  BREAK: back to the chapter list, push in on the new one → `chapters` (focus mode)
  OUTRO: closing sting                                   → `outro`
Statement cards (title / quote / equation) go dark by default; tool openers stay light.

Static PNGs (graphics.py) stay as the fallback for when node/Remotion is not available;
render.py prefers the video when it exists.
"""
from __future__ import annotations

from pathlib import Path

from .common import load_project, read_json, run, write_json
from .graphics import layout_for
from .panel import parse_full, render_panel


BREAK_SECS = {"outro": 3.2}


def break_secs(cfg: dict, it: dict) -> float:
    return float(it.get("secs") or BREAK_SECS.get(it.get("tpl", ""), cfg["output"].get("break_secs", 2.6)))


def _side_at(line: str) -> float | None:
    """`at` second of a screen-recording SIDE line (broll / screen / rec), if any."""
    import json, re
    m = re.match(r'^(?:@"[^"]*"\s+)?(broll|screen|rec)\s+(\{.*\})\s*$', line.strip())
    if not m:
        return None
    try:
        at = json.loads(m.group(2)).get("at")
    except ValueError:
        return None
    return float(at) if at is not None else None


def chapter_items(project: Path, cfg: dict, plan: list[dict]) -> list[dict]:
    """One row per BREAK: its title, and a thumbnail cut from the first screen recording of that
    chapter (source/full.mp4 at the scene's `at`, webcam cropped off). No recording → an icon."""
    gfx = project / "work" / "gfx"; gfx.mkdir(parents=True, exist_ok=True)
    full = project / "source" / "full.mp4"
    crop = (cfg.get("source") or {}).get("screen_crop")
    items, cur = [], None
    for it in plan:
        if it["type"] == "break" and it.get("tpl", "chapter") == "chapter":
            cur = {"title": it["title"], "icon": "play"}
            items.append(cur)
        elif cur is not None and "src" not in cur and it["type"] == "talk":
            at = next((a for a in (_side_at(l) for l in it.get("side") or []) if a is not None), None)
            if at is None or not full.exists():
                continue
            jpg = gfx / f"chapter_{len(items):02d}.jpg"
            if not jpg.exists():
                vf = (f"crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]}," if crop else "") + "scale=480:-2"
                run(["ffmpeg", "-v", "error", "-y", "-ss", f"{at:.2f}", "-i", str(full), "-frames:v", "1", "-vf", vf, "-q:v", "3", str(jpg)])
            if jpg.exists():
                cur["src"] = str(jpg); cur.pop("icon", None)
    return items


def _props(cfg: dict, L: dict, secs: float, style: str, src: dict) -> dict:
    extra = {k: v for k, v in src.items() if k not in ("secs", "style")}
    return {**extra, "width": L["w"], "height": L["h"], "fps": cfg["output"]["fps"], "secs": round(secs, 3),
            "accent": cfg["style"]["accent"], "bg": L["bg"], "style": style,
            "kicker": src.get("kicker", ""), "title": src.get("title", ""),
            "sub": src.get("sub", ""), "emoji": src.get("emoji", "")}


def main(project: Path, only: str | None = None, force: bool = False) -> None:
    cfg = load_project(project)
    L = layout_for(cfg["output"]["width"])
    plan = read_json(project / "work" / "plan.json")
    out_dir = project / "work" / "cards"; out_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    chapters = chapter_items(project, cfg, plan)
    breaks = [b["id"] for b in plan if b["type"] == "break" and b.get("tpl", "chapter") == "chapter"]
    for it in plan:
        if only and it["id"] != only:
            continue
        jobs: list[tuple[Path, dict]] = []
        if it["type"] == "break":
            # showreel stings: chapter (BREAK:), outro (OUTRO:)
            tpl = it.get("tpl", "chapter")
            pr = {"title": it["title"], "sub": it.get("sub", ""), "dark": True}
            if tpl == "chapter":
                # back to the chapter list: push in on this chapter, earlier ones ticked
                tpl = "chapters"
                pr = {"items": chapters, "mode": "focus", "focus": breaks.index(it["id"])}
            jobs.append((out_dir / f"{it['id']}.mp4",
                         {"width": L["w"], "height": L["h"], "fps": cfg["output"]["fps"],
                          "scenes": [{"start": 0, "duration": round(break_secs(cfg, it), 3), "template": tpl, "props": pr}]}))
        elif it["type"] == "talk" and it.get("full"):
            timings = read_json(project / "work" / "full" / f"{it['id']}.json") \
                if (project / "work" / "full" / f"{it['id']}.json").exists() else []
            for k, line in enumerate(it["full"]):
                f = parse_full(line)
                if not f:
                    continue
                pr = f["props"]
                secs = float(timings[k]["secs"]) if k < len(timings) else float(pr.get("secs", 3.6))
                # White layout: full-frame cards use the same light templates as the main frame.
                tpl = pr.get("tpl", "title")
                sp = {kk: v for kk, v in pr.items() if kk not in ("secs", "tpl")}
                if tpl == "chapters" and not sp.get("items"):
                    sp["items"] = chapters   # the opening list: rows come from the BREAK titles
                jobs.append((out_dir / f"{it['id']}_full{k}.mp4",
                             {"width": L["w"], "height": L["h"], "fps": cfg["output"]["fps"],
                              "scenes": [{"start": 0, "duration": round(secs, 3), "template": tpl, "props": sp}]}))
        for out, props in jobs:
            cache = out.with_suffix(".json")
            if out.exists() and not force and cache.exists() and read_json(cache) == props:
                print(f"{out.stem}: thẻ có sẵn"); continue
            comp = "Main"
            render_panel(props, out, composition=comp, base=project)
            print(f"{out.stem}: {comp} {props.get('secs', props.get('scenes', [{}])[0].get('duration'))}s")
            n += 1
    print(f"→ {n} thẻ dựng mới trong {out_dir}")
