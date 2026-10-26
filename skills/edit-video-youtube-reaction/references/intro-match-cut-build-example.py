"""Intro test v2 (fast match-cut style), after feedback on v1:
- match cuts: smooth push-in (zoompan on a 4K upscale, no 1-px jitter), the same push speed on every
  shot so motion carries across a cut, and the Jensen -> presenter cut lined up face on face;
- music bed (Kevin MacLeod "Hitman", CC BY 4.0) placed so its drop lands on "thông điệp xuyên suốt",
  ducked under the voice, cut to silence before the title (L15);
- SFX cut down to two, both from myinstants: soft cinematic swoosh (L1) and one boom on the title (L5);
- keyword captions over the presenter and the footage (Keys composition), not over the cards.
Output: out/intro_test_matchcut_v2.mp4
"""
import base64, json, subprocess, sys
from pathlib import Path

PRJ = Path(__file__).resolve().parents[2]
W = PRJ / "work" / "intro_test"
CL = W / "clips_v2"; CL.mkdir(parents=True, exist_ok=True)
CARDS = W / "clips"                       # Remotion cards rendered by build.py (unchanged)
MOTION = Path("C:/Users/pthao/.claude/plugins/data/edit-video-youtube-reaction-edit-video-youtube-reaction/motion")
SFX = PRJ / "assets" / "sfx" / "myinstants"
MUSIC = PRJ / "assets" / "music" / "Hitman.mp3"
FPS = 30
END_VOICE = 44.85
TITLE_AT, TITLE_LEN = 45.10, 1.80
TOTAL = TITLE_AT + TITLE_LEN
MUSIC_DROP = 51.95                         # the drop in "Hitman"
DROP_AT = 24.25                            # ...lands on the cut to "thông điệp xuyên suốt"
MUSIC_OFF = MUSIC_DROP - DROP_AT           # music time at intro 0
BEAT = 0.409                               # 146.7 BPM after the drop
beat = lambda k: round(DROP_AT + k * BEAT, 3)

KEEP = [(0.0, 14.39, 0.86), (14.39, 18.62, 15.99), (18.62, 44.905, 25.045)]
def src_of(t):
    for a, b, s in KEEP:
        if a <= t < b + 1e-6:
            return s + (t - a)
    raise ValueError(t)

# face framing: (zoom, top of the crop as a share of the frame). 1.15 / 0.13 puts the presenter's
# face at ~34 % height, the same place Jensen's face sits after the 1.23 crop below
WIDE, TIGHT = (1.0, 0.0), (1.15, 0.13)

EDL = [
    (0.00, 2.10, "src", {"at": 70}),
    (2.10, 3.20, "src", {"at": 300}),
    (3.20, 4.60, "card", {"name": "nvidia"}),
    (4.60, 6.50, "face", {"frames": [(4.60, WIDE)]}),
    (6.50, 7.55, "card", {"name": "stat87"}),
    (7.55, 8.80, "src", {"at": 3610}),
    (8.80, 11.30, "card", {"name": "stat15k"}),
    (11.30, 13.40, "card", {"name": "stat100"}),
    (13.40, 14.50, "src", {"at": 3140}),
    (14.50, 16.90, "face", {"frames": [(14.50, TIGHT)]}),
    (16.90, 18.60, "src", {"at": 905}),
    (18.60, 18.95, "src", {"at": 3760}),
    (18.95, 19.30, "src", {"at": 3900}),
    (19.30, 19.65, "src", {"at": 4745}),
    (19.65, 20.05, "src", {"at": 100}),
    (20.05, 21.75, "src", {"at": 4500, "crop": (1.23, 0.053, 0.0)}),   # Jensen's face to ~31 % height
    (21.75, 24.25, "face", {"frames": [(21.75, TIGHT), (22.80, WIDE)]}),  # face-on-face match, then open up on "rất đáng"
    (24.25, 26.25, "src", {"at": 2160}),                                 # music drop
    (26.25, 28.55, "face", {"frames": [(26.25, WIDE), (27.40, TIGHT)]}),  # punch-in on "quan trọng"
    (28.55, 31.00, "slice", {"card": "t01_full1", "from": 0.45}),
    (31.00, 32.70, "src", {"at": 3360}),
    (32.70, 34.10, "face", {"frames": [(32.70, TIGHT)]}),
    (34.10, 35.05, "card", {"name": "chatgpt"}),
    (35.05, 35.65, "card", {"name": "claude"}),
    (35.65, 37.00, "slice", {"card": "t01_full1", "from": 1.95}),
    (37.00, 39.30, "face", {"frames": [(37.00, WIDE), (38.50, TIGHT)]}),
    (39.30, 40.45, "slice", {"card": "t01_full1", "from": 4.10}),
    (40.45, beat(42), "slice", {"card": "t01_full1", "from": 5.20}),
    # "thực hiện cả một quy trình": one shot per beat
    (beat(42), beat(43), "src", {"at": 3420}), (beat(43), beat(44), "src", {"at": 2880}),
    (beat(44), beat(45), "src", {"at": 1300}), (beat(45), beat(46), "src", {"at": 4300}),
    (beat(46), beat(47), "src", {"at": 4870}),
    (beat(47), END_VOICE, "face", {"frames": [(beat(47), TIGHT)]}),
    (END_VOICE, TITLE_AT, "black", {}),
    (TITLE_AT, TOTAL, "card", {"name": "title"}),
]

