"""Animated bottom-left graphic for talk segments, rendered by the Remotion `Panel` composition.

Script lines inside a talk block:
    GFX: card {"kicker":"MỞ MÀN","title":"Alex Hormozi","sub":"…"}
    GFX: @"16 doanh nghiệp" bignumber {"value":250,"unit":"triệu đô/năm","headline":"…"}
The optional @"phrase" makes the scene start when the presenter reaches that phrase (found in
the word timings); the first scene without a phrase starts at 0. Scenes run until the next one.
Templates: card · bignumber · list · quote · compare · twoline (see remotion-explainer/src/Panel.tsx).
"""
from __future__ import annotations
import base64, json, os, re, subprocess
from pathlib import Path
from .align import normalize
from .captions import timed_words_for
from .common import load_project, read_json, write_json
from .graphics import layout_for

GFX_RE = re.compile(r'^(?:@"(?P<at>[^"]+)"\s+)?(?P<tpl>[a-z0-9_]+)\s*(?P<props>\{.*\})?\s*$', re.S)
MIN_SCENE = 1.5
def _remotion_dir() -> Path:
    """Where the Panel/Card compositions live.

    Checked in order so the shared package works unpacked anywhere: an explicit
    REMOTION_DIR, the `motion/` folder shipped beside this package, then the author's
    own explainer project.
    """
    env = os.environ.get("REMOTION_DIR")
    for c in (Path(env) if env else None,
              Path(__file__).resolve().parents[2] / "motion",
              Path.home() / "remotion-explainer"):
        if c and (c / "package.json").exists():
            return c
    return Path(env) if env else Path.home() / "remotion-explainer"


REMOTION_DIR = _remotion_dir()


def parse_gfx(line: str) -> dict | None:
    m = GFX_RE.match(line.strip())
    if not m:
        return None
    props = json.loads(m.group("props")) if m.group("props") else {}
    return {"at": m.group("at"), "template": m.group("tpl"), "props": props}



FULL_RE = re.compile(r'^(?:@"(?P<at>[^"]+)"\s+)?(?P<props>\{.*\})\s*$', re.S)


def parse_full(line: str) -> dict | None:
    """FULL: @"câu neo" {"secs":4,"kicker":"…","title":"…","sub":"…"}"""
    m = FULL_RE.match(line.strip())
    if not m:
        return None
    return {"at": m.group("at"), "props": json.loads(m.group("props"))}


def find_phrase(phrase: str, ws: list[dict]) -> float | None:
    toks = [normalize(x) for x in phrase.split() if normalize(x)]
    wn = [normalize(w["w"]) for w in ws]
    n = len(toks)
    for i in range(0, len(wn) - n + 1):
        if wn[i:i + n] == toks:
            return ws[i]["s"]
    # tolerate one differing token in longer phrases
    if n >= 3:
        for i in range(0, len(wn) - n + 1):
            if sum(1 for a, b in zip(wn[i:i + n], toks) if a == b) >= n - 1:
                return ws[i]["s"]
    return None


