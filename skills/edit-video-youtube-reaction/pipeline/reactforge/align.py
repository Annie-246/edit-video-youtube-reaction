"""Transcribe the presenter recording (faster-whisper, word timestamps), align it to the script's
talk items, and mark the stumbles to cut (false starts, retakes, long pauses)."""
from __future__ import annotations
import difflib, os, re, subprocess, unicodedata
from pathlib import Path
from .common import load_project, read_json, write_json, run, ffprobe_duration

LEAD, TAIL = 0.30, 0.40
# stumble removal
MIN_CUT = 0.45      # an unmatched run shorter than this is left alone (breath, a stray syllable)
MAX_GAP = 1.0       # silence longer than this between two kept words is shortened…
GAP_KEEP = 0.40     # …to this much
HIT_RATIO = 0.5     # share of the run's words that also appear nearby in the script → it was a retake
MIN_KEEP = 1.0      # a kept sliver shorter than this between two cuts is dropped too


CANONICAL_TOKENS = {
    "thoc": "token", "cun": "token", "thoccun": "token", "thoccan": "token", "thoccon": "token",
    "thoccen": "token", "thoccul": "token", "thoccn": "token", "toccuong": "token",
    "clot": "claude", "cloth": "claude", "cloud": "claude",
    "cach": "cache",
    "sonet": "sonnet", "sonett": "sonnet",
    "offput": "opus",
    "contach": "context",
}


def normalize(tok: str) -> str:
    t = unicodedata.normalize("NFC", tok.lower())
    t = re.sub(r"[^\w]+", "", t, flags=re.UNICODE)
    return CANONICAL_TOKENS.get(t, t)



def transcribe(audio: Path, model_name: str, language: str, beam_size: int = 2) -> list[dict]:
    from faster_whisper import WhisperModel
    device = os.environ.get("REACTFORGE_WHISPER_DEVICE", "cpu")
    threads = int(os.environ.get("REACTFORGE_WHISPER_THREADS", os.cpu_count() or 4))
    compute_type = "float16" if device == "cuda" else "int8"
    model = WhisperModel(model_name, device=device, compute_type=compute_type, cpu_threads=threads)
    # vad_filter=True let whisper swallow a false start into one 2.8s "word"; without it (and without
    # conditioning on previous text) both takes come out as words, which the retake detector needs.
    # beam_size=2 is 2.5x faster on CPU than beam_size=5 with comparable accuracy
    segs, _ = model.transcribe(str(audio), language=language, word_timestamps=True, vad_filter=False,
                               condition_on_previous_text=False, beam_size=beam_size)
    words = []
    for s in segs:
        for w in (s.words or []):
            tok = w.word.strip()
            if tok:
                words.append({"w": tok, "s": round(w.start, 3), "e": round(w.end, 3)})
    return words


