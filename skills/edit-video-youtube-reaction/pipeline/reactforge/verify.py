"""Listen to the RENDERED talk segments and cut what the first pass missed.

The first pass judges the raw recording. Anything it gets wrong survives into the cut — usually a
repeated phrase at a join. This pass closes the loop: transcribe each rendered segment (re-listening
to the spans whisper collapses, same as `align.refine_words`), flag repeated n-grams that the script
does not repeat on purpose, let Claude decide which are real, then subtract those spans from the
segment's keep list and re-render. Repeat until a round finds nothing.
"""
from __future__ import annotations
import json, os
from pathlib import Path

from .align import LONG_WORD, MIN_KEEP, detect_silences, normalize, refine_words, transcribe
from .common import load_project, read_json, run, write_json

MAX_NEAR = 14          # a restart repeats itself within this many words; further apart is normal prose
MIN_REPEAT_GAP = 0.12  # ignore "repeats" that are really one word split by the recogniser
VERIFY_MODEL = os.environ.get("REACTFORGE_VERIFY_MODEL", os.environ.get("REACTFORGE_JUDGE_MODEL", "claude-opus-5"))


# ---------- timeline mapping ----------

def out_to_src(keep: list[list[float]], a: float, b: float) -> list[list[float]]:
    """Interval on the cut timeline → the intervals it covers on the source timeline."""
    res, acc = [], 0.0
    for s, e in keep:
        d = e - s
        lo, hi = acc, acc + d
        if b > lo and a < hi:
            res.append([round(s + max(0.0, a - lo), 3), round(s + min(d, b - lo), 3)])
        acc = hi
    return res


def subtract(keep: list[list[float]], cuts: list[list[float]]) -> list[list[float]]:
    out = []
    for s, e in keep:
        segs = [[s, e]]
        for cs, ce in cuts:
            nxt = []
            for a, b in segs:
                if ce <= a or cs >= b:
                    nxt.append([a, b]); continue
                if cs > a:
                    nxt.append([a, cs])
                if ce < b:
                    nxt.append([ce, b])
            segs = nxt
        out += [[round(a, 3), round(b, 3)] for a, b in segs if b - a >= MIN_KEEP]
    return out


# ---------- listening to a rendered segment ----------

def listen(seg: Path, work: Path, sid: str, vocab: set[str], model: str) -> list[dict]:
    wav = work / "verify" / f"{sid}.wav"
    wav.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(seg), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav)])
    words = transcribe(wav, model, "vi")
    fine = detect_silences(wav, work / "verify" / f"{sid}.sil.json", 0.3)
    words, _ = refine_words(words, wav, fine, vocab)
    return words


def script_ngrams(text: str, n: int) -> set[tuple]:
    t = [normalize(x) for x in text.split() if normalize(x)]
    return {tuple(t[i:i + n]) for i in range(len(t) - n + 1)}


def find_repeats(words: list[dict], text: str) -> list[dict]:
    """Repeated n-grams close together that the script does not itself repeat."""
    an = [normalize(w["w"]) for w in words]
    hits, taken = [], set()
    for n in (5, 4, 3, 2):
        grams = script_ngrams(text, n)
        # a phrase the script says twice is rhetoric, not a stumble
        seq = [normalize(x) for x in text.split() if normalize(x)]
        counts = {}
        for i in range(len(seq) - n + 1):
            g = tuple(seq[i:i + n]); counts[g] = counts.get(g, 0) + 1
        for i in range(len(an) - n):
            g = tuple(an[i:i + n])
            if any(not x for x in g) or counts.get(g, 0) >= 2:
                continue
            for j in range(i + n, min(len(an) - n + 1, i + n + MAX_NEAR)):
                if tuple(an[j:j + n]) != g:
                    continue
                if words[j]["s"] - words[i + n - 1]["e"] < MIN_REPEAT_GAP and n <= 2:
                    break
                if any(k in taken for k in range(i, j + n)):
                    break
                hits.append({"n": n, "i": i, "j": j,
                             "text": " ".join(w["w"] for w in words[i:j + n]),
                             "t": round(words[i]["s"], 1), "in_script": tuple(g) in grams})
                taken.update(range(i, j + n))
                break
    return sorted(hits, key=lambda h: h["i"])


