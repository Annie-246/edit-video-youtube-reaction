#!/usr/bin/env python3
"""Verify a finished project, re-cut what the first pass missed, rebuild every segment, verify again.

Every segment is re-rendered (not just the changed ones) because the frame-grid fix in render.py
applies to all of them. Run detached: it reports to Telegram at the end.
"""
from __future__ import annotations
import subprocess, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from reactforge import captions, panel, render, verify  # noqa: E402
from reactforge.common import ffprobe_duration, read_json, run  # noqa: E402

P = Path(sys.argv[1]).resolve()
WORK = P / "work"


def tg(msg: str, video: str | None = None) -> None:
    cmd = [sys.executable, str(Path(__file__).parent / "tg_send.py")]
    cmd += (["--video", video, msg] if video else [msg])
    subprocess.run(cmd, capture_output=True)


def drift_report() -> tuple[str, float]:
    worst, lines = 0.0, []
    for seg in sorted((WORK / "seg").glob("*.mov")):
        v = float(run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "csv=p=0", str(seg)]).stdout)
        a = float(run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=duration", "-of", "csv=p=0", str(seg)]).stdout)
        d = abs(a - v)
        worst = max(worst, d)
        if d > 0.04:
            lines.append(f"{seg.stem}: lệch {d * 1000:.0f}ms")
    return ("; ".join(lines) or "mọi đoạn khớp trong 1 khung"), worst


def main() -> None:
    t0 = time.time()
    report = []

    print("\n═══ VÒNG 1: nghe lại bản dựng, tìm chỗ cắt sót ═══", flush=True)
    changed, lines = verify.check_round(P, 1, "medium")
    for l in lines:
        print(" ", l, flush=True)
    report += ["## Vòng 1", *lines]

    print(f"\n═══ DỰNG LẠI TOÀN BỘ (sửa lệch hình-tiếng; {len(changed)} đoạn có cắt mới) ═══", flush=True)
    captions.main(P)
    panel.main(P)
    render.main(P)

    print("\n═══ VÒNG 2: kiểm lại bản vừa dựng ═══", flush=True)
    changed2, lines2 = verify.check_round(P, 2, "medium")
    for l in lines2:
        print(" ", l, flush=True)
    report += ["", "## Vòng 2", *lines2]
    if changed2:
        print(f"  → dựng lại {len(changed2)} đoạn", flush=True)
        captions.main(P)
        for tid in changed2:
            panel.main(P, only=tid, force=True)
            render.main(P, only=tid)
        render.concat_only(P)

    drift, worst = drift_report()
    dur = ffprobe_duration(P / "out" / "final.mp4")
    report += ["", "## Khớp hình-tiếng", f"- {drift}"]
    (WORK / "verify_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    final = P / "out" / "final.mp4"
    dest = Path.home() / "Desktop/react-video-ai/260907-alex-hormozi-FULL-1080p.mp4"
    run(["cp", str(final), str(dest)])
    sample = P / "out" / "sample_90s.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-ss", "300", "-t", "90", "-i", str(final), "-vf", "scale=1280:720",
         "-c:v", "h264_videotoolbox", "-b:v", "2500k", "-allow_sw", "1", "-c:a", "aac", "-b:a", "128k",
         "-movflags", "+faststart", str(sample)])
    n1 = sum(1 for l in lines if "cắt thêm" in l)
    n2 = sum(1 for l in lines2 if "cắt thêm" in l)
    tg(f"✅ Kiểm tra + dựng lại xong ({(time.time() - t0) / 60:.0f} phút). Video {int(dur) // 60}:{int(dur) % 60:02d}. "
       f"Vòng 1 cắt thêm ở {n1} đoạn, vòng 2 ở {n2} đoạn. Khớp hình-tiếng: {drift} (lệch lớn nhất {worst * 1000:.0f}ms). "
       f"Mẫu 90s từ phút 5 gửi kèm; bản 1080p ở Desktop. Chi tiết: work/verify_report.md", str(sample))
    print(f"\n✅ XONG sau {(time.time() - t0) / 60:.0f} phút — {drift}", flush=True)


if __name__ == "__main__":
    main()
