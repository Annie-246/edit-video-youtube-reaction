"""Compose every plan item with ffmpeg, then concatenate."""
from __future__ import annotations
import math, re, subprocess
from pathlib import Path
from .common import load_project, read_json, run, ffprobe_duration, pick_encoder, escape_ffmpeg_path, FONT_DIR
from .graphics import layout_for
from .memes import place_memes, _dims, MAX_UPSCALE


def _enc(cfg) -> list[str]:
    return pick_encoder(cfg["output"]["encoder"])


def keep_intervals(al: dict) -> list[list[float]]:
    return al.get("keep") or [[al["start"], al["end"]]]


BG_SRC = FONT_DIR.parent / "bg-grid-dark.png"  # dark grid (theme); a project can override with assets/bg.png


def _bg(project: Path, L: dict) -> Path:
    """The grid background (dark theme), scaled once to the output size."""
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
    blur_p = keys.with_name(f"{item['id']}.blur.json")
    spans = read_json(blur_p) if blur_p.exists() else []
    base = "[tv]"
    if spans:
        # OVER blurtitle: the presenter goes soft behind the title, in and out with it
        on = "+".join(f"between(t\\,{s:.3f}\\,{e:.3f})" for s, e in spans)
        fc.append(f"[tv]split[bsa][bsb];[bsb]boxblur=22:2[bsc];[bsa][bsc]overlay=0:0:enable='{on}'[tvblur]")
        base = "[tvblur]"
    n_in = 1
    if keys.exists():
        # libvpx (not the native vp8 decoder) is what reads the alpha channel
        cmd += ["-c:v", "libvpx", "-i", str(keys)]
        fc += [f"[1:v]fps={fps},format=rgba[kl]", f"{base}[kl]overlay=0:0:eof_action=pass,format=yuv420p[vc]"]
        n_in = 2
    else:
        fc.append(f"{base}format=yuv420p[vc]")
    _finish(cfg, cmd, fc, _full_cards(project, item, fps, cmd, fc, "[vc]", n_in), nfr, dur, out)
    _apply_orbits(project, cfg, item, out)


def _apply_orbits(project: Path, cfg: dict, item: dict, out: Path) -> None:
    """OVER orbit: cut the presenter out frame by frame over each orbit's span (rembg human
    segmentation, lightly smoothed against flicker) and stack: picture → far half of the ring →
    presenter → near half. Done on the finished FACE body so the cut-out matches its framing."""
    import os, shutil
    spec_p = project / "work" / "keys" / f"{item['id']}.orbit.json"
    spec = read_json(spec_p) if spec_p.exists() else []
    if not spec:
        return
    try:
        import numpy as np
        from PIL import Image
        from rembg import new_session, remove
    except ImportError:
        print(f"   ⚠ {item['id']}: thiếu rembg/pillow (chạy lại setup) → bỏ ảnh xoay 3D"); return
    fps = cfg["output"]["fps"]
    W, H = layout_for(cfg["output"]["width"])["w"], layout_for(cfg["output"]["width"])["h"]
    sess = new_session("u2net_human_seg")
    cur = out
    for k, o in enumerate(spec):
        s, e = float(o["s"]), float(o["e"])
        tmp = out.parent / f"{item['id']}_orbit{k}"
        shutil.rmtree(tmp, ignore_errors=True)
        (tmp / "f").mkdir(parents=True); (tmp / "m").mkdir()
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.3f}", "-t", f"{e - s:.3f}", "-i", str(cur), "-vf", "scale=960:-2", str(tmp / "f" / "%05d.png")])
        prev = None
        for fr in sorted((tmp / "f").glob("*.png")):
            a = np.asarray(remove(Image.open(fr), session=sess, only_mask=True), dtype=np.float32)
            a = a if prev is None else 0.6 * a + 0.4 * prev   # damp frame-to-frame flicker
            prev = a
            Image.fromarray(a.clip(0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR).save(tmp / "m" / fr.name)
        nxt = out.with_name(f"{out.stem}.orbit{k}{out.suffix}")
        on = f"enable='between(t\\,{s:.3f}\\,{e:.3f})'"
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(cur), "-framerate", str(fps), "-i", str(tmp / "m" / "%05d.png"),
               "-c:v", "libvpx", "-i", o["back"], "-c:v", "libvpx", "-i", o["front"]]
        fc = [f"[0:v]split[bg][pv]",
              f"[pv]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS[pvs]",
              f"[1:v]format=gray,gblur=sigma=1.2[mk]", "[pvs][mk]alphamerge,setpts=PTS+{:.3f}/TB[ps]".format(s),
              f"[2:v]fps={fps},format=rgba,setpts=PTS+{s:.3f}/TB[b]", f"[3:v]fps={fps},format=rgba,setpts=PTS+{s:.3f}/TB[f]",
              f"[bg][b]overlay=0:0:eof_action=pass:{on}[s1]", f"[s1][ps]overlay=0:0:eof_action=pass:{on}[s2]",
              f"[s2][f]overlay=0:0:eof_action=pass:{on},format=yuv420p[v]"]
        run(cmd + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "0:a", "-r", str(fps)] + _enc(cfg) + ["-c:a", "copy", str(nxt)])
        if cur != out:
            cur.unlink(missing_ok=True)
        cur = nxt
        shutil.rmtree(tmp, ignore_errors=True)
    os.replace(cur, out)
    print(f"   {item['id']}: ghép {len(spec)} vòng ảnh xoay 3D")


