"""Refuse to ship a build with a hole in it.

Every step in this pipeline used to fail soft: a talk with no matching source range just
printed a line and carried on, a missing panel just rendered without one. That is how the
opening three minutes of a finished 32-minute video went out with a frozen left panel —
the log said so, nobody read the log.

So: one gate that knows what each plan item promised and checks the promise was kept,
run automatically before a full render and available on its own as `doctor`.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from .common import load_project, read_json

ERROR, WARN = "LỖI", "lưu ý"


def _dur(path: Path, stream: str) -> float | None:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", stream,
                        "-show_entries", "stream=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True).stdout.strip()
    try:
        return float(r)
    except ValueError:
        return None


def _nonempty(p: Path) -> bool:
    return p.exists() and p.stat().st_size > 0


def check(project: Path) -> list[tuple[str, str, str]]:
    """(level, item id, what is wrong) for everything this project promised but did not deliver."""
    out: list[tuple[str, str, str]] = []
    work = project / "work"
    plan_p = work / "plan.json"
    if not plan_p.exists():
        return [(ERROR, "-", "chưa có work/plan.json — chạy bước plan trước")]
    cfg = load_project(project)
    plan = read_json(plan_p)
    align = {a["id"]: a for a in read_json(work / "align.json")} if (work / "align.json").exists() else {}
    clips_meta = read_json(project / "source" / "clips.json") if (project / "source" / "clips.json").exists() else {}
    # a re-upload whose Vietnamese subtitles are already burned in: we keep them and add none
    burned = bool(cfg.get("source", {}).get("burned_captions"))

    talks = [i for i in plan if i["type"] == "talk"]
    with_screen = [i["id"] for i in talks if (project / "screens" / f"{i['id']}.mp4").exists()]

    for it in plan:
        tid = it["id"]
        if it["type"] == "talk":
            al = align.get(tid)
            if not al or al.get("start") is None:
                out.append((ERROR, tid, "chưa khớp lời (thiếu align) → đoạn này sẽ bị bỏ khỏi video"))
                continue
            if not _nonempty(work / "captions" / f"{tid}.ass"):
                out.append((ERROR, tid, "thiếu chữ nhảy theo lời (captions/*.ass rỗng)"))
            # the bug that shipped: most talks animate, one silently does not
            if with_screen and tid not in with_screen:
                out.append((ERROR, tid, f"thiếu ảnh chạy khung trái — {len(with_screen)}/{len(talks)} đoạn khác có, "
                                        "khung này sẽ đứng im suốt đoạn"))
            if it.get("gfx") and not _nonempty(work / "panel" / f"{tid}.mp4"):
                out.append((ERROR, tid, f"kịch bản khai {len(it['gfx'])} cảnh GFX nhưng chưa dựng panel"))
            for k, _ in enumerate(it.get("full") or []):
                mp4 = work / "cards" / f"{tid}_full{k}.mp4"
                png = work / "gfx" / f"{tid}_full{k}.png"
                if not (_nonempty(mp4) or _nonempty(png)):
                    out.append((ERROR, tid, f"khai thẻ toàn màn hình #{k} nhưng chưa có hình"))
            if it.get("full") and not (work / "full" / f"{tid}.json").exists():
                out.append((ERROR, tid, "khai thẻ toàn màn hình nhưng chưa tính được mốc hiện (chạy bước panel)"))
        elif it["type"] == "clip":
            src = project / "source" / clips_meta.get(tid, {}).get("file", f"{tid}.mp4")
            if not src.exists():
                out.append((ERROR, tid, f"thiếu clip gốc ({src.name}) → đoạn này sẽ bị bỏ khỏi video"))
            if burned:
                pass   # the source already carries Vietnamese subtitles burned into the picture
            elif not _nonempty(work / "subs" / f"{tid}.ass"):
                out.append((ERROR, tid, "thiếu phụ đề Việt (subs/*.ass rỗng)"))
            else:
                j = work / "subs" / f"{tid}.json"
                if j.exists():
                    ch = read_json(j)
                    if ch and all(c.get("vi") == c.get("en") for c in ch):
                        out.append((WARN, tid, "phụ đề vẫn là tiếng Anh — bước dịch chưa chạy được"))
        elif it["type"] == "break":
            if not (_nonempty(work / "cards" / f"{tid}.mp4") or _nonempty(work / "gfx" / f"{tid}_break.png")):
                out.append((ERROR, tid, "thiếu hình màn chuyển"))

    # anything already rendered must be frame-exact; a segment that drifts poisons the concat
    seg = work / "seg"
    if seg.exists():
        ids = [i["id"] for i in plan if i["type"] != "score"]
        for tid in ids:
            f = seg / f"{tid}.mov"
            if not f.exists():
                continue
            v, a = _dur(f, "v:0"), _dur(f, "a:0")
            if a is None:
                out.append((ERROR, tid, "đoạn đã dựng không có tiếng"))
            elif v and abs(a - v) > 0.001:
                out.append((ERROR, tid, f"lệch hình/tiếng {(a - v) * 1000:+.0f}ms trong đoạn đã dựng"))
        missing = [t for t in ids if not (seg / f"{t}.mov").exists()]
        if missing and len(missing) < len(ids):
            out.append((WARN, "-", f"chưa dựng: {', '.join(missing)}"))
    if not burned and not cfg.get("source", {}).get("cover_bottom") and any(i["type"] == "clip" for i in plan):
        out.append((WARN, "-", "source.cover_bottom chưa đặt — nếu clip gốc có chữ cháy sẵn thì sẽ chồng lên phụ đề"))
    return out


def report(problems: list[tuple[str, str, str]]) -> int:
    if not problems:
        print("✅ doctor: không thấy lỗ hổng nào")
        return 0
    errs = [p for p in problems if p[0] == ERROR]
    for lvl, tid, msg in problems:
        mark = "✗" if lvl == ERROR else "•"
        print(f"  {mark} [{tid}] {msg}")
    print(f"\n{len(errs)} lỗi, {len(problems) - len(errs)} lưu ý")
    return 1 if errs else 0


def main(project: Path) -> None:
    from .common import run
    for tool in ("ffmpeg", "ffprobe", "yt-dlp", "node"):
        try:
            run([tool, "-version"] if tool in ("ffmpeg", "ffprobe") else [tool, "--version"]); print("ok  ", tool)
        except Exception as e:
            print("THIẾU", tool, str(e)[:80])
    for mod in ("faster_whisper", "playwright", "anthropic"):
        try:
            __import__(mod); print("ok  ", mod)
        except Exception:
            print("THIẾU python:", mod)
    print()
    raise SystemExit(report(check(project)))


def preflight(project: Path) -> None:
    """Called before a full render. Stops the build instead of shipping a hole."""
    problems = [p for p in check(project) if p[0] == ERROR]
    if problems:
        print("✗ doctor chặn lại — thiếu thứ mà kịch bản đã khai:")
        for _, tid, msg in problems:
            print(f"    [{tid}] {msg}")
        raise SystemExit("Sửa xong rồi dựng lại, hoặc chạy render --only <id> nếu cố ý dựng lẻ.")
