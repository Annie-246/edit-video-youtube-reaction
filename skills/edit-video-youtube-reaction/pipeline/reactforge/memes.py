"""Memes: find the moments, fetch the memes, keep them in a shared library, cut them in.

  1. spot   AI reads every talk and picks the few moments that earn a meme (punchline, twist,
            fail, shocking number…) → work/memes_auto.json (edit or empty it freely).
            Manual `MEME: @"câu neo" {"q":"surprised pikachu"}` lines in the script always count.
  2. fetch  library first (reuse), else a short meme clip found with yt-dlp, else an Imgflip
            template image. Everything downloaded lands in the meme library with a row in
            index.csv, so later videos reuse it.
  3. place  render.py cuts each meme in right after the sentence its anchor phrase belongs to:
            the voice pauses, the meme plays with its sound on black, no card.

Library: project.json "memes": {"library": "..."} > $REACTFORGE_MEME_LIB >
<workspace>/meme-library (the folder that holds projects/).
"""
from __future__ import annotations
import csv, datetime, json, os, re, subprocess, urllib.request
from pathlib import Path

from .common import load_project, read_json, run, write_json, ffprobe_duration

MOODS = ["shock", "laugh", "facepalm", "win", "fail", "awkward", "confused", "sad", "hype", "cringe"]
FIELDS = ["file", "mood", "name", "tags", "source", "duration", "green", "still", "audio", "added", "used_in"]
MAX_CLIP = 20.0     # longer search hits are compilations, not a meme
EVERY = 75.0        # about one meme per this many seconds of talk
STARTERS = {"và", "nhưng", "cũng", "còn", "thì", "đấy", "đây", "đó", "mình", "anh", "thế", "vì", "nên", "sau",
            "tiếp", "bây", "ok", "điều", "kết", "tất", "nghe", "cứ", "trong", "khi", "nếu", "vậy", "rồi"}

SPOT = """Bạn là editor video YouTube react tiếng Việt, chuyên chèn MEME đúng lúc để người xem bật cười và xem tiếp.
Đầu vào: lời người dẫn của từng đoạn (mã đoạn, rồi lời kèm mốc giây).
Chọn những khoảnh khắc ĐÁNG chèn meme: câu đùa / châm biếm, cú twist bất ngờ, thất bại / ngớ ngẩn, con số gây sốc, câu hỏi tu từ, khoảnh khắc "wow", sự bối rối, ăn mừng.
Quy tắc:
- Tối đa {n} meme cho cả video, hai meme cách nhau ít nhất 45 giây.
- KHÔNG chèn vào chỗ giải thích nghiêm túc cần tập trung, hướng dẫn từng bước, lời kêu gọi đăng ký / mua.
- Meme phải là meme quốc tế nổi tiếng, dễ nhận ra, tìm được trên YouTube (vd "surprised pikachu", "this is fine dog", "visible confusion", "stonks", "sad violin", "vine boom", "michael scott no", "shocked guy", "math lady", "success kid", "drake no yes", "coffin dance").
- "at" là 3–6 từ LIÊN TIẾP chép NGUYÊN VĂN từ lời của đoạn đó, nằm trong câu ngay trước chỗ chèn.
- "mode": "full" khi meme là khoảnh khắc chính, "part" khi chỉ là phản ứng nhỏ.
Trả về DUY NHẤT JSON: {{"memes":[{{"id":"t03","at":"...","q":"<tên meme tiếng Anh>","mood":"{moods}","secs":<1.2–3>,"mode":"full|part","why":"≤12 từ"}}]}}"""


# ---------- library ----------

def library(project: Path, cfg: dict) -> Path:
    p = (cfg.get("memes") or {}).get("library") or os.environ.get("REACTFORGE_MEME_LIB")
    if p:
        lib = Path(p)
    else:
        lib = (project.parent.parent if project.parent.name == "projects" else project.parent) / "meme-library"
    lib.mkdir(parents=True, exist_ok=True)
    return lib


