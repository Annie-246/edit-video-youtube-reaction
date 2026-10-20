"""Compose every plan item with ffmpeg, then concatenate."""
from __future__ import annotations
import math, subprocess
from pathlib import Path
from .common import load_project, read_json, run, ffprobe_duration, pick_encoder, escape_ffmpeg_path, FONT_DIR
from .graphics import layout_for
from .memes import place_memes


def _enc(cfg) -> list[str]:
    return pick_encoder(cfg["output"]["encoder"])


def keep_intervals(al: dict) -> list[list[float]]:
    return al.get("keep") or [[al["start"], al["end"]]]


BG_SRC = FONT_DIR.parent / "bg-grid.png"  # white grid; a project can override with assets/bg.png


def _bg(project: Path, L: dict) -> Path:
    """The white grid background, scaled once to the output size."""
    out = project / "work" / "gfx" / "bg.png"
    if not out.exists():
        src = project / "assets" / "bg.png"
        if not src.exists():
            src = BG_SRC
        run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", f"scale={L['w']}:{L['h']}:flags=lanczos", str(out)])
    return out


def _crop(cx: float, cy: float, z: float, ratio: float) -> str:
    cw = f"min(iw\\,ih*{ratio:.4f})/{z}"; ch = f"min(ih\\,iw/{ratio:.4f})/{z}"
    return (f"crop=w={cw}:h={ch}:x=max(0\\,min(iw-{cw}\\,{cx}*iw-{cw}/2)):y=max(0\\,min(ih-{ch}\\,{cy}*ih-{ch}/2))")


def _head_crop(cfg: dict, ratio: float) -> str:
    rc = cfg["recording"]
    return _crop(float(rc.get("cx", 0.5)), float(rc.get("cy", 0.5)), float(rc.get("zoom", 1.0)), ratio)


def _snap(al: dict, fps: int) -> tuple[list[list[float]], float, float, int, float]:
    """Keep intervals relative to the first kept frame, every edge on the frame grid.

    Video can only cut on a frame; audio cuts anywhere, so an unsnapped interval leaves the two
    ~1 frame apart, and the error accumulates over the joins and then over the concatenated
    segments — that is the half-second drift heard mid-video. The segment length is a whole
    number of frames and the audio gets exactly that length, so `-frames:v` and `atrim` agree
    to the sample. `-t` cannot do this: it rounds the two differently."""
    keep = keep_intervals(al)
    t0 = keep[0][0]; t1 = keep[-1][1]
    def q(t: float) -> float:
        return round(round((t - t0) * fps) / fps, 6)
    keep = [[q(s), q(e)] for s, e in keep]
    nfr = max(1, int(round(sum(e - s for s, e in keep) * fps)))
    return keep, t0, t1, nfr, round(nfr / fps, 6)


def _join(keep: list[list[float]], fc: list[str], per_part: list[str] | None = None) -> None:
    """Stumble removal: keep only the good takes, joined with straight cuts landing in silence.
    `per_part` adds a video filter to each part (FACE uses it to change the punch-in per cut)."""
    if len(keep) == 1 and not per_part:
        fc.append("[0:v]null[tv]"); fc.append("[0:a]anull[ta]"); return
    parts = []
    for k, (s, e) in enumerate(keep):
        extra = f",{per_part[k]}" if per_part else ""
        fc.append(f"[0:v]trim=start={s:.6f}:end={e:.6f},setpts=PTS-STARTPTS{extra}[v{k}]")
        fc.append(f"[0:a]atrim=start={s:.6f}:end={e:.6f},asetpts=PTS-STARTPTS[a{k}]")
        parts.append(f"[v{k}][a{k}]")
    fc.append("".join(parts) + f"concat=n={len(keep)}:v=1:a=1[tv][ta]")


def _cap_filter(project: Path, item: dict) -> str:
    cap = project / "work" / "captions" / f"{item['id']}.ass"
    return f",subtitles='{escape_ffmpeg_path(cap)}':fontsdir='{escape_ffmpeg_path(FONT_DIR)}'" if cap.exists() and cap.stat().st_size > 0 else ""


def _full_cards(project: Path, item: dict, fps: int, cmd: list[str], fc: list[str], vtag: str, n_in: int) -> str:
    """Full-frame cards take the whole screen for a few seconds so a key line can land on its own."""
    g = project / "work" / "gfx"
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
    return vtag


