"""Build Vietnamese .ass subtitles for each clip from the source captions (translated by Claude)."""
from __future__ import annotations
import html, json, os, re
from pathlib import Path
from .common import load_project, read_json, write_json, sec_to_ass, FONT_DIR, load_env
from .graphics import layout_for

TS_RE = re.compile(r"^(\d{2}:\d{2}:\d{2})\.(\d{3}) --> (\d{2}:\d{2}:\d{2})\.(\d{3})")


def parse_vtt(path: Path) -> list[dict]:
    cues, prev = [], ""
    for block in re.split(r"\n\n+", path.read_text(encoding="utf-8")):
        ts, texts = None, []
        for l in block.strip().split("\n"):
            m = TS_RE.match(l)
            if m:
                ts = (int(m[1][:2]) * 3600 + int(m[1][3:5]) * 60 + int(m[1][6:8]) + int(m[2]) / 1000,
                      int(m[3][:2]) * 3600 + int(m[3][3:5]) * 60 + int(m[3][6:8]) + int(m[4]) / 1000); continue
            if l.startswith(("WEBVTT", "Kind:", "Language:")) or not l.strip():
                continue
            t = html.unescape(re.sub(r"<[^>]+>", "", l)).strip()
            t = re.sub(r"^\s*(>>|-)\s*|\[[^\]]*\]", "", t).strip()
            if t: texts.append(t)
        if ts is None: continue
        for t in texts:
            if t != prev:
                cues.append({"s": ts[0], "e": ts[1], "t": t}); prev = t
    # rolling auto-captions: the same line appears as the 2nd line of the previous cue → fix end times
    for i in range(len(cues) - 1):
        cues[i]["e"] = min(cues[i]["e"], cues[i + 1]["s"]) if cues[i + 1]["s"] > cues[i]["s"] else cues[i]["e"]
    return cues


def chunk_cues(cues: list[dict], start: float, end: float, max_words: int = 13) -> list[dict]:
    sel = [c for c in cues if c["e"] > start and c["s"] < end]
    out, buf, bs = [], [], None
    for c in sel:
        if bs is None: bs = c["s"]
        buf.append(c["t"])
        words = " ".join(buf).split()
        if len(words) >= max_words or re.search(r"[.?!]$", c["t"]):
            out.append({"s": max(bs, start) - start, "e": min(c["e"], end) - start, "en": " ".join(buf)}); buf, bs = [], None
    if buf:
        out.append({"s": max(bs, start) - start, "e": min(sel[-1]["e"], end) - start, "en": " ".join(buf)})
    for o in out:
        o["e"] = max(o["e"], o["s"] + 0.8)
    return out


SUB_SYSTEM = ("Bạn là người dịch phụ đề phim tài liệu sang tiếng Việt. Dịch tự nhiên, gọn để hiện dưới màn hình: "
              "mỗi dòng tối đa 14 từ, giữ nguyên số liệu và tên riêng, xưng hô thân mật (bạn / mình / cô ấy). "
              "Trả về DUY NHẤT một mảng JSON các chuỗi, cùng số phần tử và cùng thứ tự với đầu vào, không thêm lời nào khác.")


def translate(project: Path, chunks: list[dict], context: str) -> list[str]:
    """Translate one clip's caption lines.

    Routed through judge.ask so it works the same way the cut judge does: the API when the key
    has credit, otherwise the `claude -p` CLI on the Claude Code subscription. Without that
    fallback a missing key silently left the clips in English — and this script requires
    Vietnamese subtitles.
    """
    from .judge import ask
    src = json.dumps([c["en"] for c in chunks], ensure_ascii=False)
    text, usage = ask(project, SUB_SYSTEM, f"Bối cảnh: {context}\n\n{src}", max_tokens=8000)
    m = re.search(r"\[.*\]", text, re.S)
    arr = json.loads(m.group(0) if m else text)
    if len(arr) != len(chunks):
        raise RuntimeError(f"dịch trả về {len(arr)} dòng, cần {len(chunks)}")
    print(f"   (dịch qua {usage['via']})")
    return [str(x) for x in arr]


def write_ass(path: Path, chunks: list[dict], play_w: int, play_h: int, font_size: int, margin_v: int) -> None:
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {play_w}
PlayResY: {play_h}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,NotionInter,{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2.2,1,2,80,80,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [head]
    for c in chunks:
        t = re.sub(r"^\s*(>>|-)\s*|\[[^\]]*\]", "", c["vi"]).replace("\n", " ").replace("{", "(").replace("}", ")").strip()
        lines.append(f"Dialogue: 0,{sec_to_ass(c['s'])},{sec_to_ass(c['e'])},Sub,,0,0,0,,{t}\n")
    path.write_text("".join(lines), encoding="utf-8")


def transcribe_clip(clip_path: Path) -> list[dict]:
    """Fallback when no .vtt file exists: transcribe the clip audio directly."""
    from .align import transcribe
    try:
        words = transcribe(clip_path, "base", language="en", beam_size=1)
    except Exception as e:
        print(f"   ⚠ Không thể transcribe clip ({e})")
        return []
    if not words:
        return []
    chunks, buf, bs = [], [], None
    for w in words:
        if bs is None: bs = w["s"]
        buf.append(w["w"])
        if len(buf) >= 10 or w["w"].endswith((".", "!", "?")):
            chunks.append({"s": bs, "e": w["e"], "en": " ".join(buf)})
            buf, bs = [], None
    if buf:
        chunks.append({"s": bs, "e": words[-1]["e"], "en": " ".join(buf)})
    return chunks


def main(project: Path, force: bool = False) -> None:
    import time
    load_env(project)
    cfg = load_project(project)
    plan = read_json(project / "work" / "plan.json")
    clips = [i for i in plan if i["type"] == "clip"]
    vtts = list((project / "source").glob("captions*.vtt"))
    cues = parse_vtt(vtts[0]) if vtts else None
    if not cues:
        print("ℹ Không có captions*.vtt — sẽ tự động nghe và tạo phụ đề từ clip gốc qua Whisper")
    L = layout_for(cfg["output"]["width"])
    sd = project / "work" / "subs"; sd.mkdir(parents=True, exist_ok=True)
    clips_meta = read_json(project / "source" / "clips.json") if (project / "source" / "clips.json").exists() else {}
    for c in clips:
        jp, ap = sd / f"{c['id']}.json", sd / f"{c['id']}.ass"
        if ap.exists() and jp.exists() and not force:
            print(f"{c['id']}: phụ đề có sẵn"); continue
        if jp.exists() and not force:
            chunks = read_json(jp)
            write_ass(ap, chunks, L["clip"]["w"], L["clip"]["h"], L["sub_font"], L["sub_margin"])
            print(f"{c['id']}: dựng lại .ass từ bản dịch đã có"); continue
        if cues:
            chunks = chunk_cues(cues, c["start"], c["end"])
        else:
            clip_file = project / "source" / clips_meta.get(c["id"], {}).get("file", f"{c['id']}.mp4")
            chunks = transcribe_clip(clip_file) if clip_file.exists() else []
        if not chunks:
            print(f"{c['id']}: không có caption trong khoảng này"); ap.write_text("", encoding="utf-8"); continue
        vi = translate(project, chunks, cfg.get("title", ""))
        for ch, v in zip(chunks, vi): ch["vi"] = v
        write_json(jp, chunks)
        write_ass(ap, chunks, L["clip"]["w"], L["clip"]["h"], L["sub_font"], L["sub_margin"])
        print(f"{c['id']}: {len(chunks)} dòng phụ đề → {ap.name}")
        time.sleep(3)