def read_index(lib: Path) -> list[dict]:
    f = lib / "index.csv"
    if not f.exists():
        return []
    with f.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_index(lib: Path, rows: list[dict]) -> None:
    # utf-8-sig so Excel opens the Vietnamese text correctly
    with (lib / "index.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})


def _toks(s: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", s.lower()) if len(t) > 1 and t not in {"meme", "the", "and", "of", "a"}}


def lookup(rows: list[dict], q: str) -> dict | None:
    want = _toks(q)
    if not want:
        return None
    best, score = None, 0.0
    for r in rows:
        sc = len(want & _toks(r["name"] + " " + r["tags"])) / len(want)
        if sc > score:
            best, score = r, sc
    return best if score >= 0.6 else None


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:50] or "meme"


# ---------- fetch ----------

def _has_audio(p: Path) -> bool:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


def _is_green(p: Path, still: bool) -> bool:
    """A green-screen meme: over a quarter of a sample frame is near pure green."""
    ss = [] if still else ["-ss", f"{min(1.0, ffprobe_duration(p) / 3):.2f}"]
    r = subprocess.run(["ffmpeg", "-v", "error", *ss, "-i", str(p), "-frames:v", "1", "-vf", "scale=64:36", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True)
    px = r.stdout
    n = len(px) // 3
    if not n:
        return False
    g = sum(1 for i in range(n) if px[3 * i + 1] > 140 and px[3 * i] < 110 and px[3 * i + 2] < 110)
    return g / n > 0.25


def _from_youtube(q: str, dest: Path) -> tuple[Path, str] | None:
    r = subprocess.run(["yt-dlp", f"ytsearch10:{q} meme", "--flat-playlist", "--dump-json", "--no-warnings"],
                       capture_output=True, text=True, timeout=120)
    hits = []
    for line in r.stdout.splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        d = e.get("duration") or 0
        if 0 < d <= MAX_CLIP:
            title = (e.get("title") or "").lower()
            hits.append((len(_toks(q) & _toks(title)) * 3 - d / 5 + (2 if "green screen" in title else 0), e))
    if not hits:
        return None
    e = max(hits, key=lambda h: h[0])[1]
    url = e.get("url") or f"https://www.youtube.com/watch?v={e['id']}"
    out = dest.with_suffix(".mp4")
    run(["yt-dlp", "-q", "--no-playlist", "-f", "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b",
         "--merge-output-format", "mp4", "-o", str(out), url])
    return (out, url) if out.exists() else None


_IMGFLIP: list[dict] | None = None


def _from_imgflip(q: str, dest: Path) -> tuple[Path, str] | None:
    global _IMGFLIP
    if _IMGFLIP is None:
        with urllib.request.urlopen("https://api.imgflip.com/get_memes", timeout=30) as resp:
            _IMGFLIP = json.loads(resp.read().decode("utf-8"))["data"]["memes"]
    want = _toks(q)
    best = max(_IMGFLIP, key=lambda m: len(want & _toks(m["name"])), default=None)
    if not best or not want or len(want & _toks(best["name"])) / len(want) < 0.5:
        return None
    out = dest.with_suffix(Path(best["url"]).suffix or ".jpg")
    urllib.request.urlretrieve(best["url"], out)
    return out, best["url"]


def fetch(lib: Path, rows: list[dict], m: dict, project_name: str) -> dict | None:
    """Library row for this meme request, downloading it if the library has nothing close."""
    row = lookup(rows, m["q"])
    if row is None:
        mood = m.get("mood") if m.get("mood") in MOODS else "other"
        (lib / mood).mkdir(exist_ok=True)
        dest = lib / mood / _slug(m["q"])
        got = None
        for src in (_from_youtube, _from_imgflip):
            try:
                got = src(m["q"], dest)
            except Exception as e:
                print(f"   ⚠ {src.__name__[6:]}: {str(e)[:80]}")
            if got:
                break
        if not got:
            return None
        f, url = got
        still = f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".gif")
        row = {"file": str(f.relative_to(lib)).replace("\\", "/"), "mood": mood, "name": m["q"], "tags": m.get("why", ""),
               "source": url, "duration": "" if still else f"{ffprobe_duration(f):.1f}", "green": int(_is_green(f, still)),
               "still": int(still), "audio": int(not still and _has_audio(f)), "added": datetime.date.today().isoformat(), "used_in": ""}
        rows.append(row)
        print(f"   ⬇ {m['q']} → {row['file']}" + (" (nền xanh)" if row["green"] else ""))
    used = [x for x in row["used_in"].split(";") if x]
    if project_name not in used:
        row["used_in"] = ";".join(used + [project_name])
    return row


# ---------- spot ----------

def spot(project: Path, plan: list[dict], words: list[dict], align: dict) -> list[dict]:
    from .captions import timed_words_for
    from .judge import ask, _extract_json
    blocks, total = [], 0.0
    for it in plan:
        al = align.get(it["id"])
        if it["type"] != "talk" or not al or al.get("start") is None:
            continue
        ws = timed_words_for(it, words, al)
        total += al.get("kept") or (al["end"] - al["start"])
        lines = [f"[{ws[k]['s']:.0f}s] " + " ".join(w["w"] for w in ws[k:k + 12]) for k in range(0, len(ws), 12)]
        blocks.append(f"## {it['id']}\n" + "\n".join(lines))
    n = max(1, round(total / EVERY))
    text, _ = ask(project, SPOT.format(n=n, moods="|".join(MOODS)), "\n\n".join(blocks), max_tokens=3000)
    return _extract_json(text).get("memes", [])[:n]


# ---------- place (used by render) ----------

def place_memes(entries: list[dict], item: dict, words: list[dict], al: dict) -> list[dict]:
    """Insert time on the talk's cut timeline: the first sentence end (or real pause) at or after
    the anchor phrase. Recomputed at every render so later re-cuts move the memes with the words."""
    from .captions import timed_words_for
    from .panel import find_phrase
    ws = timed_words_for(item, words, al)
    total = al.get("kept") or (al["end"] - al["start"])
    out = []
    for m in entries:
        t0 = find_phrase(m["at"], ws) if m.get("at") else None
        if t0 is None:
            print(f'   ⚠ {item["id"]}: không thấy câu neo meme "{m.get("at")}" — bỏ meme {m.get("q")}')
            continue
        k = next(i for i, w in enumerate(ws) if w["s"] >= t0 - 1e-3) + len(m["at"].split()) - 1
        # first sentence end or real pause within 8 s after the anchor. Run-on scripts often drop
        # the full stop but keep the capital: "…diễn viên này Cũng không cần…" ends a sentence.
        def ends(i: int) -> bool:
            nxt = ws[i + 1]["w"]
            return bool(re.search(r"[.!?…]$", ws[i]["w"])) or ws[i + 1]["s"] - ws[i]["e"] >= 0.35 \
                or (nxt[:1].isupper() and nxt.lower() in STARTERS)
        win = [i for i in range(min(k, len(ws) - 2), len(ws) - 1) if ws[i]["s"] - t0 <= 8]
        hit = next((i for i in win if ends(i)), None)
        if hit is None and win:
            hit = max(win, key=lambda i: ws[i + 1]["s"] - ws[i]["e"])
        t = (ws[hit]["e"] + ws[hit + 1]["s"]) / 2 if hit is not None else total
        out.append({**m, "t": round(t, 3)})
    return out


# ---------- step ----------

def main(project: Path, force: bool = False) -> None:
    cfg = load_project(project)
    work = project / "work"
    plan = read_json(work / "plan.json")
    words = read_json(work / "words.json")
    align = {a["id"]: a for a in read_json(work / "align.json")}
    from .panel import parse_full
    wanted: list[dict] = []
    for it in plan:
        for line in it.get("memes") or []:
            f = parse_full(line)
            if f and f["props"].get("q"):
                wanted.append({"id": it["id"], "at": f["at"], **f["props"]})
            else:
                print(f"   ⚠ {it['id']}: dòng MEME không đọc được: {line[:60]}")
    auto = work / "memes_auto.json"
    if (cfg.get("memes") or {}).get("auto", True):
        if force or not auto.exists():
            try:
                write_json(auto, spot(project, plan, words, align))
            except Exception as e:
                print(f"⚠ AI chưa chọn được chỗ chèn meme ({str(e)[:80]})")
                write_json(auto, [])
        manual = {m["q"].lower() for m in wanted}
        wanted += [m for m in read_json(auto) if m.get("q", "").lower() not in manual]
    lib = library(project, cfg)
    rows = read_index(lib)
    per: dict[str, list[dict]] = {}
    for m in wanted:
        row = fetch(lib, rows, m, project.name)
        if not row:
            print(f"⚠ {m['id']}: không tìm được meme \"{m['q']}\" — bỏ qua")
            continue
        f = lib / row["file"]
        secs = float(m.get("secs", 2.5))
        if not int(row["still"] or 0) and row["duration"] and float(row["duration"]) <= 4.5:
            secs = float(row["duration"])   # a short clip plays whole: the punch is usually at the end
        per.setdefault(m["id"], []).append({"at": m["at"], "q": m["q"], "file": str(f), "secs": round(min(secs, 6.0), 2),
                                            "ss": float(m.get("ss", 0)), "mode": m.get("mode", "full"),
                                            "green": bool(int(row["green"] or 0)), "still": bool(int(row["still"] or 0)),
                                            "audio": bool(int(row["audio"] or 0))})
    write_index(lib, rows)
    out = work / "memes"
    if out.exists():
        for old in out.glob("t*.json"):
            old.unlink()
    for tid, ms in per.items():
        write_json(out / f"{tid}.json", ms)
    _sheet(work, [m for ms in per.values() for m in ms])
    print(f"→ {sum(len(v) for v in per.values())} meme trong {len(per)} đoạn · kho: {lib}")


def _sheet(work: Path, memes: list[dict]) -> None:
    """One frame per meme in work/memes_sheet.jpg (in the order printed) — look before you ship."""
    if not memes:
        return
    d = work / "memes" / "sheet"; d.mkdir(parents=True, exist_ok=True)
    for old in d.glob("*.jpg"):
        old.unlink()
    for k, m in enumerate(memes, 1):
        ss = [] if m["still"] else ["-ss", f"{m['ss'] + min(1.0, m['secs'] / 2):.2f}"]
        run(["ffmpeg", "-v", "error", "-y", *ss, "-i", m["file"], "-frames:v", "1",
             "-vf", "scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:(ow-iw)/2:(oh-ih)/2", str(d / f"{k:03d}.jpg")])
        print(f"   {k}. {m['q']} ({m['mode']}, {m['secs']}s)")
    cols = min(4, len(memes)); rows = -(-len(memes) // cols)
    run(["ffmpeg", "-v", "error", "-y", "-framerate", "1", "-i", str(d / "%03d.jpg"), "-vf", f"tile={cols}x{rows}", "-frames:v", "1", str(work / "memes_sheet.jpg")])
