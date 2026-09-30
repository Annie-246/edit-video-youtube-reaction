from __future__ import annotations
import json, os, re, shutil, subprocess
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parent
FONT_DIR = ROOT / "assets" / "fonts"

# Optional: point FFMPEG_DIR at an ffmpeg bin folder when ffmpeg is not on PATH.
FFMPEG_DIR = os.environ.get("FFMPEG_DIR", "")
if FFMPEG_DIR and os.path.isdir(FFMPEG_DIR) and FFMPEG_DIR not in os.environ.get("PATH", ""):
    os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")


def load_env(project: Path) -> None:
    """Tiny .env loader (project/.env, workspace/.env then ~/.env); never overrides existing vars."""
    candidates = (
        project / ".env",
        project.parent / ".env",
        Path(__file__).resolve().parents[4] / ".env",
        Path.home() / ".env",
        Path(os.environ.get("REACTFORGE_ENV_FALLBACK", Path.home() / "video_bot" / ".env")),
    )
    for p in candidates:
        if not p.is_file():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and v and k not in os.environ:
                os.environ[k] = v


def load_project(project: Path) -> dict:
    cfg = json.loads((project / "project.json").read_text(encoding="utf-8"))
    cfg.setdefault("output", {})
    out = cfg["output"]
    out.setdefault("width", 1920); out.setdefault("height", 1080); out.setdefault("fps", 30)
    out.setdefault("encoder", "auto")
    cfg.setdefault("whisper", {"model": "medium", "language": "vi"})
    cfg.setdefault("style", {})
    cfg["style"].setdefault("accent", "#8B7CFF")
    cfg.setdefault("recording", {})
    cfg["recording"].setdefault("cx", 0.5)
    cfg.setdefault("source", {})
    cfg["source"].setdefault("quality", 1080)
    cfg["source"].setdefault("pad", 1.0)
    return cfg


def run(cmd: list[str], quiet: bool = True) -> subprocess.CompletedProcess:
    resolved = list(cmd)
    if resolved and resolved[0] in ("ffmpeg", "ffprobe"):
        which_bin = shutil.which(resolved[0])
        if not which_bin and os.path.isdir(FFMPEG_DIR):
            cand = os.path.join(FFMPEG_DIR, resolved[0] + ".exe")
            if os.path.isfile(cand):
                resolved[0] = cand
    r = subprocess.run(resolved, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"command failed ({r.returncode}): {' '.join(resolved)}\n{r.stderr[-2000:]}")
    return r


def ffprobe_duration(path: Path) -> float:
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)])
    return float(r.stdout.strip())


def ffprobe_size(path: Path) -> tuple[int, int]:
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path)])
    w, h = r.stdout.strip().split(",")[:2]
    return int(w), int(h)


def hms_to_sec(s: str) -> float:
    parts = [float(x) for x in s.strip().split(":")]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    h, m, sec = parts
    return h * 3600 + m * 60 + sec


def sec_to_ass(t: float) -> str:
    t = max(0.0, t)
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def escape_ffmpeg_path(p: Path | str) -> str:
    """Escape a path for ffmpeg filter arguments (subtitles, fontsdir).
    On Windows: convert backslashes to forward slashes, and escape drive colons (e.g. D\\:).
    """
    s = str(p).replace("\\", "/")
    return s.replace(":", r"\:")


def pick_encoder(pref: str) -> list[str]:
    """Return ffmpeg video encoder args.
    Checks hardware encoders first (videotoolbox on Mac, qsv/amf/nvenc on PC),
    then falls back to multithreaded libx264 for CPU.
    """
    if pref == "auto":
        r = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True)
        stdout = r.stdout or ""
        if "h264_videotoolbox" in stdout:
            pref = "h264_videotoolbox"
        elif "h264_qsv" in stdout:
            pref = "h264_qsv"
        elif "h264_amf" in stdout:
            pref = "h264_amf"
        elif "h264_nvenc" in stdout:
            pref = "h264_nvenc"
        else:
            pref = "libx264"
    if pref == "h264_videotoolbox":
        return ["-c:v", "h264_videotoolbox", "-b:v", "12M", "-allow_sw", "1"]
    if pref == "h264_qsv":
        return ["-c:v", "h264_qsv", "-b:v", "10M", "-preset", "veryfast"]
    if pref == "h264_amf":
        return ["-c:v", "h264_amf", "-b:v", "10M", "-quality", "speed"]
    if pref == "h264_nvenc":
        return ["-c:v", "h264_nvenc", "-b:v", "10M", "-preset", "p4"]
    return ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-threads", "0"]


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
