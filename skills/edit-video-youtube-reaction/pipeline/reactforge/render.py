"""Compose every plan item with ffmpeg, then concatenate."""
from __future__ import annotations
import subprocess
from pathlib import Path
from .common import load_project, read_json, run, ffprobe_duration, pick_encoder, escape_ffmpeg_path, FONT_DIR
from .graphics import layout_for


def _enc(cfg) -> list[str]:
    return pick_encoder(cfg["output"]["encoder"])


def keep_intervals(al: dict) -> list[list[float]]:
    return al.get("keep") or [[al["start"], al["end"]]]


def render_talk(project: Path, cfg: dict, L: dict, item: dict, al: dict, out: Path) -> None:
    fps = cfg["output"]["fps"]; g = project / "work" / "gfx"
    rec = project / "work" / "recording.mp4"
    keep = keep_intervals(al)
    t0 = keep[0][0]; t1 = keep[-1][1]
    # Snap every cut to the frame grid. Video can only cut on a frame; audio cuts anywhere, so an
    # unsnapped interval leaves the two ~1 frame apart, and the error accumulates over the joins and
    # then over the concatenated segments — that is the half-second drift heard mid-video.
    def q(t: float) -> float:
        return round(round((t - t0) * fps) / fps, 6)
    keep = [[q(s), q(e)] for s, e in keep]
    # Fix the segment length as a whole number of frames and give the audio exactly that length, so
    # `-frames:v` and `atrim` agree to the sample. `-t` cannot do this: it rounds the two differently.
    nfr = max(1, int(round(sum(e - s for s, e in keep) * fps)))
    dur = round(nfr / fps, 6)
    head, left = L["head"], L["left"]
    ratio = head["w"] / head["h"]; cx = float(cfg["recording"].get("cx", 0.5)); cy = float(cfg["recording"].get("cy", 0.5))
    screen = project / "screens" / f"{item['id']}.mp4"
    panel = project / "work" / "panel" / f"{item['id']}.mp4"
    side = project / "work" / "side" / f"{item['id']}.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0 + 0.5:.3f}", "-i", str(rec),
           "-loop", "1", "-i", str(g / f"{item['id']}_fg.png"), "-loop", "1", "-i", str(g / "mask_head.png")]
    fc = [f"color=c={L['bg']}:s={L['w']}x{L['h']}:r={fps}:d={dur + 1:.3f}[bg]"]
    # stumble removal: keep only the good takes, joined with straight cuts landing in silence
    if len(keep) == 1:
        fc.append("[0:v]null[tv]"); fc.append("[0:a]anull[ta]")
    else:
        parts = []
        for k, (s, e) in enumerate(keep):
            fc.append(f"[0:v]trim=start={s:.6f}:end={e:.6f},setpts=PTS-STARTPTS[v{k}]")
            fc.append(f"[0:a]atrim=start={s:.6f}:end={e:.6f},asetpts=PTS-STARTPTS[a{k}]")
            parts.append(f"[v{k}][a{k}]")
        fc.append(f"{''.join(parts)}concat=n={len(keep)}:v=1:a=1[tv][ta]")
    fc += [f"[tv]fps={fps},crop=w='min(iw,ih*{ratio:.4f})':h='min(ih,iw/{ratio:.4f})':x='{cx}*iw-min(iw,ih*{ratio:.4f})/2':y='{cy}*ih-min(ih,iw/{ratio:.4f})/2',scale={head['w']}:{head['h']},setsar=1[hv]",
           "[2:v]format=gray[hm]", "[hv][hm]alphamerge[ha]", f"[bg][ha]overlay={head['x']}:{head['y']}:shortest=1[a]"]
    last = "[a]"; n_in = 3
    if side.exists():
        S = L.get("side", {"x": 32, "y": 32, "w": 900, "h": 1016})
        cmd += ["-i", str(side), "-loop", "1", "-i", str(g / "mask_side.png")]
        fc += [f"[{n_in}:v]fps={fps},scale={S['w']}:{S['h']},setsar=1[sv0]", f"[{n_in + 1}:v]format=gray[sm0]", "[sv0][sm0]alphamerge[sa0]",
               f"{last}[sa0]overlay={S['x']}:{S['y']}:eof_action=repeat[p]"]
        last = "[p]"; n_in += 2
    else:
        if screen.exists():
            cmd += ["-i", str(screen), "-loop", "1", "-i", str(g / "mask_left.png")]
            fc += [f"[{n_in}:v]fps={fps},scale={left['w']}:{left['h']}:force_original_aspect_ratio=increase,scale='max(iw,{left['w']})':'max(ih,{left['h']})',crop={left['w']}:{left['h']},setsar=1[sv]",
                   f"[{n_in + 1}:v]format=gray[sm]", "[sv][sm]alphamerge[sa]", f"{last}[sa]overlay={left['x']}:{left['y']}:eof_action=pass[b]"]
            last = "[b]"; n_in += 2
        if panel.exists():
            P = L["panel"]
            cmd += ["-i", str(panel), "-loop", "1", "-i", str(g / "mask_panel.png")]
            fc += [f"[{n_in}:v]fps={fps},scale={P['w']}:{P['h']},setsar=1[pv0]", f"[{n_in + 1}:v]format=gray[pm0]", "[pv0][pm0]alphamerge[pa0]",
                   f"{last}[pa0]overlay={P['x']}:{P['y']}:eof_action=repeat[p]"]
            last = "[p]"; n_in += 2
    cap = project / "work" / "captions" / f"{item['id']}.ass"
    cap_f = f",subtitles='{escape_ffmpeg_path(cap)}':fontsdir='{escape_ffmpeg_path(FONT_DIR)}'" if cap.exists() and cap.stat().st_size > 0 else ""
    vtag = "[vc]"
    fc.append(f"{last}[1:v]overlay=0:0:shortest=1{cap_f}{vtag}")
    # Full-frame cards take the whole screen for a few seconds so a question can land on its own.
    fp = project / "work" / "full" / f"{item['id']}.json"
    for k, c in enumerate(read_json(fp) if fp.exists() else []):
        mp4 = project / "work" / "cards" / f"{item['id']}_full{k}.mp4"
        png = g / c["png"]
        if mp4.exists():
            cmd += ["-i", str(mp4)]
        elif png.exists():
            cmd += ["-loop", "1", "-t", f"{c['secs']:.3f}", "-i", str(png)]
        else:
            continue
        fade_out = max(0.0, c["secs"] - 0.3)
        fc.append(f"[{n_in}:v]fps={fps},format=rgba,fade=in:st=0:d=0.3:alpha=1,"
                  f"fade=out:st={fade_out:.3f}:d=0.3:alpha=1,setpts=PTS-STARTPTS+{c['start']:.3f}/TB[fc{k}]")
        fc.append(f"{vtag}[fc{k}]overlay=0:0:eof_action=pass[vf{k}]")
        vtag = f"[vf{k}]"; n_in += 1
    fc += [f"{vtag}format=yuv420p[v]", f"[ta]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,aformat=channel_layouts=stereo,asetpts=N/SR/TB,apad,atrim=end={dur:.6f},asetpts=PTS-STARTPTS[a]"]
    # asetpts=N/SR/TB before the atrim is load-bearing: loudnorm pushes the stream's PTS forward by
    # ~2 frames, so atrim=end=<dur> — which measures absolute PTS — silently ate that much off the
    # tail of every segment (~0.5 s summed over a 28-segment video). Rebuilding PTS from the sample
    # count makes the trim length-based. apad=whole_dur alone is NOT a substitute: it never ends
    # the stream, so `-frames:v` stops the mux wherever it happens to be, losing seconds of audio.
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-frames:v", str(nfr), "-r", str(fps)] + _enc(cfg) + ["-c:a", "pcm_s16le", str(out)]
    run(cmd)