def _round_mask(path: Path, w: int, h: int, r: int, rgba: bool = False) -> Path:
    """Rounded-rectangle mask (gray) or a white rounded plate with alpha, made once with geq."""
    if path.exists():
        return path
    inside = f"lte(pow(max(max({r}-X\\,X-{w - 1 - r})\\,0)\\,2)+pow(max(max({r}-Y\\,Y-{h - 1 - r})\\,0)\\,2)\\,{r * r})"
    vf = f"format=rgba,geq=r=255:g=255:b=255:a='235*{inside}'" if rgba else f"format=gray,geq=lum='255*{inside}'"
    path.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=black:s={w}x{h}", "-frames:v", "1", "-vf", vf, str(path)])
    return path


RIM = ((240, 180, 154), (217, 119, 87), (181, 83, 47))   # #F0B49A → #D97757 → #B5532F, top-left → bottom-right


def _inside(x: int, y: int, w: int, h: int, r: int) -> str:
    """geq expression: 1 inside the rounded rectangle, 0 outside."""
    X, Y = f"(X-{x})", f"(Y-{y})"
    return (f"between({X}\\,0\\,{w - 1})*between({Y}\\,0\\,{h - 1})*"
            f"lte(pow(max(max({r}-{X}\\,{X}-{w - 1 - r})\\,0)\\,2)+pow(max(max({r}-{Y}\\,{Y}-{h - 1 - r})\\,0)\\,2)\\,{r * r})")


def _card_plate(path: Path, L: dict, cards: list[dict]) -> Path:
    """Full-frame RGBA layer for BUBBLE / MOTION: a soft shadow under each card and the card's
    orange gradient rim. The card content is laid on top, so only the rim stays visible."""
    if path.exists():
        return path
    W, H, k, S = L["w"], L["h"], L["rim"], L["shadow"]
    drops = "+".join(_inside(c["x"], c["y"] + S["dy"], c["w"], c["h"], c["r"]) for c in cards)
    fc = [f"color=black@0:s={W}x{H},format=rgba,geq=r=20:g=20:b=19:a='{int(255 * S['alpha'])}*min(1\\,{drops})',"
          f"gblur=sigma={S['blur']}[l0]"]
    for n, c in enumerate(cards):
        # each card runs the whole gradient across its own diagonal
        t = f"((X-{c['x']}+Y-{c['y']})/{c['w'] + c['h']})"
        def ch(i: int) -> str:
            a, b, d = RIM[0][i], RIM[1][i], RIM[2][i]
            return f"'clip(if(lt({t}\\,0.5)\\,{a}+({b - a})*{t}*2\\,{b}+({d - b})*({t}*2-1))\\,0\\,255)'"
        inside = _inside(c["x"] - k, c["y"] - k, c["w"] + 2 * k, c["h"] + 2 * k, c["r"] + k)
        fc.append(f"color=black@0:s={W}x{H},format=rgba,geq=r={ch(0)}:g={ch(1)}:b={ch(2)}:a='255*{inside}'[r{n}]")
        fc.append(f"[l{n}][r{n}]overlay=0:0:format=auto,format=rgba[l{n + 1}]")
    fc = ";".join(fc)[:-len(f"[l{len(cards)}]")]
    path.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", "-filter_complex", fc, "-frames:v", "1", str(path)])
    return path