def _audio_out(dur: float) -> str:
    # asetpts=N/SR/TB before the atrim is load-bearing: loudnorm pushes the stream's PTS forward by
    # ~2 frames, so atrim=end=<dur> — which measures absolute PTS — silently ate that much off the
    # tail of every segment (~0.5 s summed over a 28-segment video). Rebuilding PTS from the sample
    # count makes the trim length-based. apad=whole_dur alone is NOT a substitute: it never ends
    # the stream, so `-frames:v` stops the mux wherever it happens to be, losing seconds of audio.
    return (f"[ta]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,aformat=channel_layouts=stereo,"
            f"asetpts=N/SR/TB,apad,atrim=end={dur:.6f},asetpts=PTS-STARTPTS[a]")


def _finish(cfg: dict, cmd: list[str], fc: list[str], vtag: str, nfr: int, dur: float, out: Path) -> None:
    fps = cfg["output"]["fps"]
    fc += [f"{vtag}format=yuv420p[v]", _audio_out(dur)]
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-frames:v", str(nfr), "-r", str(fps)] + _enc(cfg) + ["-c:a", "pcm_s16le", str(out)]
    run(cmd)


def render_talk(project: Path, cfg: dict, L: dict, item: dict, al: dict, out: Path) -> None:
    """White layout: big content frame, presenter card top-right, running word captions."""
    fps = cfg["output"]["fps"]; g = project / "work" / "gfx"
    rec = project / "work" / "recording.mp4"
    keep, t0, t1, nfr, dur = _snap(al, fps)
    head, M = L["head"], L["main"]
    ratio = head["w"] / head["h"]
    side = project / "work" / "side" / f"{item['id']}.mp4"
    screen = project / "screens" / f"{item['id']}.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0 + 0.5:.3f}", "-i", str(rec),
           "-loop", "1", "-i", str(g / f"{item['id']}_fg.png"), "-loop", "1", "-i", str(g / "mask_head.png"),
           "-loop", "1", "-i", str(_bg(project, L))]
    fc = [f"[3:v]fps={fps},format=rgb24,trim=duration={dur + 1:.3f}[bg]"]
    _join(keep, fc)
    fc += [f"[tv]fps={fps},{_head_crop(cfg, ratio)},scale={head['w']}:{head['h']},setsar=1[hv]",
           "[2:v]format=gray[hm]", "[hv][hm]alphamerge[ha]", f"[bg][ha]overlay={head['x']}:{head['y']}:shortest=1[a]"]
    last = "[a]"; n_in = 4
    main_src = side if side.exists() else (screen if screen.exists() else None)
    if main_src is not None:
        cmd += ["-i", str(main_src), "-loop", "1", "-i", str(g / "mask_main.png")]
        fc += [f"[{n_in}:v]fps={fps},scale={M['w']}:{M['h']}:force_original_aspect_ratio=increase,crop={M['w']}:{M['h']},setsar=1[sv0]",
               f"[{n_in + 1}:v]format=gray[sm0]", "[sv0][sm0]alphamerge[sa0]",
               f"{last}[sa0]overlay={M['x']}:{M['y']}:eof_action=repeat[p]"]
        last = "[p]"; n_in += 2
    fc.append(f"{last}[1:v]overlay=0:0:shortest=1{_cap_filter(project, item)}[vc]")
    _finish(cfg, cmd, fc, _full_cards(project, item, fps, cmd, fc, "[vc]", n_in), nfr, dur, out)


PUNCH_EVERY = 7.0   # FACE: longest stretch on one framing before the punch-in changes


def _face_parts(keep: list[list[float]], ws: list[dict], fps: int) -> list[list[float]]:
    """Split long takes at a word gap so the framing changes every few seconds, not only at cuts."""
    gaps = [(a["e"] + b["s"]) / 2 for a, b in zip(ws, ws[1:]) if b["s"] - a["e"] > 0.08]
    out, acc = [], 0.0
    for s, e in keep:
        d = e - s
        n = max(1, math.ceil(d / PUNCH_EVERY))
        bounds = [s]
        for j in range(1, n):
            tgt = acc + d * j / n
            near = min(gaps, key=lambda x: abs(x - tgt)) if gaps else tgt
            c = near if abs(near - tgt) < d / n / 2 else tgt
            bounds.append(round(round((s + c - acc) * fps) / fps, 6))
        bounds.append(e)
        out += [[a, b] for a, b in zip(bounds, bounds[1:]) if b - a >= 1.0 / fps]
        acc += d
    return out


