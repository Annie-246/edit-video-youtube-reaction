"""Build the moving left-hand panel for talk segments.

The left box used to hold ONE frozen frame for the whole talk, which reads as a stalled
video. This samples several stills from the stretch of the source the presenter is talking
about, then crossfades between them with a slow push-in, sized to the talk's own length.

Output goes to `screens/<talk id>.mp4`, which the renderer already knows how to place —
its presence also switches off the static still.

    python3 scripts/make_screens.py <project> [--only t03] [--per-shot 11]
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from reactforge.common import load_project, read_json, run  # noqa: E402
from reactforge.graphics import layout_for  # noqa: E402

FADE = 0.7        # crossfade between stills
ZOOM = 1.10       # push-in over one still
MIN_SHOTS, MAX_SHOTS = 3, 8
WIDEN = 0.25      # sample a little either side of the clip, for variety on short clips
MIN_SPAN = 120.0
STILL_SECS = 4.5   # how long one supplied still holds before the next  # a 45 s clip barely changes on screen; widen until there is something to see
# Match the look the static still had (CSS brightness .55 / saturate .8) so the box still
# sits behind the face instead of competing with it.
DIM = "lutyuv=y='val*0.58',eq=saturation=0.82"


def source_range(plan: list[dict], idx: int, dur_src: float) -> tuple[float, float] | None:
    """The stretch of source video this talk is talking about.

    Prefer the clip that sits right next to it — that is what the presenter is reacting to.
    Falling back to the nearest clip in either direction matters: the opening talk has no clip
    before it and a chapter card plus another talk after it, and an earlier version gave up
    there, leaving the single most-watched segment of the video with a frozen panel.
    """
    for step in (-1, 1):        # immediate neighbour, not crossing another talk
        j = idx + step
        while 0 <= j < len(plan):
            if plan[j]["type"] == "clip":
                return _pad(plan[j], dur_src)
            if plan[j]["type"] == "talk":
                break
            j += step
    clips = [(abs(j - idx), j) for j, it in enumerate(plan) if it["type"] == "clip"]
    return _pad(plan[min(clips)[1]], dur_src) if clips else None


def _pad(clip: dict, dur_src: float) -> tuple[float, float]:
    a, b = clip["start"], clip["end"]
    pad = max((b - a) * WIDEN, (MIN_SPAN - (b - a)) / 2)
    return max(0.0, a - pad), min(dur_src, b + pad)


def grab(src: Path, times: list[float], out_dir: Path, w: int, h: int, cover: dict | None) -> list[Path]:
    shots = []
    # the same burned-in caption strip the clips get painted over would otherwise ride along here
    cov = f"drawbox=x=0:y=ih*{cover['y']}:w=iw:h=ih*{cover['h']}:color=black@1:t=fill," if cover else ""
    for k, t in enumerate(times):
        p = out_dir / f"s{k:02d}.jpg"
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(src), "-frames:v", "1",
             "-vf", f"{cov}scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},{DIM}", "-q:v", "3", str(p)])
        if p.exists() and p.stat().st_size > 0:
            shots.append(p)
    return shots



def fit(src: Path, dest: Path, w: int, h: int) -> Path:
    """Letterbox a supplied image into the box on the panel's own background, then dim it."""
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-frames:v", "1",
         "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
                f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=0x0B0B10,{DIM}", "-q:v", "3", str(dest)])
    return dest


def parse_span(t: str) -> tuple[float, float] | None:
    """'1:52-2:18' (or en dash) -> seconds. Anything else is a hand-written note, not a cut."""
    m = re.match(r"^\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*[\u2013\u2014-]\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*$", t)
    if not m:
        return None
    def sec(x: str) -> float:
        parts = [float(v) for v in x.split(":")]
        return parts[0] * 60 + parts[1] if len(parts) == 2 else parts[0] * 3600 + parts[1] * 60 + parts[2]
    a, b = sec(m.group(1)), sec(m.group(2))
    return (a, b) if b > a else None