SYSTEM = """Bạn là người dựng video đang KIỂM TRA LẠI một đoạn talking-head tiếng Việt ĐÃ CẮT một lần.
Đầu vào: KỊCH BẢN người dẫn định đọc, LỜI THẬT nghe lại từ chính file đã dựng (mỗi từ có số thứ tự và mốc giây), và DANH SÁCH NGHI NGỜ (những cụm bị lặp mà máy dò được).
Nhiệm vụ: chỉ ra những chỗ CÒN SÓT phải cắt thêm để lời nghe liền mạch:
- Cụm từ bị lặp do lần cắt trước cắt chưa sạch (thường ở mối nối): giữ LẦN CUỐI, cắt lần trước.
- Nửa câu thừa dính lại ở mối nối ("với... với doanh thu", "một công ty... một công ty nắm").
- Từ đệm, tiếng không ra chữ còn sót.
KHÔNG cắt: lặp có chủ ý có trong kịch bản; nói lệch chữ nhưng trôi chảy; cách đọc số.
QUAN TRỌNG: đoạn này đã được cắt rồi, phần lớn nghi ngờ có thể là báo động giả. Chỉ cắt khi thật sự nghe ra lặp. Nếu không có gì phải cắt, trả về danh sách rỗng.
Ranh giới cắt phải rơi giữa hai từ. Trả về DUY NHẤT JSON:
{"cuts":[{"from":<số thứ tự từ đầu>,"to":<số thứ tự từ cuối, bao gồm>,"why":"lặp|thừa mối nối|đệm","note":"≤12 từ"}],"review":["ghi chú nếu có chỗ đáng ngờ mà bạn không dám cắt"]}"""


def ask_claude(project: Path, script_text: str, words: list[dict], hits: list[dict]) -> dict:
    from .judge import ask
    lines = []
    for i, w in enumerate(words):
        if i > 0 and w["s"] - words[i - 1]["e"] >= 0.4:
            lines.append(f"   [nghỉ {w['s'] - words[i - 1]['e']:.1f}s]")
        lines.append(f"#{i} [{w['s']:.1f}] {w['w']}")
    sus = "\n".join(f"- #{h['i']}→#{h['j']} ({h['t']}s, lặp {h['n']} từ): {h['text'][:120]}" for h in hits) or "(máy không dò được cụm lặp nào — vẫn đọc kỹ)"
    user = f"KỊCH BẢN:\n{script_text}\n\nLỜI TRONG FILE ĐÃ DỰNG:\n" + "\n".join(lines) + f"\n\nDANH SÁCH NGHI NGỜ:\n{sus}"
    text, usage = ask(project, SYSTEM, user)
    import re
    m = re.search(r"\{.*\}", text, re.S)
    data = json.loads(m.group(0) if m else text)
    return {"cuts": data.get("cuts", []), "review": data.get("review", []), "usage": usage}


def cuts_on_out_timeline(cuts: list[dict], words: list[dict]) -> list[list[float]]:
    out, n = [], len(words)
    for c in cuts:
        try:
            i, j = int(c["from"]), int(c["to"])
        except (KeyError, ValueError, TypeError):
            continue
        if i < 0 or j >= n or j < i:
            continue
        a = (words[i - 1]["e"] + words[i]["s"]) / 2 if i > 0 else max(0.0, words[i]["s"] - 0.15)
        b = (words[j]["e"] + words[j + 1]["s"]) / 2 if j + 1 < n else words[j]["e"] + 0.15
        out.append([round(a, 3), round(b, 3)])
    return out


# ---------- one round ----------