def render_face(project: Path, cfg: dict, L: dict, item: dict, al: dict, out: Path, words: list[dict]) -> None:
    """FACE: presenter full screen, framing alternates wide / punched-in at every cut, keyword captions."""
    from .captions import timed_words_for
    fps = cfg["output"]["fps"]; W, H = L["w"], L["h"]
    rec = project / "work" / "recording.mp4"
    keep, t0, t1, nfr, dur = _snap(al, fps)
    fcfg = cfg["recording"].get("face", {})
    cx = float(fcfg.get("cx", 0.5)); cy = float(fcfg.get("cy", 0.45))
    z = float(fcfg.get("zoom", 1.0)); punch = float(fcfg.get("punch", 1.15))
    parts = _face_parts(keep, timed_words_for(item, words, al), fps)
    per = [f"fps={fps},{_crop(cx, cy, z * (punch if k % 2 else 1.0), W / H)},scale={W}:{H},setsar=1" for k in range(len(parts))]
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0 + 0.5:.3f}", "-i", str(rec)]
    fc: list[str] = []
    _join(parts, fc, per)
    keys = project / "work" / "keys" / f"{item['id']}.webm"
    n_in = 1
    if keys.exists():
        # libvpx (not the native vp8 decoder) is what reads the alpha channel
        cmd += ["-c:v", "libvpx", "-i", str(keys)]
        fc += [f"[1:v]fps={fps},format=rgba[kl]", "[tv][kl]overlay=0:0:eof_action=pass,format=yuv420p[vc]"]
        n_in = 2
    else:
        fc.append("[tv]format=yuv420p[vc]")
    _finish(cfg, cmd, fc, _full_cards(project, item, fps, cmd, fc, "[vc]", n_in), nfr, dur, out)


def _round_mask(path: Path, w: int, h: int, r: int, rgba: bool = False) -> Path:
    """Rounded-rectangle mask (gray) or a white rounded plate with alpha, made once with geq."""
    if path.exists():
        return path
    inside = f"lte(pow(max(max({r}-X\\,X-{w - 1 - r})\\,0)\\,2)+pow(max(max({r}-Y\\,Y-{h - 1 - r})\\,0)\\,2)\\,{r * r})"
    vf = f"format=rgba,geq=r=255:g=255:b=255:a='235*{inside}'" if rgba else f"format=gray,geq=lum='255*{inside}'"
    path.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=black:s={w}x{h}", "-frames:v", "1", "-vf", vf, str(path)])
    return path


def render_screen(project: Path, cfg: dict, L: dict, item: dict, al: dict, out: Path) -> None:
    """BUBBLE / MOTION: the scenes fill the screen, no captions. BUBBLE adds the presenter in a
    small rounded card on the right edge; MOTION is voice only."""
    fps = cfg["output"]["fps"]; W, H = L["w"], L["h"]; g = project / "work" / "gfx"
    rec = project / "work" / "recording.mp4"
    keep, t0, t1, nfr, dur = _snap(al, fps)
    side = project / "work" / "side" / f"{item['id']}.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0 + 0.5:.3f}", "-i", str(rec), "-i", str(side)]
    fc: list[str] = []
    _join(keep, fc)
    if item.get("mode") == "bubble":
        # content keeps clear of the bubble; the strip behind it is the same picture, blurred
        A = L["bubble_area"]
        fc += [f"[1:v]fps={fps},setsar=1,trim=duration={dur + 1:.3f},split[s0][s1]",
               f"[s0]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma=40,eq=brightness=-0.06[blur]",
               f"[s1]scale={A}:{H}:force_original_aspect_ratio=decrease,pad={A}:{H}:(ow-iw)/2:(oh-ih)/2:color=black@0,format=rgba[sharp]",
               "[blur][sharp]overlay=0:0,setsar=1[base]"]
    else:
        fc.append(f"[1:v]fps={fps},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,trim=duration={dur + 1:.3f}[base]")
    if item.get("mode") == "bubble":
        B = L["bubble"]; ring = 3
        rc = cfg["recording"]; bc = rc.get("bubble", {})
        crop = _crop(float(bc.get("cx", rc.get("cx", 0.5))), float(bc.get("cy", 0.42)), float(bc.get("zoom", 1.25)), B["w"] / B["h"])
        cmd += ["-loop", "1", "-i", str(_round_mask(g / "mask_bubble.png", B["w"], B["h"], B["r"])),
                "-loop", "1", "-i", str(_round_mask(g / "plate_bubble.png", B["w"] + 2 * ring, B["h"] + 2 * ring, B["r"] + ring, rgba=True))]
        fc += [f"[tv]fps={fps},{crop},scale={B['w']}:{B['h']},setsar=1[hv]", "[2:v]format=gray[hm]", "[hv][hm]alphamerge[ha]",
               f"[base][3:v]overlay={B['x'] - ring}:{B['y'] - ring}[b1]",
               f"[b1][ha]overlay={B['x']}:{B['y']}:shortest=1[vc]"]
        n_in = 4
    else:
        fc += ["[tv]nullsink", f"[base]trim=duration={dur:.6f}[vc]"]
        n_in = 2
    _finish(cfg, cmd, fc, _full_cards(project, item, fps, cmd, fc, "[vc]", n_in), nfr, dur, out)