def _box_filter(w: int, h: int, crop_bottom: float) -> str:
    """Fill the left box, dropping the source's burned-in caption strip first."""
    pre = f"crop=iw:ih*{1 - crop_bottom:.4f}:0:0," if crop_bottom > 0 else ""
    return (f"{pre}scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h},setsar=1,{DIM}")


def cut_broll(src: Path, spans: list[tuple[float, float]], w: int, h: int, fps: int,
              crop_bottom: float, tmp: Path) -> list[Path]:
    out = []
    for k, (a, b) in enumerate(spans):
        q = tmp / f"b{k:02d}.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.2f}", "-t", f"{b - a:.2f}", "-i", str(src),
             "-an", "-vf", f"fps={fps},{_box_filter(w, h, crop_bottom)}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", str(q)])
        if q.exists() and q.stat().st_size > 0:
            out.append(q)
    return out


def still_clip(img: Path, secs: float, w: int, h: int, fps: int, out: Path) -> Path:
    """A supplied still (headline, photo) as a clip with a slow push-in, so it reads as motion."""
    frames = max(2, int(round(secs * fps)))
    run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", f"{secs:.2f}", "-i", str(img),
         "-vf", f"scale={w * 2}:{h * 2}:force_original_aspect_ratio=decrease,"
                f"pad={w * 2}:{h * 2}:(ow-iw)/2:(oh-ih)/2:color=0x0B0B10,"
                f"zoompan=z='min(zoom+{(ZOOM - 1) / frames:.6f},{ZOOM})':d={frames}"
                f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={w}x{h}:fps={fps},setsar=1,{DIM}",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", str(out)])
    return out