def render_clip(project: Path, cfg: dict, L: dict, item: dict, meta: dict, pip_src: Path, pip_is_video: bool, out: Path) -> None:
    fps = cfg["output"]["fps"]; g = project / "work" / "gfx"
    src = project / "source" / meta["file"]; off = float(meta.get("offset", 0.0))
    nfr = max(1, int(round((item["end"] - item["start"]) * fps)))
    dur = round(nfr / fps, 6)
    C, P = L["clip"], L["pip"]
    ass = project / "work" / "subs" / f"{item['id']}.ass"
    sub_f = f",subtitles='{escape_ffmpeg_path(ass)}':fontsdir='{escape_ffmpeg_path(FONT_DIR)}'" if ass.exists() and ass.stat().st_size > 0 else ""
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{off:.3f}", "-t", f"{dur:.3f}", "-i", str(src),
           "-loop", "1", "-i", str(g / f"{item['id']}_fg.png"), "-loop", "1", "-i", str(g / "mask_clip.png")]
    if pip_is_video:
        cmd += ["-stream_loop", "-1", "-i", str(pip_src)]
    else:
        cmd += ["-loop", "1", "-i", str(pip_src)]
    cmd += ["-loop", "1", "-i", str(g / "mask_pip.png")]
    # Some re-uploads burn their own captions into the picture. Painting a band over that strip
    # before scaling turns three stacked layers of text into one, and our subtitle lands on it.
    cov = (load_project(project).get("source") or {}).get("cover_bottom")
    cover = f",drawbox=x=0:y=ih*{cov['y']}:w=iw:h=ih*{cov['h']}:color={L['bg']}@1:t=fill" if cov else ""
    fc = [f"color=c={L['bg']}:s={L['w']}x{L['h']}:r={fps}:d={dur + 1:.3f}[bg]",
          f"[0:v]fps={fps}{cover},scale={C['w']}:{C['h']}:force_original_aspect_ratio=decrease,pad={C['w']}:{C['h']}:(ow-iw)/2:(oh-ih)/2,setsar=1{sub_f}[cv]",
          "[2:v]format=gray[cm]", "[cv][cm]alphamerge[ca]", f"[bg][ca]overlay={C['x']}:{C['y']}:shortest=1[a]",
          f"[3:v]fps={fps},scale={P['w']}:{P['h']}:force_original_aspect_ratio=increase,scale='max(iw,{P['w']})':'max(ih,{P['h']})',crop={P['w']}:{P['h']},setsar=1[pv]",
          "[4:v]format=gray[pm]", "[pv][pm]alphamerge[pa]", f"[a][pa]overlay={P['x']}:{P['y']}:shortest=1[b]",
          "[b][1:v]overlay=0:0:shortest=1[c]"]
    last = "[c]"
    note = g / f"{item['id']}_note.png"
    if note.exists():
        cmd += ["-loop", "1", "-i", str(note)]
        fc += [f"[c][5:v]overlay=0:0:shortest=1:enable='gte(t,{max(0.0, dur-8):.2f})'[d]"]; last = "[d]"
    fc += [f"{last}format=yuv420p[v]", f"[0:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,aformat=channel_layouts=stereo,asetpts=N/SR/TB,apad,atrim=end={dur:.6f},asetpts=PTS-STARTPTS[a]"]
    # asetpts=N/SR/TB before the atrim is load-bearing: loudnorm pushes the stream's PTS forward by
    # ~2 frames, so atrim=end=<dur> — which measures absolute PTS — silently ate that much off the
    # tail of every segment (~0.5 s summed over a 28-segment video). Rebuilding PTS from the sample
    # count makes the trim length-based. apad=whole_dur alone is NOT a substitute: it never ends
    # the stream, so `-frames:v` stops the mux wherever it happens to be, losing seconds of audio.
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-frames:v", str(nfr), "-r", str(fps)] + _enc(cfg) + ["-c:a", "pcm_s16le", str(out)]
    run(cmd)