def render_memes(project: Path, cfg: dict, L: dict, memes: list[dict], body: Path, out: Path) -> None:
    """Cut memes into a rendered talk: the voice pauses, the meme plays with its own sound on black
    (full frame or part of it, no card), then the talk carries on from the same frame."""
    fps = cfg["output"]["fps"]; W, H = L["w"], L["h"]
    total = ffprobe_duration(body)
    def q(t: float) -> float:
        return round(round(t * fps) / fps, 6)
    pts = sorted({q(min(max(m["t"], 0.3), total)): m for m in memes}.items())
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(body)]
    fc, seq, prev, nfr = [], [], 0.0, 0
    for k, (t, m) in enumerate(pts):
        if t > prev:
            fc.append(f"[0:v]trim=start={prev:.6f}:end={t:.6f},setpts=PTS-STARTPTS,setsar=1[bv{k}]")
            fc.append(f"[0:a]atrim=start={prev:.6f}:end={t:.6f},asetpts=PTS-STARTPTS[ba{k}]")
            seq.append(f"[bv{k}][ba{k}]"); nfr += int(round((t - prev) * fps))
        mf = int(round(float(m["secs"]) * fps)); md = mf / fps; nfr += mf
        n = k + 1   # input index of this meme
        if m.get("still"):
            cmd += ["-loop", "1", "-t", f"{md + 0.5:.3f}", "-i", m["file"]]
        else:
            cmd += ["-ss", f"{float(m.get('ss', 0)):.3f}", "-t", f"{md + 0.5:.3f}", "-i", m["file"]]
        part = m.get("mode") == "part"
        bw, bh = (int(W * 0.58) // 2 * 2, int(H * 0.66) // 2 * 2) if part else (W, H)
        x = f"(W-w)/2{'-' if k % 2 else '+'}{int(W * 0.17)}" if part else "(W-w)/2"
        key = ",colorkey=0x00FF00:0.32:0.12" if m.get("green") else ""
        fc.append(f"color=c=black:s={W}x{H}:r={fps}:d={md + 0.5:.3f}[mb{k}]")
        fc.append(f"[{n}:v]fps={fps},scale={bw}:{bh}:force_original_aspect_ratio=decrease,setsar=1,format=rgba{key}[mk{k}]")
        fc.append(f"[mb{k}][mk{k}]overlay=x={x}:y=(H-h)/2,trim=end_frame={mf},setpts=PTS-STARTPTS,setsar=1,format=yuv420p[mv{k}]")
        src_a = f"[{n}:a]loudnorm=I=-18:TP=-2:LRA=11," if m.get("audio") else "anullsrc=r=48000:cl=stereo,"
        fc.append(f"{src_a}aresample=48000,aformat=channel_layouts=stereo,asetpts=N/SR/TB,apad,atrim=end={md:.6f},asetpts=PTS-STARTPTS[ma{k}]")
        seq.append(f"[mv{k}][ma{k}]")
        prev = t
    end = q(total)
    if end > prev:
        fc.append(f"[0:v]trim=start={prev:.6f},setpts=PTS-STARTPTS,setsar=1[bvz]")
        fc.append(f"[0:a]atrim=start={prev:.6f},asetpts=PTS-STARTPTS[baz]")
        seq.append("[bvz][baz]"); nfr += int(round((end - prev) * fps))
    fc.append("".join(seq) + f"concat=n={len(seq)}:v=1:a=1[v][a]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-frames:v", str(nfr), "-r", str(fps)] + _enc(cfg) + ["-c:a", "pcm_s16le", str(out)]
    run(cmd)


def render_clip(project: Path, cfg: dict, L: dict, item: dict, meta: dict, pip_src: Path, pip_is_video: bool, out: Path) -> None:
    """Source clip full screen with Vietnamese subtitles — no presenter, no frame (user's call)."""
    fps = cfg["output"]["fps"]
    src = project / "source" / meta["file"]; off = float(meta.get("offset", 0.0))
    nfr = max(1, int(round((item["end"] - item["start"]) * fps)))
    dur = round(nfr / fps, 6)
    W, H = L["w"], L["h"]
    ass = project / "work" / "subs" / f"{item['id']}.ass"
    sub_f = f",subtitles='{escape_ffmpeg_path(ass)}':fontsdir='{escape_ffmpeg_path(FONT_DIR)}'" if ass.exists() and ass.stat().st_size > 0 else ""
    cov = (load_project(project).get("source") or {}).get("cover_bottom")
    cover = f",drawbox=x=0:y=ih*{cov['y']}:w=iw:h=ih*{cov['h']}:color=black@1:t=fill" if cov else ""
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{off:.3f}", "-t", f"{dur:.3f}", "-i", str(src)]
    fc = [f"[0:v]fps={fps}{cover},scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1{sub_f},format=yuv420p[v]",
          f"[0:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,aformat=channel_layouts=stereo,asetpts=N/SR/TB,apad,atrim=end={dur:.6f},asetpts=PTS-STARTPTS[a]"]
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-frames:v", str(nfr), "-r", str(fps)] + _enc(cfg) + ["-c:a", "pcm_s16le", str(out)]
    run(cmd)


def render_break(project: Path, cfg: dict, L: dict, item: dict, out: Path) -> None:
    """A full-frame card: chapter breaks are silent (they rest the ear); the intro / outro stings
    get a synthesised whoosh + low hit timed to the title slam."""
    from .cards import break_secs
    fps = cfg["output"]["fps"]
    secs = break_secs(cfg, item)
    nfr = max(1, int(round(secs * fps))); dur = round(nfr / fps, 6)
    tpl = item.get("tpl", "chapter")
    hit = {"intro": 22 / fps, "outro": 0.05}.get(tpl)
    audio = "anullsrc=r=48000:cl=stereo" if hit is None else (
        f"aevalsrc='0.35*(random(0)-0.5)*exp(-pow(t-{hit - 0.12:.3f},2)/0.012)"
        f"+gte(t,{hit:.3f})*0.8*sin(2*PI*(42*(t-{hit:.3f})+4*(1-exp(-12*(t-{hit:.3f})))))*exp(-3*(t-{hit:.3f}))'"
        f":s=48000:c=stereo,lowpass=f=6000")
    mp4 = project / "work" / "cards" / f"{item['id']}.mp4"
    png = project / "work" / "gfx" / f"{item['id']}_break.png"
    src = ["-i", str(mp4)] if mp4.exists() else ["-loop", "1", "-t", f"{dur + 0.5:.3f}", "-i", str(png)]
    cmd = ["ffmpeg", "-v", "error", "-y", *src,
           "-f", "lavfi", "-t", f"{dur + 0.5:.3f}", "-i", audio]
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
    words = read_json(project / "work" / "words.json")
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
            mode = it.get("mode", "layout")
            mp = work / "memes" / f"{it['id']}.json"
            memes = place_memes(read_json(mp), it, words, al) if mp.exists() else []
            body = seg / f"{it['id']}.body.mov" if memes else out
            print(f"{it['id']}: đang render talk ({mode})...")
            if mode == "face":
                render_face(project, cfg, L, it, al, body, words)
            elif mode in ("bubble", "motion"):
                render_screen(project, cfg, L, it, al, body)
            else:
                render_talk(project, cfg, L, it, al, body)
            if memes:
                render_memes(project, cfg, L, memes, body, out)
            print(f"{it['id']} → {out.name} ({ffprobe_duration(out):.1f}s)" + (f" · {len(memes)} meme" if memes else ""))
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