def build_scenes(gfx_lines: list[str], ws: list[dict], total: float) -> tuple[list[dict], list[str]]:
    scenes, notes = [], []
    parsed = [g for g in (parse_gfx(l) for l in gfx_lines) if g]
    starts: list[float | None] = []
    for g in parsed:
        if g["at"] is None:
            starts.append(0.0 if not scenes and not starts else None)
        else:
            t = find_phrase(g["at"], ws)
            if t is None:
                notes.append(f'không thấy câu "{g["at"]}" trong lời — chia đều thời gian')
            starts.append(t)
    # fill runs of unknown starts evenly between their known neighbours
    i = 0
    while i < len(starts):
        if starts[i] is not None:
            i += 1; continue
        j = i
        while j < len(starts) and starts[j] is None:
            j += 1
        prev = starts[i - 1] if i > 0 else 0.0
        nxt = starts[j] if j < len(starts) else total
        step = (nxt - prev) / (j - i + 1)
        for k in range(i, j):
            starts[k] = prev + step * (k - i + 1)
        i = j
    # enforce order + minimum length
    if starts:
        starts[0] = 0.0
    cur = 0.0
    for i, st in enumerate(starts):
        st = max(st, cur if i == 0 else cur + MIN_SCENE)
        starts[i] = min(st, max(0.0, total - MIN_SCENE)); cur = starts[i]
    if starts:
        starts[0] = 0.0
    for i, g in enumerate(parsed):
        end = starts[i + 1] if i + 1 < len(parsed) else max(total + 5.0, starts[i] + MIN_SCENE)
        scenes.append({"start": round(starts[i], 3), "duration": round(max(MIN_SCENE, end - starts[i]), 3),
                       "template": g["template"], "props": g["props"]})
    return scenes, notes


MAX_SCENE, SHOW_FOR = 11.0, 7.0
NO_SPLIT = {"recap", "broll"}


def split_long(scenes: list[dict], total: float) -> list[dict]:
    """The 10-second rule: a graphic that would sit longer than MAX_SCENE keeps the screen for
    SHOW_FOR seconds, then hands over to running b-roll. The filler comes from the source moment
    this talk showed most recently (same topic), or the next one if none was shown yet."""
    brolls = [(i, float(s["props"]["at"])) for i, s in enumerate(scenes) if s["template"] == "broll" and "at" in s["props"]]
    if not brolls:
        return scenes
    starts: list[tuple[float, str, dict]] = []
    used: dict[float, int] = {}
    for i, s in enumerate(scenes):
        end = scenes[i + 1]["start"] if i + 1 < len(scenes) else total
        d = end - s["start"]
        starts.append((s["start"], s["template"], s["props"]))
        if d <= MAX_SCENE or s["template"] == "recap":
            continue
        is_b = s["template"] == "broll"
        prev = [a for j, a in brolls if j < i]
        nxt = [a for j, a in brolls if j > i]
        if is_b:
            cands = nxt[:1] + prev[-1:] or [float(s["props"]["at"])]
        else:
            cands = prev[-1:] + nxt[:1]
        first = min(9.0, d / 2) if is_b else SHOW_FOR
        t, n = s["start"] + first, 0
        while end - t > 3.0:
            base = cands[n % len(cands)]
            used[base] = used.get(base, 0) + 1
            starts.append((t, "broll", {"at": round(base + 5.0 * used[base], 2)}))
            t += 9.0 if end - t > 12.0 else (end - t)
            n += 1
    out = []
    for i, (st, tpl, pr) in enumerate(starts):
        nxt_t = starts[i + 1][0] if i + 1 < len(starts) else max(total + 5.0, st + MIN_SCENE)
        out.append({"start": round(st, 3), "duration": round(nxt_t - st, 3), "template": tpl, "props": pr})
    return out


IMG_EXT = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif"}


def _inline_images(v, base: Path | None):
    """Remotion renders in a browser that cannot read local paths: turn image files into data URIs."""
    if isinstance(v, dict):
        return {k: _inline_images(x, base) for k, x in v.items()}
    if isinstance(v, list):
        return [_inline_images(x, base) for x in v]
    if isinstance(v, str) and Path(v).suffix.lower() in IMG_EXT and not v.startswith(("http:", "https:", "data:")):
        p = Path(v)
        if not p.is_absolute() and base is not None:
            p = base / p
        if p.is_file():
            return f"data:{IMG_EXT[p.suffix.lower()]};base64," + base64.b64encode(p.read_bytes()).decode()
        print(f"   ⚠ không thấy ảnh {v}")
    return v