def align_single(talks: list[dict], words: list[dict]) -> list[dict]:
    """One continuous recording: locate each talk item by fuzzy token alignment."""
    script_tokens, owner = [], []
    for ti, t in enumerate(talks):
        toks = [normalize(x) for x in t["text"].split()]
        toks = [x for x in toks if x]
        script_tokens += toks; owner += [ti] * len(toks)
    asr_tokens = [normalize(w["w"]) for w in words]
    sm = difflib.SequenceMatcher(None, script_tokens, asr_tokens, autojunk=False)
    matched: dict[int, list[int]] = {ti: [] for ti in range(len(talks))}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            matched[owner[a + k]].append(b + k)
    result, prev_end = [], 0.0
    for ti, t in enumerate(talks):
        idx = sorted(matched[ti]); n_script = owner.count(ti)
        if not idx:
            result.append({"id": t["id"], "start": None, "end": None, "coverage": 0.0, "asr": "", "warn": "KHÔNG tìm thấy đoạn này trong bản ghi"}); continue
        # drop stray matches far from the bulk (median-based)
        mid = idx[len(idx) // 2]
        idx = [i for i in idx if abs(i - mid) <= max(60, n_script * 2)]
        s = max(prev_end, words[idx[0]]["s"] - LEAD)
        e = words[idx[-1]]["e"] + TAIL
        cov = round(len(idx) / max(1, n_script), 2)
        asr = " ".join(w["w"] for w in words[idx[0]: idx[-1] + 1])
        warn = "" if cov >= 0.5 else f"khớp thấp ({cov:.0%}) — kiểm tra lại đoạn này"
        result.append({"id": t["id"], "start": round(s, 3), "end": round(e, 3), "coverage": cov, "asr": asr, "warn": warn})
        prev_end = e
    return result


RETAKE_PASSES = ((4, 80), (3, 12))   # (n-gram, max words ahead): long restarts, then short false starts


def retake_cuts(aw: list[dict], an: list[str], sw: list[str]) -> list[dict]:
    """The presenter restarted a sentence: the same n-word run shows up again a little later.
    Keep the LAST take (that is the one editors keep), cut from the earlier take's start to the
    later take's start. Runs that repeat inside the script itself (rhetorical repeats) are left alone.
    If the words just before the earlier take are a partial prefix of it ("Vào… Vào tháng 7"),
    they belong to the same false start and go too."""
    cuts = []
    script = " ".join(sw)
    for n, span in RETAKE_PASSES:
        i = 0
        while i < len(aw) - n:
            g = an[i:i + n]
            if any(not t for t in g) or script.count(" ".join(g)) >= 2:
                i += 1; continue
            found = None
            for j in range(i + n, min(len(aw) - n + 1, i + span)):
                if an[j:j + n] == g:
                    found = j; break
            if found is None:
                i += 1; continue
            if span <= 12 and aw[found]["s"] - aw[found - 1]["e"] < 0.25:
                i += 1; continue  # short pass: a real false start restarts after a pause; "ông ấy nói… ông ấy nói" is rhetoric
            i0 = i
            for k in (3, 2, 1):  # look back over a partial prefix of the same start
                if i0 - k >= 0 and an[i0 - k:i0] == g[:k]:
                    i0 -= k; break
            cs = (aw[i0 - 1]["e"] + aw[i0]["s"]) / 2 if i0 > 0 else max(0.0, aw[i0]["s"] - 0.15)
            ce = (aw[found - 1]["e"] + aw[found]["s"]) / 2
            cuts.append({"s": round(cs, 3), "e": round(ce, 3), "why": "đọc lại", "text": " ".join(w["w"] for w in aw[i0:found])})
            i = found
    return cuts


SIL_DB, SIL_MIN = -35, 0.7
MUMBLE_GAP = 0.7    # no transcribed word for this long while the audio is NOT silent → mumble / false start


def detect_silences(wav: Path, out: Path, min_dur: float = SIL_MIN) -> list[list[float]]:
    """Silences straight from the audio (ffmpeg silencedetect) — whisper word times drift too much."""
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(wav), "-af", f"silencedetect=noise={SIL_DB}dB:d={min_dur}", "-f", "null", "-"],
                       capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    sil = [[round(a, 3), round(b, 3)] for a, b in zip(starts, ends) if b > a]
    write_json(out, sil)
    return sil


LONG_WORD, FINE_SIL = 1.0, 0.3
_small = None


def _small_model():
    global _small
    if _small is None:
        from faster_whisper import WhisperModel
        device = os.environ.get("REACTFORGE_WHISPER_DEVICE", "cpu")
        threads = int(os.environ.get("REACTFORGE_WHISPER_THREADS", os.cpu_count() or 4))
        compute_type = "float16" if device == "cuda" else "int8"
        refine_m = os.environ.get("REACTFORGE_REFINE_MODEL", "medium")
        _small = WhisperModel(refine_m, device=device, compute_type=compute_type, cpu_threads=threads)
    return _small


def _transcribe_window(wav: Path, a: float, b: float) -> list[dict]:
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp = f.name
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", str(wav), "-c", "copy", tmp])
    segs, _ = _small_model().transcribe(tmp, language="vi", word_timestamps=True, vad_filter=False, condition_on_previous_text=False,
                                        beam_size=1, temperature=0.0, compression_ratio_threshold=None, log_prob_threshold=None, no_speech_threshold=None)
    out = []
    for sg in segs:
        for w in (sg.words or []):
            if w.word.strip():
                out.append({"w": w.word.strip(), "s": round(min(b, max(a, float(w.start) + a)), 3), "e": round(min(b, max(a, float(w.end) + a)), 3), "zoom": True})
    Path(tmp).unlink(missing_ok=True)
    return out