MORPH = 0.6   # seconds the presenter takes to shrink into / grow out of the MOTION bubble


def _rec_time(keep: list[list[float]], t0: float, t: float) -> float:
    """Second in recording.mp4 of second `t` of a cut talk."""
    acc = 0.0
    for s, e in keep:
        if t < acc + (e - s):
            return t0 + s + (t - acc)
        acc += e - s
    return t0 + keep[-1][1]


def _bubble_morph(project: Path, cfg: dict, L: dict, al: dict, out: Path, enter: str | None, leave: str | None, mode: str = "motion") -> None:
    """Joins with the neighbouring talk, done on this talk's first / last MORPH seconds.
    `enter` / `leave` name the neighbour's kind:
      "face"   full-screen presenter ↔ this layout's presenter frame (the round bubble of MOTION, the
               rounded card of BUBBLE, the portrait card of the white layout): the presenter shrinks
               into it / grows out of it, corners rounding, crop easing, rim fading in.
      "bubble" (MOTION only) BUBBLE ↔ MOTION: the big screen-recording card opens up to full screen
               with the graphics inside it, while the presenter's card rounds off and slides into the
               bubble; the other way it closes back into the card.
    The presenter never stops: the frames are the talk's own recording, so picture and voice stay
    together across the join."""
    if not (enter or leave):
        return
    import os, shutil
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter
    fps = cfg["output"]["fps"]; W, H = L["w"], L["h"]
    keep, t0, _, nfr, dur = _snap(al, fps)
    n = max(2, int(round(MORPH * fps)))
    rec = project / "work" / "recording.mp4"
    rc = cfg["recording"]; fc_ = rc.get("face", {}); dc = rc.get("dot", {})
    # the frame the presenter lands in: outer box (rim included), corner radius, rim width, rim colour
    if mode == "motion":
        D = L["dot"]; R = D["d"] + 2 * D["rim"]
        bx, by, bw, bh, brad, rim, clay = W - D["m"] - R, H - D["m"] - R, R, R, R / 2, D["rim"], True
    elif mode == "bubble":
        B = L["bubble"]; k = L["rim"]
        bx, by, bw, bh, brad, rim, clay = B["x"] - k, B["y"] - k, B["w"] + 2 * k, B["h"] + 2 * k, B["r"] + k, k, True
    else:
        Hd = L["head"]; k = int(6 * L["s"])
        bx, by, bw, bh, brad, rim, clay = Hd["x"] - k, Hd["y"] - k, Hd["w"] + 2 * k, Hd["h"] + 2 * k, Hd["r"] + k, k, False
    iw, ih = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                     "-of", "csv=p=0", str(rec)], capture_output=True, text=True).stdout.strip().split(",")[:2])

    def window(cx: float, cy: float, z: float, ratio: float) -> tuple[float, float, float, float]:
        cw = min(iw, ih * ratio) / z; ch = min(ih, iw / ratio) / z
        return (max(0, min(iw - cw, cx * iw - cw / 2)), max(0, min(ih - ch, cy * ih - ch / 2)), cw, ch)

    face_w = window(float(fc_.get("cx", 0.5)), float(fc_.get("cy", 0.45)), float(fc_.get("zoom", 1.0)), W / H)
    if mode == "motion":
        dot_w = window(float(dc.get("cx", rc.get("cx", 0.5))), float(dc.get("cy", 0.5)), float(dc.get("zoom", 1.0)), 1.0)
    elif mode == "bubble":
        bc = rc.get("bubble", {})
        dot_w = window(float(bc.get("cx", rc.get("cx", 0.5))), float(bc.get("cy", 0.42)), float(bc.get("zoom", 1.25)), L["bubble"]["w"] / L["bubble"]["h"])
    else:
        dot_w = window(float(rc.get("cx", 0.5)), float(rc.get("cy", 0.5)), float(rc.get("zoom", 1.0)), L["head"]["w"] / L["head"]["h"])
    # the BUBBLE layout this talk may open out of / close into
    Bc = L["bubble"]; kb = L["rim"]; Cc = L["screen"]["bubble"]
    bub_box = (Bc["x"] - kb, Bc["y"] - kb, Bc["w"] + 2 * kb, Bc["h"] + 2 * kb, Bc["r"] + kb, kb)
    bcfg = rc.get("bubble", {})
    bub_w = window(float(bcfg.get("cx", rc.get("cx", 0.5))), float(bcfg.get("cy", 0.42)), float(bcfg.get("zoom", 1.25)), Bc["w"] / Bc["h"])
    bg_img = Image.open(_bg(project, L)).convert("RGB").resize((W, H)) if "bubble" in (enter, leave) else None
    ease = lambda x: 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
    lerp = lambda a, b, p: a + (b - a) * p
    # clay ring gradient (#F0B49A → #D97757 → #B5532F along the diagonal), cut to shape per frame
    gy, gx = np.mgrid[0:H, 0:W].astype(np.float32)
    tt = ((gx + gy) / (W + H))[..., None]
    c0, c1, c2 = (np.array(c, np.float32) for c in RIM)
    ring = np.where(tt < 0.5, c0 + (c1 - c0) * tt * 2, c1 + (c2 - c1) * (tt * 2 - 1)).astype(np.uint8)
    ring_img = Image.fromarray(ring, "RGB") if clay else Image.new("RGB", (W, H), (38, 37, 35))

    spans = ([("enter", 0.0, enter)] if enter else []) + ([("leave", max(0.0, dur - n / fps), leave)] if leave else [])
    cur = out
    for kind, start, via in spans:
        tmp = out.parent / f"{out.stem}_morph_{kind}"
        shutil.rmtree(tmp, ignore_errors=True); tmp.mkdir(parents=True)
        src = tmp / "src"; src.mkdir()
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{_rec_time(keep, t0, start):.3f}", "-i", str(rec), "-frames:v", str(n), str(src / "%04d.png")])
        frames = sorted(src.glob("*.png"))
        if via == "bubble":
            body = tmp / "body"; body.mkdir()
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}", "-i", str(cur), "-frames:v", str(n), "-vf", f"scale={W}:{H}", str(body / "%04d.png")])
            bodies = sorted(body.glob("*.png"))
            sx, sy, sw, sh_, srad, srim = bub_box; swin = bub_w
        else:
            sx, sy, sw, sh_, srad, srim = 0, 0, W, H, 0, 0; swin = face_w
        for i, fr in enumerate(frames):
            x = i / (len(frames) - 1)
            p = ease(x) if kind == "enter" else ease(1 - x)          # p: 0 = the neighbour's look, 1 = this talk's
            rx, ry, rw, rh = lerp(sx, bx, p), lerp(sy, by, p), lerp(sw, bw, p), lerp(sh_, bh, p)
            rad = lerp(srad, brad, p)
            k = lerp(srim, rim, p)
            cx_, cy_, cw_, ch_ = (lerp(a, b, p) for a, b in zip(swin, dot_w))
            img = Image.open(fr).convert("RGB").crop((int(cx_), int(cy_), int(cx_ + cw_), int(cy_ + ch_)))
            iw2, ih2 = max(2, int(rw - 2 * k)), max(2, int(rh - 2 * k))
            img = img.resize((iw2, ih2), Image.LANCZOS)
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            # shadow, then the ring, then the picture inside it
            sh = Image.new("L", (W, H), 0)
            sp = 1.0 if via == "bubble" else p
            ImageDraw.Draw(sh).rounded_rectangle((rx, ry + 20 * sp, rx + rw, ry + rh + 20 * sp), radius=rad, fill=int(92 * sp))
            layer.paste((20, 20, 19, 255), (0, 0, W, H), sh.filter(ImageFilter.GaussianBlur(22)))
            if k > 0.3:
                m = Image.new("L", (W, H), 0)
                ImageDraw.Draw(m).rounded_rectangle((rx, ry, rx + rw, ry + rh), radius=rad, fill=255)
                layer.paste(ring_img, (0, 0), m)
            m2 = Image.new("L", (iw2, ih2), 0)
            ImageDraw.Draw(m2).rounded_rectangle((0, 0, iw2 - 1, ih2 - 1), radius=max(0, rad - k), fill=255)
            layer.paste(img, (int(rx + k), int(ry + k)), m2)
            if via == "bubble" and i < len(bodies):
                # the big card opening up: the graphics show through a rounded window that grows
                # from the screen-recording card to the whole frame, its clay rim thinning away
                ox, oy = lerp(Cc["x"], 0, p), lerp(Cc["y"], 0, p)
                ow, oh = lerp(Cc["w"], W, p), lerp(Cc["h"], H, p)
                orad, ok = lerp(Cc["r"], 0, p), kb * (1 - p)
                canvas = bg_img.copy().convert("RGBA")
                if ok > 0.3:
                    mr = Image.new("L", (W, H), 0)
                    ImageDraw.Draw(mr).rounded_rectangle((ox - ok, oy - ok, ox + ow + ok, oy + oh + ok), radius=orad + ok, fill=255)
                    canvas.paste(ring_img, (0, 0), mr)
                mw = Image.new("L", (W, H), 0)
                dw = ImageDraw.Draw(mw)
                dw.rounded_rectangle((ox, oy, ox + ow, oy + oh), radius=orad, fill=255)
                # the talk's own bubble is baked into these frames: keep it hidden (plain background
                # there), the moving one lands on that spot
                hole = (bx - 30, by - 10, bx + bw + 30, by + bh + 50)
                dw.ellipse(hole, fill=0)
                canvas.paste(Image.open(bodies[i]).convert("RGB"), (0, 0), mw)
                mh = Image.new("L", (W, H), 0)
                ImageDraw.Draw(mh).ellipse(hole, fill=255)
                canvas.paste(bg_img, (0, 0), mh)
                canvas.alpha_composite(layer)
                layer = canvas
            layer.save(tmp / f"{i:04d}.png")
        nxt = out.with_name(f"{out.stem}.morph_{kind}{out.suffix}")
        run(["ffmpeg", "-v", "error", "-y", "-i", str(cur), "-framerate", str(fps), "-i", str(tmp / "%04d.png"),
             # growing out: hold the last (full-frame) picture to the very end, or the graphics flash back for a frame
             "-filter_complex", f"[1:v]format=rgba,setpts=PTS+{start:.6f}/TB[m];[0:v][m]overlay=0:0:eof_action={'repeat' if kind == 'leave' else 'pass'},format=yuv420p[v]",
             "-map", "[v]", "-map", "0:a", "-r", str(fps)] + _enc(cfg) + ["-c:a", "copy", str(nxt)])
        if cur != out:
            cur.unlink(missing_ok=True)
        cur = nxt
        shutil.rmtree(tmp, ignore_errors=True)
    os.replace(cur, out)
    print("   chuyển cảnh: " + " + ".join(("vào từ " if k == "enter" else "ra sang ") + v for k, _, v in spans))