# keyword captions: (first spoken word index, text with *keywords*, style); skipped over cards and slices
KEYS = [
    ("Ngày *21/10* vừa rồi", "line"),
    ("*Jensen* *Huang*", "stack"),
    ("đã có một *bài* *phát* *biểu*", "line"),
    ("tại *Berlin*", "line"),
    ("trên *toàn* *thế* *giới*", "line"),
    ("Và với *vị* *thế*", "line"),
    ("cung cấp *chip* *AI*", "stack"),
    ("các *ngành* *công* *nghiệp*", "line"),
    ("những gì *Jensen* *Huang* chia sẻ", "line"),
    ("*rất* *đáng* để chúng ta chú ý", "line"),
    ("*thông* *điệp* xuyên suốt", "stack"),
    ("mình thấy đặc biệt *quan* *trọng*", "line"),
    ("sang *tự* *thực* *hiện* công việc", "line"),
    ("thay vì chỉ *hỏi*", "line"),
    ("giờ đây *AI* đã có thể", "line"),
    ("cả một *quy* *trình*", "stack"),
    ("*công* *việc* cho chúng ta", "line"),
]

SFX_PLAN = [
    # (event time, file, peak offset in file, gain dB, rule, note)
    (31.00, "deep-swoosh", 1.50, -16, "L1", "chuyển sang 'tự thực hiện công việc' (vắt qua điểm cắt)"),
    (TITLE_AT, "cinematic-boom-hq", 0.18, -8, "L5", "thẻ tiêu đề kết intro, sau 0,32 s im lặng (L15)"),
]


def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=isinstance(cmd, str))
    if r.returncode != 0:
        sys.exit(f"FAILED: {cmd}\n{r.stderr[-2500:]}")


def frames(a, b):
    return round(b * FPS) - round(a * FPS)


ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-an", "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709"]
NORM = "scale=out_range=tv:out_color_matrix=bt709,format=yuv420p"   # one colour format for every clip (a change mid-stream resets the filter graph and drops frames)
PUSH = 0.0009                              # zoom gained per frame, same on every footage shot


