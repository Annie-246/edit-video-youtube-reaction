"""Full-frame cards rendered by the Remotion `Card` composition.

Three kinds, one composition — they differ only in tone:
  FULL:  a question the video is about to answer      → style "question"
  BEAT:  a punchline or a feeling, emoji allowed      → style "beat"
  BREAK: a chapter title over a beat of silence       → style "chapter"

Static PNGs (graphics.py) stay as the fallback for when node/Remotion is not available;
render.py prefers the video when it exists.
"""
from __future__ import annotations

from pathlib import Path

from .common import load_project, read_json, write_json
from .graphics import layout_for
from .panel import parse_full, render_panel


def _props(cfg: dict, L: dict, secs: float, style: str, src: dict) -> dict:
    return {"width": L["w"], "height": L["h"], "fps": cfg["output"]["fps"], "secs": round(secs, 3),
            "accent": cfg["style"]["accent"], "bg": L["bg"], "style": style,
            "kicker": src.get("kicker", ""), "title": src.get("title", ""),
            "sub": src.get("sub", ""), "emoji": src.get("emoji", "")}


def main(project: Path, only: str | None = None, force: bool = False) -> None:
    cfg = load_project(project)
    L = layout_for(cfg["output"]["width"])
    plan = read_json(project / "work" / "plan.json")
    out_dir = project / "work" / "cards"; out_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for it in plan:
        if only and it["id"] != only:
            continue
        jobs: list[tuple[Path, dict]] = []
        if it["type"] == "break":
            secs = float(cfg["output"].get("break_secs", 2.6))
            jobs.append((out_dir / f"{it['id']}.mp4",
                         _props(cfg, L, secs, "chapter",
                                {"kicker": f"PHẦN {it['section']}" if it.get("section") else "",
                                 "title": it["title"]})))
        elif it["type"] == "talk" and it.get("full"):
            timings = read_json(project / "work" / "full" / f"{it['id']}.json") \
                if (project / "work" / "full" / f"{it['id']}.json").exists() else []
            for k, line in enumerate(it["full"]):
                f = parse_full(line)
                if not f:
                    continue
                pr = f["props"]
                secs = float(timings[k]["secs"]) if k < len(timings) else float(pr.get("secs", 3.6))
                style = pr.get("style", "question")
                jobs.append((out_dir / f"{it['id']}_full{k}.mp4", _props(cfg, L, secs, style, pr)))
        for out, props in jobs:
            cache = out.with_suffix(".json")
            if out.exists() and not force and cache.exists() and read_json(cache) == props:
                print(f"{out.stem}: thẻ có sẵn"); continue
            render_panel(props, out, composition="Card")
            print(f"{out.stem}: {props['style']} {props['secs']}s — {props['title'][:52]}")
            n += 1
    print(f"→ {n} thẻ dựng mới trong {out_dir}")