def render_panel(props: dict, out: Path, composition: str = "Main", base: Path | None = None) -> None:
    write_json(out.with_suffix(".json"), props)  # cache key, compared on the next run
    props_p = out.with_suffix(".props.json")
    write_json(props_p, _inline_images(props, base))
    cmd = ["npx", "remotion", "render", composition, str(out), f"--props={props_p}", "--log=error"]
    # b-roll scenes play work/public/screen.mp4 of THIS project
    if base is not None and (base / "work" / "public").is_dir():
        cmd.append(f"--public-dir={base / 'work' / 'public'}")
    r = subprocess.run(cmd, cwd=str(REMOTION_DIR), capture_output=True, text=True, shell=(os.name == "nt"))
    if r.returncode != 0:
        raise RuntimeError(f"remotion failed: {r.stderr[-1500:]}")


def main(project: Path, only: str | None = None, force: bool = False) -> None:
    cfg = load_project(project); L = layout_for(cfg["output"]["width"]); P = L["panel"]; S = L["main"]
    plan = read_json(project / "work" / "plan.json")
    words = read_json(project / "work" / "words.json")
    align = {a["id"]: a for a in read_json(project / "work" / "align.json")}
    out_dir = project / "work" / "panel"; out_dir.mkdir(parents=True, exist_ok=True)
    side_dir = project / "work" / "side"; side_dir.mkdir(parents=True, exist_ok=True)
    full_dir = project / "work" / "full"
    for it in plan:
        if it["type"] != "talk" or not (it.get("full") or it.get("side")):
            continue
        if only and it["id"] != only:
            continue
        al = align.get(it["id"])
        if not al or al.get("start") is None:
            continue
        ws = timed_words_for(it, words, al)
        total = al.get("kept") or (al["end"] - al["start"])
        # Full-frame cards: anchor each to the phrase it belongs with, so the layout drops away
        # exactly as the question is asked rather than at an arbitrary second.
        if it.get("full"):
            full_dir.mkdir(parents=True, exist_ok=True)
            cards = []
            for k, line in enumerate(it["full"]):
                f = parse_full(line)
                if not f:
                    print(f"   ⚠ {it['id']}: dòng FULL không đọc được: {line[:60]}"); continue
                secs = float(f["props"].get("secs", 4.0))
                t = find_phrase(f["at"], ws) if f["at"] else 0.0
                if t is None:
                    print(f'   ⚠ {it["id"]}: không thấy câu "{f["at"]}" — đặt thẻ ở đầu đoạn'); t = 0.0
                cards.append({"png": f"{it['id']}_full{k}.png", "start": round(max(0.0, t), 3),
                              "secs": round(min(secs, max(1.0, total - t)), 3)})
            write_json(full_dir / f"{it['id']}.json", cards)
            print(f"{it['id']}: {len(cards)} thẻ toàn màn hình — " + " · ".join(f"{c['start']:.0f}s ({c['secs']:.1f}s)" for c in cards))
        if it.get("side"):
            scenes, notes = build_scenes(it["side"], ws, total)
            scenes = split_long(scenes, total)
            # BUBBLE / MOTION fill the whole screen with these scenes; the white layout has its frame
            # (BUBBLE keeps the content clear of the presenter bubble on the right)
            W, H = {"motion": (L["w"], L["h"]), "bubble": (L["bubble_area"], L["h"])}.get(it.get("mode"), (S["w"], S["h"]))
            props = {"width": W, "height": H, "fps": cfg["output"]["fps"], "scenes": scenes}
            out = side_dir / f"{it['id']}.mp4"
            if out.exists() and not force and out.with_suffix(".json").exists() and read_json(out.with_suffix(".json")) == props:
                print(f"{it['id']}: side graphic có sẵn")
            else:
                render_panel(props, out, composition="Main", base=project)
                print(f"{it['id']}: {len(scenes)} cảnh khung chính → side/{out.name}  " + " · ".join(f"{s['start']:.0f}s {s['template']}" for s in scenes))
                for n in notes:
                    print("   ⚠", n)