def make_clip(i, a, b, kind, args):
    out = CL / f"{i:03d}.mp4"
    n = frames(a, b)
    if out.exists():
        return out
    if kind == "src":
        z0, x0, y0 = args.get("crop", (1.0, None, None))
        # crop first (face match), then a sub-pixel push-in done at 4K and scaled back down
        pre = "fps=30"
        if z0 != 1.0:
            w, h = 1920 / z0, 1080 / z0
            pre += f",crop={w:.0f}:{h:.0f}:{x0 * 1920:.0f}:{y0 * 1080:.0f}"
        zp = f"zoompan=z='1+{PUSH}*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=3840x2160:fps=30"
        vf = f"{pre},scale=3840:2160:flags=lanczos,{zp},scale=1920:1080:flags=lanczos,setsar=1,{NORM}"
        run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(args["at"]), "-i", str(PRJ / "source" / "full.mp4"), "-vf", vf, *ENC, "-frames:v", str(n), str(out)])
    elif kind in ("card", "slice"):
        srcf = CARDS / f"card_{args['name']}.mp4" if kind == "card" else PRJ / "work" / "cards" / f"{args['card']}.mp4"
        ss = ["-ss", str(args["from"])] if kind == "slice" else []
        run(["ffmpeg", "-loglevel", "error", "-y", *ss, "-i", str(srcf), "-vf", f"fps=30,scale=1920:1080,setsar=1,{NORM}", *ENC, "-frames:v", str(n), str(out)])
    elif kind == "black":
        run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=1920x1080:r=30", "-vf", f"{NORM}", *ENC, "-frames:v", str(n), str(out)])
    elif kind == "face":
        marks = args["frames"] + [(b, None)]
        subs = []
        for k in range(len(marks) - 1):
            x, (z, top) = marks[k]
            y = marks[k + 1][0]
            sp = CL / f"{i:03d}_{k}.mp4"
            vf = f"fps=30,setsar=1,{NORM}" if z == 1.0 else \
                f"fps=30,scale={round(1920 * z)}:{round(1080 * z)}:flags=lanczos,crop=1920:1080:(iw-1920)/2:{top * 1080 * z:.0f},setsar=1,{NORM}"
            run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{src_of(x):.3f}", "-i", str(PRJ / "work" / "recording.mp4"), "-vf", vf, *ENC, "-frames:v", str(frames(x, y)), str(sp)])
            subs.append(sp)
        lst = CL / f"{i:03d}.txt"
        lst.write_text("".join(f"file '{s.as_posix()}'\n" for s in subs), encoding="utf-8")
        run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
    return out


def words():
    sys.path.insert(0, "C:/Users/pthao/.claude/plugins/cache/edit-video-youtube-reaction/edit-video-youtube-reaction/b694db0e4ef6/skills/edit-video-youtube-reaction/pipeline")
    from reactforge.panel import timed_words_for, normalize
    from reactforge.common import read_json
    plan = [x for x in read_json(PRJ / "work" / "plan.json") if x["id"] == "t01"][0]
    al = {x["id"]: x for x in read_json(PRJ / "work" / "align.json")}["t01"]
    ws = timed_words_for(plan, read_json(PRJ / "work" / "words.json"), al)
    return [w for w in ws if w["s"] < END_VOICE], normalize


def keys_layer():
    ws, norm = words()
    wn = [norm(w["w"]) for w in ws]
    covered = [(a, b) for a, b, k, _ in EDL if k in ("card", "slice", "black")]
    phrases, pos = [], 0
    for text, style in KEYS:
        toks = text.split()
        nt = [norm(t.strip("*")) for t in toks]
        hit = next(j for j in range(pos, len(wn) - len(nt) + 1) if wn[j:j + len(nt)] == nt)
        pos = hit + len(nt)
        s, e = ws[hit]["s"], ws[hit + len(nt) - 1]["e"] + 0.45
        under = [b for a, b in covered if a - 0.05 <= s < b]
        if under and e > under[0] + 0.5:
            s = under[0] + 0.02                      # card still up: start as it leaves
        elif under:
            print("  skip (under a card):", text); continue
        nxt = [a for a, b in covered if a > s]
        e = min(e, min(nxt) - 0.03) if nxt else e
        phrases.append({"s": round(s - 0.05, 3), "e": round(e, 3), "style": style,
                        "words": [{"w": ws[hit + k]["w"].strip(",.:"), "t": round(ws[hit + k]["s"] - 0.05, 3), "hl": toks[k].startswith("*")} for k in range(len(nt))]})
    for p, q in zip(phrases, phrases[1:]):        # one phrase on screen at a time
        p["e"] = round(min(p["e"], q["s"] - 0.04), 3)
    props = {"width": 1920, "height": 1080, "fps": FPS, "total": TOTAL, "phrases": phrases, "overs": []}
    pj = W / "keys_v2.props.json"; pj.write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")
    out = W / "keys_v2.webm"
    run(f'npx remotion render Keys "{out}" "--props={pj}" --log=error --codec=vp8 --image-format=png --pixel-format=yuva420p', cwd=str(MOTION))
    return out, phrases