def chain(clips: list[Path], total: float, fps: int, tmp: Path, out: Path) -> None:
    """Lay the clips end to end, looping the run until it covers the talk, then cut to length."""
    lst = tmp / "concat.txt"
    lst.write_text("".join(f"file '{c}'\n" for c in clips), encoding="utf-8")
    joined = tmp / "joined.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c", "copy", str(joined)])
    dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                     str(joined)]).stdout)
    loops = max(0, int(total // max(dur, 0.1)))
    run(["ffmpeg", "-v", "error", "-y", "-stream_loop", str(loops), "-i", str(joined),
         "-t", f"{total:.3f}", "-vf", f"fps={fps}",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", str(out)])


def slideshow(shots: list[Path], total: float, fps: int, w: int, h: int, out: Path) -> None:
    """Crossfade the stills so the run lasts exactly `total` seconds."""
    n = len(shots)
    if n == 1:
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", f"{total:.3f}", "-i", str(shots[0]),
             "-vf", f"scale={w}:{h},fps={fps}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
             "-pix_fmt", "yuv420p", str(out)])
        return
    # K clips crossfaded pairwise run for K*seg - (K-1)*FADE; solve that for `total`
    seg = (total + (n - 1) * FADE) / n
    frames = max(2, int(round(seg * fps)))
    cmd, fc = ["ffmpeg", "-v", "error", "-y"], []
    for k, p in enumerate(shots):
        cmd += ["-loop", "1", "-t", f"{seg + 0.2:.3f}", "-i", str(p)]
        # alternate the push-in direction so a long run does not feel mechanical
        z = f"min(zoom+{(ZOOM - 1) / frames:.6f},{ZOOM})" if k % 2 == 0 else f"max({ZOOM}-{(ZOOM - 1) / frames:.6f}*on,1.0)"
        fc.append(f"[{k}:v]scale={w * 2}:{h * 2},zoompan=z='{z}':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                  f":s={w}x{h}:fps={fps},setsar=1[v{k}]")
    last = "[v0]"
    for k in range(1, n):
        off = k * (seg - FADE)
        tag = f"[x{k}]"
        fc.append(f"{last}[v{k}]xfade=transition=fade:duration={FADE}:offset={off:.3f}{tag}")
        last = tag
    cmd += ["-filter_complex", ";".join(fc), "-map", last, "-t", f"{total:.3f}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", str(out)]
    run(cmd)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project", type=Path)
    ap.add_argument("--only")
    ap.add_argument("--per-shot", type=float, default=11.0, help="giây mỗi ảnh")
    a = ap.parse_args()

    P = a.project.resolve()
    cfg = load_project(P)
    L = layout_for(cfg["output"]["width"])
    fps = cfg["output"]["fps"]
    box = L["left"]
    src = P / (cfg["source"].get("local_file") or "source/raw.mp4")
    dur_src = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)]).stdout)
    plan = read_json(P / "work" / "plan.json")
    align = {x["id"]: x for x in read_json(P / "work" / "align.json")}
    out_dir = P / "screens"; out_dir.mkdir(exist_ok=True)

    for i, it in enumerate(plan):
        if it["type"] != "talk" or (a.only and it["id"] != a.only):
            continue
        al = align.get(it["id"])
        if not al or al.get("start") is None:
            continue
        keep = al.get("keep") or [[al["start"], al["end"]]]
        total = round(sum(e - s for s, e in keep), 3) + 0.5
        rng = source_range(plan, i, dur_src)
        if not rng:
            print(f"{it['id']}: không tìm được đoạn nguồn tương ứng, bỏ qua"); continue
        lo, hi = rng
        n = max(MIN_SHOTS, min(MAX_SHOTS, int(round(total / a.per_shot))))
        times = [lo + (hi - lo) * (k + 0.5) / n for k in range(n)]
        tmp = Path(tempfile.mkdtemp(prefix=f"scr_{it['id']}_"))
        try:
            # hand-picked stills for this talk (a portrait, a product screenshot, a drawn graphic)
            # lead the run; frames from the source fill the rest
            custom = sorted(q for q in (P / "assets" / it["id"]).glob("*")
                            if q.suffix.lower() in (".jpg", ".jpeg", ".png"))
            # [MÀN HÌNH: 1:52-2:18] lines name stretches of the source to run as live b-roll.
            # A frozen still under a voice-over reads as a stalled video; moving footage does not.
            spans = [sp for sp in (parse_span(x) for x in it.get("screens", [])) if sp]
            # Stills supplied for a talk are the subject of that talk. Topping them up with frames
            # from the source — which is what the still-sampling path does — drops a Chinese film
            # set into a passage about a blender ad, so hold the supplied run and loop it instead.
            if spans or custom:
                crop_b = float(cfg["source"].get("crop_bottom", 0.0))
                hold = max(STILL_SECS, min(9.0, total / max(1, len(custom)))) if custom else STILL_SECS
                clips = [still_clip(q, hold, box["w"], box["h"], fps, tmp / f"c{k:02d}.mp4")
                         for k, q in enumerate(custom)]
                clips += cut_broll(src, spans, box["w"], box["h"], fps, crop_b, tmp)
                if clips:
                    dest = out_dir / f"{it['id']}.mp4"
                    chain(clips, total, fps, tmp, dest)
                    print(f"{it['id']}: {len(custom)} ảnh (mỗi ảnh {hold:.1f}s) + {len(spans)} đoạn b-roll → {dest.name} ({total:.1f}s)", flush=True)
                    continue
            n = max(len(custom), n)
            times = [lo + (hi - lo) * (k + 0.5) / n for k in range(max(0, n - len(custom)))]
            shots = [fit(q, tmp / f"a{k:02d}.jpg", box["w"], box["h"]) for k, q in enumerate(custom)]
            shots += grab(src, times, tmp, box["w"], box["h"], cfg["source"].get("cover_bottom"))
            if not shots:
                print(f"{it['id']}: không lấy được ảnh nào, bỏ qua"); continue
            dest = out_dir / f"{it['id']}.mp4"
            slideshow(shots, total, fps, box["w"], box["h"], dest)
            print(f"{it['id']}: {len(shots)} ảnh từ {lo:.0f}-{hi:.0f}s nguồn → {dest.name} ({total:.1f}s)", flush=True)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