def _dot_mask(path: Path, d: int) -> Path:
    """Gray disc mask for the MOTION presenter bubble."""
    if path.exists():
        return path
    c = (d - 1) / 2
    path.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=black:s={d}x{d}", "-frames:v", "1",
         "-vf", f"format=gray,geq=lum='255*lte(pow(X-{c}\\,2)+pow(Y-{c}\\,2)\\,{c * c})'", str(path)])
    return path


def _dot_plate(path: Path, L: dict, x: int, y: int, R: int) -> Path:
    """Full-frame RGBA layer: soft shadow under the bubble and its orange gradient ring."""
    if path.exists():
        return path
    W, H, S = L["w"], L["h"], L["shadow"]
    r = R / 2; cx, cy = x + r, y + r
    disc = lambda ox, oy: f"lte(pow(X-{cx + ox}\\,2)+pow(Y-{cy + oy}\\,2)\\,{r * r})"
    t = f"((X-{x}+Y-{y})/{2 * R})"
    def ch(i: int) -> str:
        a, b, dd = RIM[0][i], RIM[1][i], RIM[2][i]
        return f"'clip(if(lt({t}\\,0.5)\\,{a}+({b - a})*{t}*2\\,{b}+({dd - b})*({t}*2-1))\\,0\\,255)'"
    fc = (f"color=black@0:s={W}x{H},format=rgba,geq=r=20:g=20:b=19:a='{int(255 * S['alpha'])}*{disc(0, S['dy'])}',gblur=sigma={S['blur']}[sh];"
          f"color=black@0:s={W}x{H},format=rgba,geq=r={ch(0)}:g={ch(1)}:b={ch(2)}:a='255*{disc(0, 0)}'[ring];"
          f"[sh][ring]overlay=0:0:format=auto,format=rgba")
    path.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", "-filter_complex", fc, "-frames:v", "1", str(path)])
    return path