def audio():
    voice = W / "voice.wav"            # written by build.py: final.mp4 0-44.85 s, padded to TOTAL
    music = W / "music_v2.wav"
    # music from MUSIC_OFF; fade in 0.4 s; hard stop (40 ms fade) at the end of the last word
    run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{MUSIC_OFF:.3f}", "-t", f"{END_VOICE - 0.07:.3f}", "-i", str(MUSIC), "-ac", "2", "-ar", "48000",
         "-af", f"afade=t=in:d=0.4,afade=t=out:st={END_VOICE - 0.11:.3f}:d=0.04,apad=whole_dur={TOTAL}", str(music)])
    ins = ["-i", str(voice), "-i", str(music)]
    ch, lab = [], []
    for k, (t, name, peak, gain, rule, note) in enumerate(SFX_PLAN):
        ins += ["-i", str(SFX / f"{name}.wav")]
        d = int(round(max(0.0, t - peak) * 1000))
        ch.append(f"[{k + 2}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={gain}dB,adelay={d}|{d}[s{k}]")
        lab.append(f"[s{k}]")
    # music sits ~14 dB under the voice and is pushed down a further few dB while words are spoken
    # the quiet build of the track plays almost as is (-2 dB); after the drop it comes down 15 dB, so both
    # sit ~12-15 dB under the voice and the drop still hits by density, not by loudness
    gain = f"volume=volume='if(lt(t,{DROP_AT - 0.05}),0.794,0.178)':eval=frame"
    fc = (f"[0:a]asplit=2[v][vsc];[1:a]{gain}[m];[m][vsc]sidechaincompress=threshold=0.05:ratio=2.5:attack=20:release=400:makeup=1[md];"
          + ";".join(ch) + f";[v][md]{''.join(lab)}amix=inputs={len(lab) + 2}:normalize=0:duration=first,alimiter=limit=0.95[out]")
    mix = W / "mix_v2.wav"
    run(["ffmpeg", "-loglevel", "error", "-y", *ins, "-filter_complex", fc, "-map", "[out]", "-t", f"{TOTAL}", str(mix)])
    return mix


def main():
    outs = [make_clip(i, *e) for i, e in enumerate(EDL)]
    lst = W / "concat_v2.txt"
    lst.write_text("".join(f"file '{o.as_posix()}'\n" for o in outs), encoding="utf-8")
    base = W / "video_v2.mp4"
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(base)])
    keys, phrases = keys_layer()
    mix = audio()
    out = PRJ / "out" / "intro_test_matchcut_v2.mp4"
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(base), "-c:v", "libvpx", "-i", str(keys), "-i", str(mix),
         # concat -c copy leaves slightly uneven timestamps; renumber every frame or overlay drops one at a join
         "-filter_complex", "[0:v]setpts=N/30/TB[b];[1:v]setpts=N/30/TB[k];[b][k]overlay=0:0:eof_action=pass,format=yuv420p[v]",
         "-map", "[v]", "-map", "2:a", "-r", "30",
         "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-c:a", "aac", "-b:a", "192k", "-t", f"{TOTAL}", str(out)])
    (W / "edl_v2.json").write_text(json.dumps({"music_offset": MUSIC_OFF, "edl": EDL, "keys": phrases, "sfx": SFX_PLAN}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("OK", out)


if __name__ == "__main__":
    main()