def check_round(project: Path, rnd: int, model: str, only: str | None = None) -> tuple[list[str], list[str]]:
    """Returns (talk ids changed, report lines)."""
    cfg = load_project(project)
    work = project / "work"
    plan = read_json(work / "plan.json")
    align = read_json(work / "align.json")
    by_id = {a["id"]: a for a in align}
    talks = {i["id"]: i for i in plan if i["type"] == "talk"}
    changed, lines = [], []
    for tid, item in talks.items():
        if only and tid != only:
            continue
        seg = work / "seg" / f"{tid}.mov"
        al = by_id.get(tid)
        if not seg.exists() or not al or al.get("start") is None:
            continue
        vocab = {normalize(x) for x in item["text"].split() if normalize(x)}
        words = listen(seg, work, tid, vocab, model)
        write_json(work / "verify" / f"{tid}.words.json", words)
        hits = find_repeats(words, item["text"])
        if not hits:
            lines.append(f"- {tid}: sạch ({len(words)} từ)")
            continue
        try:
            v = ask_claude(project, item["text"], words, hits)
        except Exception as e:
            lines.append(f"- {tid}: ⚠ Claude lỗi ({type(e).__name__}) — {len(hits)} nghi ngờ chưa xử lý")
            continue
        write_json(work / "verify" / f"{tid}.judge.json", {"hits": hits, **v})
        cuts_out = cuts_on_out_timeline(v["cuts"], words)
        if not cuts_out:
            lines.append(f"- {tid}: {len(hits)} nghi ngờ → Claude kết luận không phải lặp, giữ nguyên")
            for n in v.get("review", []):
                lines.append(f"  👀 {n}")
            continue
        keep = al.get("keep") or [[al["start"], al["end"]]]
        src_cuts = [x for a, b in cuts_out for x in out_to_src(keep, a, b)]
        new_keep = subtract(keep, src_cuts)
        removed = sum(e - s for s, e in keep) - sum(e - s for s, e in new_keep)
        al["keep"] = new_keep
        al["kept"] = round(sum(e - s for s, e in new_keep), 3)
        al.setdefault("cuts", []).extend([{"s": s, "e": e, "why": f"vòng {rnd}: {c.get('why', 'lặp')}",
                                           "text": (c.get("note") or "")} for (s, e), c in zip(src_cuts, v["cuts"])])
        al["verify_round"] = rnd
        changed.append(tid)
        lines.append(f"- {tid}: cắt thêm {len(cuts_out)} chỗ, bỏ {removed:.1f}s")
        for (a, b), c in zip(cuts_out, v["cuts"]):
            words_txt = " ".join(w["w"] for w in words[int(c["from"]):int(c["to"]) + 1])[:110]
            lines.append(f"    {a:.1f}–{b:.1f}s ({c.get('why', '')}): {words_txt}")
        for n in v.get("review", []):
            lines.append(f"  👀 {n}")
    if changed:
        write_json(work / "align.json", align)
    return changed, lines


def main(project: Path, rounds: int = 2, only: str | None = None, model: str = "medium", rebuild: bool = True) -> None:
    from . import captions, panel, render
    work = project / "work"
    report = ["# Báo cáo kiểm tra sau khi dựng\n"]
    for rnd in range(1, rounds + 1):
        print(f"── vòng kiểm tra {rnd}")
        changed, lines = check_round(project, rnd, model, only)
        report.append(f"\n## Vòng {rnd}\n")
        report += lines
        for l in lines:
            print(" ", l)
        if not changed:
            print("  → không còn chỗ nào phải cắt")
            report.append("\n→ không còn chỗ nào phải cắt.")
            break
        if not rebuild:
            break
        print(f"  → dựng lại {len(changed)} đoạn: {', '.join(changed)}")
        captions.main(project)
        for tid in changed:
            panel.main(project, only=tid, force=True)
            render.main(project, only=tid)
    if rebuild:
        render.concat_only(project)
    (work / "verify_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"→ {work / 'verify_report.md'}")
