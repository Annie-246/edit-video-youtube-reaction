"""Source video: the whole file (b-roll needs any moment of it), clip ranges, captions, and
the b-roll screen file the Remotion main frame plays (work/public/screen.mp4)."""
from __future__ import annotations
from pathlib import Path
from .common import load_project, read_json, write_json, run, ffprobe_duration

YTDLP = ["yt-dlp", "--js-runtimes", "node"]


def main(project: Path) -> None:
    cfg = load_project(project); src = cfg["source"]
    plan = read_json(project / "work" / "plan.json")
    clips = [i for i in plan if i["type"] == "clip"]
    d = project / "source"; d.mkdir(exist_ok=True)
    meta_p = d / "clips.json"
    meta = read_json(meta_p) if meta_p.exists() else {}
    url, local = src.get("url"), src.get("local_file")
    q, pad = int(src.get("quality", 1080)), float(src.get("pad", 1.0))
    # captions + thumbnail (once)
    if url and not list(d.glob("captions*.vtt")):
        try:
            run(YTDLP + ["--skip-download", "--write-subs", "--write-auto-subs", "--sub-langs", "en-orig,en", "--sub-format", "vtt", "-o", str(d / "captions"), url])
        except RuntimeError as e:
            print("captions bỏ qua (sẽ dùng Whisper nghe clip):", str(e)[-120:])
        print("captions:", [p.name for p in d.glob("captions*.vtt")])
    if url and not (d / "thumb.jpg").exists():
        try:
            run(YTDLP + ["--skip-download", "--write-thumbnail", "--convert-thumbnails", "jpg", "-o", str(d / "thumb"), url])
        except RuntimeError as e:
            print("thumbnail bỏ qua:", str(e)[:120])
    # The whole source: b-roll scenes ("broll" template, "at": seconds) can point anywhere in it.
    if url and not local:
        full = d / "full.mp4"
        if not full.exists():
            run(YTDLP + ["-f", f"bv*[height<={q}][ext=mp4]+ba[ext=m4a]/bv*[height<={q}]+ba/b", "--merge-output-format", "mp4", "-o", str(full), url])
        local = "source/full.mp4"
    build_screen(project, src, local)
    for c in clips:
        out = d / f"{c['id']}.mp4"
        if out.exists() and c["id"] in meta:
            print(f"{c['id']}: có sẵn ({meta[c['id']]['file']}, offset {meta[c['id']]['offset']}s)"); continue
        s, e = max(0.0, c["start"] - pad), c["end"] + pad
        if local:
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.2f}", "-to", f"{e:.2f}", "-i", str(project / local), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "192k", str(out)])
        else:
            def hms(t): return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:06.3f}"
            run(YTDLP + ["-f", f"bv*[height<={q}][ext=mp4]+ba[ext=m4a]/b[height<={q}]/b", "--download-sections", f"*{hms(s)}-{hms(e)}", "--force-keyframes-at-cuts", "--merge-output-format", "mp4", "-o", str(out), url])
        meta[c["id"]] = {"file": out.name, "offset": round(c["start"] - s, 3), "start": c["start"], "end": c["end"]}
        write_json(meta_p, meta)
        print(f"{c['id']}: {out.name} ({ffprobe_duration(out):.1f}s, offset {meta[c['id']]['offset']}s)")
    write_json(meta_p, meta)


def build_screen(project: Path, src: dict, local: str | None) -> None:
    """work/public/screen.mp4: the source at 30 fps, cropped to `source.screen_crop`
    ([x, y, w, h] in source pixels) so a webcam box or burned lower-third stays out of b-roll.
    Remotion serves it from the project's own public dir, so projects never collide."""
    if not local or not (project / local).exists():
        return
    out = project / "work" / "public" / "screen.mp4"
    if out.exists():
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    crop = src.get("screen_crop")
    vf = (f"crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]}," if crop else "") + "scale=1440:-2:flags=lanczos,fps=30"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(project / local), "-an", "-vf", vf, "-c:v", "libx264",
         "-preset", "veryfast", "-crf", "20", "-g", "30", "-pix_fmt", "yuv420p", str(out)])
    print(f"b-roll screen → {out.relative_to(project)} (crop {crop or 'none'})")