def render_screen(project: Path, cfg: dict, L: dict, item: dict, al: dict, out: Path) -> None:
    """BUBBLE: the scenes play in a big rounded card on the white grid (orange gradient rim, shadow
    underneath), the presenter in a small card on the right. MOTION has no presenter, so no grid
    either: the scenes fill the screen, voice only. No captions in both."""
    fps = cfg["output"]["fps"]; g = project / "work" / "gfx"
    mode = item.get("mode"); C = L["screen"][mode]; B = L["bubble"]
    rec = project / "work" / "recording.mp4"
    keep, t0, t1, nfr, dur = _snap(al, fps)
    side = project / "work" / "side" / f"{item['id']}.mp4"
    if mode == "motion":
        # graphics fill the screen; the presenter rides along in a round bubble bottom-right
        # (wide crop: background and shirt stay in, not just the face)
        D = L["dot"]; d = D["d"]; R = d + 2 * D["rim"]
        x, y = L["w"] - D["m"] - R, L["h"] - D["m"] - R
        rc = cfg["recording"]; dc = rc.get("dot", {})
        crop = _crop(float(dc.get("cx", rc.get("cx", 0.5))), float(dc.get("cy", 0.5)), float(dc.get("zoom", 1.0)), 1.0)
        plate = _dot_plate(g / f"dot_{L['w']}x{L['h']}_{d}.png", L, x, y, R)
        dmask = _dot_mask(g / f"mask_dot_{d}.png", d)
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0 + 0.5:.3f}", "-i", str(rec), "-i", str(side),
               "-loop", "1", "-i", str(plate), "-loop", "1", "-i", str(dmask)]
        fc: list[str] = []
        _join(keep, fc)
        fc += [f"[1:v]fps={fps},scale={L['w']}:{L['h']}:force_original_aspect_ratio=increase,crop={L['w']}:{L['h']},setsar=1,"
               f"trim=duration={dur:.6f}[sv]", "[2:v]format=rgba[dp]", "[sv][dp]overlay=0:0:shortest=1[sp]",
               f"[tv]fps={fps},{crop},scale={d}:{d},setsar=1[fv]", "[3:v]format=gray[fm]", "[fv][fm]alphamerge[fa]",
               f"[sp][fa]overlay={x + D['rim']}:{y + D['rim']}:shortest=1[vc]"]
        _finish(cfg, cmd, fc, _full_cards(project, item, fps, cmd, fc, "[vc]", 4), nfr, dur, out)
        return
    cards = [C, B]
    # cached by name, so the names carry the sizes
    plate = _card_plate(g / f"rim_{mode}_{C['w']}x{C['h']}.png", L, cards)
    cmask = _round_mask(g / f"mask_card_{C['w']}x{C['h']}.png", C["w"], C["h"], C["r"])
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0 + 0.5:.3f}", "-i", str(rec), "-i", str(side),
           "-loop", "1", "-i", str(_bg(project, L)), "-loop", "1", "-i", str(plate), "-loop", "1", "-i", str(cmask)]
    fc = [f"[2:v]fps={fps},format=rgb24,trim=duration={dur + 1:.3f}[bg]", "[3:v]format=rgba[pl]", "[bg][pl]overlay=0:0:shortest=1[bp]"]
    _join(keep, fc)
    fc += [f"[1:v]fps={fps},scale={C['w']}:{C['h']}:force_original_aspect_ratio=increase,crop={C['w']}:{C['h']},setsar=1[sv]",
           "[4:v]format=gray[sm]", "[sv][sm]alphamerge[sa]", f"[bp][sa]overlay={C['x']}:{C['y']}:eof_action=repeat,setsar=1[base]"]
    rc = cfg["recording"]; bc = rc.get("bubble", {})
    crop = _crop(float(bc.get("cx", rc.get("cx", 0.5))), float(bc.get("cy", 0.42)), float(bc.get("zoom", 1.25)), B["w"] / B["h"])
    cmd += ["-loop", "1", "-i", str(_round_mask(g / f"mask_face_{B['w']}x{B['h']}.png", B["w"], B["h"], B["r"]))]
    fc += [f"[tv]fps={fps},{crop},scale={B['w']}:{B['h']},setsar=1[hv]", "[5:v]format=gray[hm]", "[hv][hm]alphamerge[ha]",
           f"[base][ha]overlay={B['x']}:{B['y']}:shortest=1[vc]"]
    _finish(cfg, cmd, fc, _full_cards(project, item, fps, cmd, fc, "[vc]", 6), nfr, dur, out)