def render_break(project: Path, cfg: dict, L: dict, item: dict, out: Path) -> None:
    """A silent full-frame card between sections: names what is coming and rests the ear."""
    fps = cfg["output"]["fps"]
    secs = float(cfg["output"].get("break_secs", 2.6))
    nfr = max(1, int(round(secs * fps))); dur = round(nfr / fps, 6)
    mp4 = project / "work" / "cards" / f"{item['id']}.mp4"
    png = project / "work" / "gfx" / f"{item['id']}_break.png"
    src = ["-i", str(mp4)] if mp4.exists() else ["-loop", "1", "-t", f"{dur + 0.5:.3f}", "-i", str(png)]
    cmd = ["ffmpeg", "-v", "error", "-y", *src,
           "-f", "lavfi", "-t", f"{dur + 0.5:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
    fc = [f"[0:v]fps={fps},scale={L['w']}:{L['h']},setsar=1,fade=in:st=0:d=0.3,"
          f"fade=out:st={max(0.0, dur - 0.3):.3f}:d=0.3,format=yuv420p[v]",
          f"[1:a]aformat=channel_layouts=stereo,asetpts=N/SR/TB,apad,atrim=end={dur:.6f},asetpts=PTS-STARTPTS[a]"]
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-frames:v", str(nfr), "-r", str(fps)] \
        + _enc(cfg) + ["-c:a", "pcm_s16le", str(out)]
    run(cmd)


def main(project: Path, only: str | None = None, concat: bool = True) -> None:
    if not only:
        from .doctor import preflight
        preflight(project)
    cfg = load_project(project); L = layout_for(cfg["output"]["width"])
    plan = read_json(project / "work" / "plan.json")
    align = {a["id"]: a for a in read_json(project / "work" / "align.json")}
    meta = read_json(project / "source" / "clips.json")
    work = project / "work"; seg = work / "seg"; seg.mkdir(parents=True, exist_ok=True)
    # PiP source: reaction loop if given, else a still from the recording at the first talk's start
    pip_file = cfg["recording"].get("pip_file")
    if pip_file and (project / pip_file).exists():
        pip_src, pip_video = project / pip_file, True
    else:
        pip_src, pip_video = work / "gfx" / "pip_still.jpg", False
        if not pip_src.exists():
            first = next((align[i["id"]] for i in plan if i["type"] == "talk" and align.get(i["id"], {}).get("start") is not None), None)
            t0 = (first["start"] + 1.0) if first else 1.0
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.2f}", "-i", str(work / "recording.mp4"), "-frames:v", "1", "-q:v", "3", str(pip_src)])
    order = []
    for it in plan:
        if it["type"] == "score": continue
        out = seg / f"{it['id']}.mov"
        order.append(out)
        if only and it["id"] != only:
            continue
        if out.exists() and out.stat().st_size > 1000:
            print(f"{it['id']}: có sẵn ({out.name})")
            continue
        if it["type"] == "break":
            print(f"{it['id']}: đang render break...")
            render_break(project, cfg, L, it, out)
            print(f"{it['id']} → {out.name} ({ffprobe_duration(out):.1f}s) — {it['title']}")
            continue
        if it["type"] == "talk":
            al = align.get(it["id"])
            if not al or al["start"] is None:
                print(f"⚠ {it['id']}: chưa khớp lời, bỏ qua"); order.pop(); continue
            print(f"{it['id']}: đang render talk...")
            render_talk(project, cfg, L, it, al, out)
            print(f"{it['id']} → {out.name} ({ffprobe_duration(out):.1f}s)")
        else:
            m = meta.get(it["id"])
            if not m or not (project / "source" / m["file"]).exists():
                print(f"⚠ {it['id']}: chưa tải được clip gốc, bỏ qua"); order.pop(); continue
            print(f"{it['id']}: đang render clip...")
            render_clip(project, cfg, L, it, m, pip_src, pip_video, out)
            print(f"{it['id']} → {out.name} ({ffprobe_duration(out):.1f}s)")
    if only:
        if concat:
            concat_only(project)
        return
    if not concat:
        return
    _concat(project, order)