def refine_words(words: list[dict], wav: Path, silences_fine: list[list[float]], vocab: set[str] | None = None,
                 lo: float = 0.0, hi: float = 1e9) -> tuple[list[dict], list[dict]]:
    """Whisper drops disfluent repeats: a restarted sentence comes back as ONE word stretched over
    4-5 s (or as a non-silent gap). Re-listen to those spans in short chunks split at brief
    silences — chunk edges are exact, and a chunk usually holds one take, so nothing collapses."""
    out, regions = [], []
    n = len(words)
    for i, w in enumerate(words):
        nxt = words[i + 1] if i + 1 < n else None
        long_word = (w["e"] - w["s"]) > LONG_WORD
        gap = (nxt["s"] - w["e"]) if nxt else 0.0
        silent = sum(max(0.0, min(b, nxt["s"]) - max(a, w["e"])) for a, b in silences_fine) if nxt else 0.0
        if not (lo <= w["s"] <= hi) or (not long_word and not (gap > 0.7 and gap - silent >= 0.5)):
            out.append(w); continue
        a = (w["s"] + 0.35) if long_word else w["e"]
        b = (nxt["s"] - 0.05) if nxt else w["e"]
        if b - a < 0.4:
            out.append(w); continue
        # chunk the span at brief silences
        edges = [a] + [round((x + y) / 2, 3) for x, y in silences_fine if a < x and y < b] + [b]
        chunks = [(edges[k], edges[k + 1]) for k in range(len(edges) - 1) if edges[k + 1] - edges[k] >= 0.35]
        heard = []
        for ca, cb in chunks:
            if cb - ca < 0.5:  # a breath, not speech
                continue
            got = _transcribe_window(wav, ca, cb)
            toks = [normalize(x["w"]) for x in got if normalize(x["w"])]
            hit = (sum(1 for t in toks if t in vocab) / len(toks)) if (vocab and toks) else 1.0
            if not toks or hit < 0.5:  # whisper hallucinates on short noisy chunks ("Hãy subscribe cho kênh…") → unknown speech
                heard.append({"w": "[tiếng không rõ]", "s": round(ca, 3), "e": round(cb, 3), "zoom": True, "unk": True})
            else:
                heard += got
        if long_word:
            out.append({"w": w["w"], "s": w["s"], "e": round(min(w["e"], a), 3)})  # the word itself, trimmed to a normal length
        else:
            out.append(w)
        out += heard
        regions.append({"s": a, "e": b, "chunks": len(chunks), "heard": " ".join(x["w"] for x in heard)})
    return out, regions


def stumble_cuts(text: str, words: list[dict], start: float, end: float, silences: list[list[float]] | None = None,
                 judge_cuts: list[dict] | None = None) -> tuple[list[list[float]], list[dict]]:
    """Return (keep intervals, cuts) for one talk.

    A cut is (a) a run of recognised words that do not align to the script but whose words
    appear nearby IN the script → the presenter restarted a sentence; the aligner already kept
    the later, complete take, so the earlier attempt goes; or (b) a silence longer than MAX_GAP.
    Cut edges sit halfway between the neighbouring words so the cut lands in silence.
    """
    sw = [normalize(w) for w in text.split() if normalize(w)]
    aw = [w for w in words if w["s"] >= start - 0.05 and w["e"] <= end + 0.05]
    an = [normalize(w["w"]) for w in aw]
    cuts: list[dict] = []
    if aw:
        rcuts = judge_cuts if judge_cuts is not None else retake_cuts(aw, an, sw)  # Claude's verdicts win when available
        cuts += rcuts
        # everything below looks at the LAST takes only, so the script aligns to what stays in
        aw = [w for w in aw if not any(c["s"] <= (w["s"] + w["e"]) / 2 <= c["e"] for c in rcuts)]
        an = [normalize(w["w"]) for w in aw]
    if aw:
        sil = [x for x in (silences or []) if x[0] < end and x[1] > start]
        # long silences (audio-measured) → shorten to GAP_KEEP
        for a, b in sil:
            if b - a > MAX_GAP:
                cuts.append({"s": round(max(start, a) + GAP_KEEP / 2, 3), "e": round(min(end, b) - GAP_KEEP / 2, 3), "why": "im lặng", "text": f"{b - a:.1f}s"})
        # gap between two words that is NOT silent → whisper heard something it would not write (mumble, false start)
        for k in range(len(aw) - 1):
            g0, g1 = aw[k]["e"], aw[k + 1]["s"]
            if g1 - g0 < MUMBLE_GAP:
                continue
            silent = sum(max(0.0, min(b, g1) - max(a, g0)) for a, b in sil)
            if (g1 - g0) - silent >= 0.5:
                cuts.append({"s": round(g0 + 0.12, 3), "e": round(g1 - 0.12, 3), "why": "lẩm bẩm", "text": f"{g1 - g0:.1f}s sau '{aw[k]['w']}'"})
        # dead air before the first / after the last word
        if aw[0]["s"] - start > LEAD + 0.3:
            cuts.append({"s": start, "e": round(aw[0]["s"] - LEAD, 3), "why": "im lặng đầu", "text": ""})
        if end - aw[-1]["e"] > TAIL + 0.3:
            cuts.append({"s": round(aw[-1]["e"] + TAIL, 3), "e": end, "why": "im lặng cuối", "text": ""})
    # merge + complement
    cuts = [c for c in cuts if c["e"] - c["s"] >= 0.15]  # a silence rule can produce an inverted range at the edges
    cuts.sort(key=lambda c: c["s"])
    merged: list[dict] = []
    for c in cuts:
        if merged and c["s"] <= merged[-1]["e"]:
            merged[-1]["e"] = max(merged[-1]["e"], c["e"]); merged[-1]["text"] = (merged[-1]["text"] + " | " + c["text"]).strip(" |")
        else:
            merged.append(dict(c))
    keep: list[list[float]] = []
    cur = start
    for c in merged:
        if c["s"] - cur >= MIN_KEEP:
            keep.append([round(cur, 3), round(c["s"], 3)])
        cur = max(cur, c["e"])
    if end - cur >= MIN_KEEP:
        keep.append([round(cur, 3), round(end, 3)])
    if not keep:
        keep = [[start, end]]
    return keep, merged