DUCK = 0.28     # presenter level while a meme with sound plays over the talk
MEME_DB = -20.0  # mean level a meme's sound is brought to (the voice sits near -19 dB)


def _mean_db(f: Path, ss: float, secs: float) -> float | None:
    """Mean level of the part of a meme that will play; None if it has no audio stream."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-ss", f"{ss:.3f}", "-t", f"{secs:.3f}", "-i", str(f), "-vn", "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"mean_volume: (-?[\d.]+) dB", r.stderr)
    return float(m.group(1)) if m else None


def render_memes(project: Path, cfg: dict, L: dict, memes: list[dict], body: Path, out: Path) -> None:
    """Lay memes over a rendered talk, right after the sentence their anchor belongs to: the meme
    shows on black (full frame or part of it, no card) while the presenter keeps talking. A meme
    with sound plays it and ducks the voice for its length; a still is silent. Length unchanged."""
    fps = cfg["output"]["fps"]; W, H = L["w"], L["h"]
    total = ffprobe_duration(body)
    nfr = int(round(total * fps)); dur = nfr / fps
    def q(t: float) -> float:
        return round(round(t * fps) / fps, 6)
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(body)]
    fc, vtag, mixes, ducks = [], "[0:v]", [], []
    for k, m in enumerate(sorted(memes, key=lambda m: m["t"])):
        t = q(min(max(m["t"], 0.3), total - 0.5))
        md = min(int(round(float(m["secs"]) * fps)) / fps, dur - t)
        n = k + 1   # input index of this meme
        if m.get("still"):
            cmd += ["-loop", "1", "-t", f"{md + 0.5:.3f}", "-i", m["file"]]
        else:
            cmd += ["-ss", f"{float(m.get('ss', 0)):.3f}", "-t", f"{md + 0.5:.3f}", "-i", m["file"]]
        part = m.get("mode") == "part"
        bw, bh = (int(W * 0.58) // 2 * 2, int(H * 0.66) // 2 * 2) if part else (W, H)
        x = f"(W-w)/2{'-' if k % 2 else '+'}{int(W * 0.17)}" if part else "(W-w)/2"
        if not m.get("still"):   # blur standard: never enlarge a clip past MAX_UPSCALE x its own pixels
            sw, sh = _dims(Path(m["file"]))
            if sw and sh and min(bw / sw, bh / sh) > MAX_UPSCALE:
                bw, bh = int(sw * MAX_UPSCALE) // 2 * 2, int(sh * MAX_UPSCALE) // 2 * 2
        key = ",colorkey=0x00FF00:0.32:0.12" if m.get("green") else ""
        fc.append(f"color=c=black:s={W}x{H}:r={fps}:d={md + 0.5:.3f}[mb{k}]")
        fc.append(f"[{n}:v]fps={fps},scale={bw}:{bh}:force_original_aspect_ratio=decrease,setsar=1,format=rgba{key}[mk{k}]")
        fc.append(f"[mb{k}][mk{k}]overlay=x={x}:y=(H-h)/2,trim=duration={md:.6f},setpts=PTS-STARTPTS+{t:.6f}/TB,setsar=1[mv{k}]")
        fc.append(f"{vtag}[mv{k}]overlay=0:0:eof_action=pass[vo{k}]")
        vtag = f"[vo{k}]"
        level = _mean_db(Path(m["file"]), float(m.get("ss", 0)), md) if m.get("audio") and not m.get("still") else None
        if level is not None and level > -50:
            # plain gain, never loudnorm: on a clip that opens silent loudnorm lifts the hiss to 0 dB
            gain = min(12.0, MEME_DB - level)
            ms = int(round(t * 1000))
            fc.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,volume={gain:.1f}dB,alimiter=limit=0.9,"
                      f"atrim=end={md:.6f},afade=t=out:st={max(0.0, md - 0.15):.3f}:d=0.15,adelay={ms}|{ms}[ma{k}]")
            mixes.append(f"[ma{k}]")
            # ramp the voice down/up over 0.15 s so the duck never clicks
            ducks.append(f"min(1,max(0,min((t-{t:.3f})/0.15,({t + md:.3f}-t)/0.15)))")
    # quoted, so the commas inside need no escaping
    vol = f",volume='1-{1 - DUCK}*min(1,{'+'.join(ducks)})':eval=frame" if ducks else ""
    fc.append(f"[0:a]aformat=channel_layouts=stereo{vol}[voice]")
    if mixes:
        fc.append(f"[voice]{''.join(mixes)}amix=inputs={len(mixes) + 1}:duration=first:normalize=0,"
                  f"asetpts=N/SR/TB,apad,atrim=end={dur:.6f},asetpts=PTS-STARTPTS[a]")
    else:
        fc.append(f"[voice]asetpts=N/SR/TB,apad,atrim=end={dur:.6f},asetpts=PTS-STARTPTS[a]")
    fc.append(f"{vtag}format=yuv420p[v]")
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
    """A full-frame card: chapter breaks are silent (they rest the ear); the outro sting gets a
    synthesised whoosh + low hit."""
    from .cards import break_secs
    fps = cfg["output"]["fps"]
    secs = break_secs(cfg, item)
    nfr = max(1, int(round(secs * fps))); dur = round(nfr / fps, 6)
    tpl = item.get("tpl", "chapter")
    hit = 0.05 if tpl == "outro" else None
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
    seq = [i for i in plan if i["type"] != "score"]
    def _is_face(i: int) -> bool:
        return 0 <= i < len(seq) and seq[i]["type"] == "talk" and seq[i].get("mode") == "face"
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
            if mode != "face":
                # joins: shrink from / grow to a full-screen FACE talk; MOTION also opens out of /
                # closes into a neighbouring BUBBLE talk's big card
                k = seq.index(it)
                def _via(j: int) -> str | None:
                    if _is_face(j):
                        return "face"
                    if mode == "motion" and 0 <= j < len(seq) and seq[j]["type"] == "talk" and seq[j].get("mode") == "bubble":
                        return "bubble"
                    return None
                _bubble_morph(project, cfg, L, al, body, enter=_via(k - 1), leave=_via(k + 1), mode=mode)
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