def _concat(project: Path, order: list[Path]) -> None:
    work = project / "work"
    lst = work / "concat.txt"
    lst.write_text("".join(f"file '{str(p.resolve()).replace('\\', '/')}'\n" for p in order if p.exists()), encoding="utf-8")
    final = project / "out" / "final.mp4"; final.parent.mkdir(exist_ok=True)
    for attempt in (1, 2):
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)])
        # A muxing hiccup here writes a file that plays back as garbage; catch it now, not on the timeline.
        bad = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration", "-of", "csv=p=0", str(final)],
                             capture_output=True, text=True).stderr.strip()
        if not bad:
            break
        print(f"⚠ file nối bị lỗi ({bad.splitlines()[0][:70]}) → nối lại lần {attempt + 1}")
    else:
        raise RuntimeError("nối file cuối hỏng sau 2 lần thử — kiểm tra đĩa và các seg")
    print(f"✅ {final} ({ffprobe_duration(final):.1f}s)")


def concat_only(project: Path) -> None:
    """Re-join the existing segments in plan order — used after re-rendering a few of them."""
    plan = read_json(project / "work" / "plan.json")
    seg = project / "work" / "seg"
    order = [seg / f"{it['id']}.mov" for it in plan if it["type"] != "score"]
    _concat(project, [p for p in order if p.exists()])