def main(project: Path, force: bool = False) -> None:
    cfg = load_project(project)
    plan = read_json(project / "work" / "plan.json")
    talks = [i for i in plan if i["type"] == "talk"]
    rec_cfg = cfg["recording"]
    files = [project / f for f in rec_cfg.get("files", [])]
    if not files:
        files = sorted((project / "recording").glob("*.mp4")) + sorted((project / "recording").glob("*.mov"))
    if not files:
        raise SystemExit("Không thấy file ghi hình trong recording/ (mp4/mov)")
    work = project / "work"; work.mkdir(exist_ok=True)
    rec = work / "recording.mp4"
    if force or not rec.exists():
        if len(files) == 1:
            run(["ffmpeg", "-v", "error", "-y", "-i", str(files[0]), "-c", "copy", "-movflags", "+faststart", str(rec)])
        else:
            lst = work / "rec_list.txt"
            lst.write_text("".join(f"file '{f.resolve()}'\n" for f in files), encoding="utf-8")
            fps, w, h = cfg["output"]["fps"], cfg["output"]["width"], cfg["output"]["height"]
            run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,fps={fps}",
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(rec)])
        print(f"recording → {rec} ({ffprobe_duration(rec):.1f}s)")
    wav = work / "recording.wav"
    if force or not wav.exists():
        run(["ffmpeg", "-v", "error", "-y", "-i", str(rec), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav)])
    words_p = work / "words.json"
    if force or not words_p.exists():
        beam = int(cfg.get("whisper", {}).get("beam_size", 2))
        print(f"whisper {cfg['whisper']['model']} ({cfg['whisper']['language']}, beam={beam}) đang nghe {ffprobe_duration(wav):.0f}s …")
        words = transcribe(wav, cfg["whisper"]["model"], cfg["whisper"]["language"], beam_size=beam)
        write_json(words_p, words)
    words = read_json(words_p)
    print(f"{len(words)} từ nhận dạng")
    res = align_single(talks, words)
    # re-listen to the spans whisper collapsed (restarted sentences hide inside 4-5 s "words")
    if cfg.get("refine", True) and not any(w.get("zoom") for w in words):
        fine_p = work / "silences_fine.json"
        fine = read_json(fine_p) if fine_p.exists() and not force else detect_silences(wav, fine_p, FINE_SIL)
        vocab = {normalize(x) for t in talks for x in t["text"].split() if normalize(x)}
        found = [r for r in res if r["start"] is not None]
        lo = min(r["start"] for r in found) - 1 if found else 0.0
        hi = max(r["end"] for r in found) + 1 if found else 0.0
        write_json(work / "words_raw.json", words)
        words, regions = refine_words(words, wav, fine, vocab, lo, hi)
        write_json(words_p, words)
        print(f"nghe lại {len(regions)} vùng whisper nuốt chữ → {len(words)} từ")
        for rg in regions:
            print(f"  {rg['s']:.1f}–{rg['e']:.1f}s: {rg['heard'][:110]}")
        res = align_single(talks, words)
    clean = cfg.get("clean_cuts", True)
    sil_p = work / "silences.json"
    silences = read_json(sil_p) if sil_p.exists() and not force else detect_silences(wav, sil_p)
    from .common import load_env
    load_env(project)
    has_gemini = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    has_claude = bool(os.environ.get("ANTHROPIC_API_KEY"))
    use_judge = clean and cfg.get("cut_judge", "auto") != "off" and (has_gemini or has_claude)
    if clean:
        engine_label = "Gemini" if has_gemini else ("Claude" if has_claude else "AI")
        print("cắt vấp bằng:", f"{engine_label} AI" if use_judge else "thuật toán n-gram")
    for r, t in zip(res, talks):
        if r["start"] is None:
            continue
        jc, review = None, []
        judge_p = work / "judge" / f"{r['id']}.json"
        if judge_p.exists() and not force:
            from . import judge
            jr = read_json(judge_p)
            aw = [w for w in words if w["s"] >= r["start"] - 0.05 and w["e"] <= r["end"] + 0.05]
            jc = judge.cuts_to_times(jr.get("cuts", []), aw, r["start"], r["end"])
            review = jr.get("review", [])
            print(f"  {r['id']}: Antigravity đã chấm sẵn ({len(jc)} chỗ cắt)")
        elif use_judge:
            from . import judge
            aw = [w for w in words if w["s"] >= r["start"] - 0.05 and w["e"] <= r["end"] + 0.05]
            try:
                jr = judge.judge_talk(project, t["text"], aw, silences)
                write_json(judge_p, jr)
                jc = judge.cuts_to_times(jr["cuts"], aw, r["start"], r["end"]); review = jr.get("review", [])
                print(f"  {r['id']}: AI đánh dấu {len(jc)} chỗ cắt")
            except Exception as e:
                print(f"  ⚠ {r['id']}: AI lỗi ({type(e).__name__}: {str(e)[:120]}) → dùng thuật toán n-gram")
        r["review"] = review; r["engine"] = "claude" if jc is not None else "ngram"
        if clean:
            keep, cuts = stumble_cuts(t["text"], words, r["start"], r["end"], silences, jc)
        else:
            keep, cuts = [[r["start"], r["end"]]], []
        r["keep"] = keep; r["cuts"] = cuts
        r["kept"] = round(sum(e - s for s, e in keep), 3)
    write_json(work / "align.json", res)
    lines = ["# Báo cáo khớp lời\n", "| ID | Bắt đầu | Kết thúc | Dài | Giữ lại | Cắt | Khớp | Cảnh báo |", "|---|---|---|---|---|---|---|---|"]
    for r in res:
        if r["start"] is None:
            lines.append(f"| {r['id']} | — | — | — | — | — | 0% | {r['warn']} |")
        else:
            d = r["end"] - r["start"]
            lines.append(f"| {r['id']} | {r['start']:.1f}s | {r['end']:.1f}s | {d:.1f}s | {r['kept']:.1f}s | {len(r['cuts'])} chỗ, {d - r['kept']:.1f}s | {r['coverage']:.0%} | {r['warn']} |")
    lines.append("\n## Chỗ đã cắt (vấp / im lặng) — kiểm lại nếu thấy cắt nhầm\n")
    for r in res:
        for c in r.get("cuts", []):
            lines.append(f"- {r['id']} {c['s']:.1f}–{c['e']:.1f}s ({c['e']-c['s']:.1f}s, {c['why']}): {c['text'][:160]}")
        for n in r.get("review", []):
            lines.append(f"- {r['id']} 👀 Claude lưu ý: {n}")
    lines.append("\n## Lời nhận dạng từng đoạn (đối chiếu với kịch bản)\n")
    for r, t in zip(res, talks):
        lines.append(f"### {r['id']} — {t['slide']['keyword']}\n\n{r['asr']}\n")
    (work / "align_report.md").write_text("\n".join(lines), encoding="utf-8")
    for l in lines[1:len(res) + 3]:
        print(l)
    print(f"→ {work/'align_report.md'}")
    try:
        from . import captions
        captions.main(project)
    except Exception as e:  # captions are optional
        print("captions bỏ qua:", e)
