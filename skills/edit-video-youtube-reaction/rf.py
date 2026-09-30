#!/usr/bin/env python3
"""Runner for the reactforge pipeline.

Installed plugins get their folder replaced on every update, so the Python venv and
Remotion node_modules live in a persistent data dir instead:
  --data <dir>  >  $CLAUDE_PLUGIN_DATA  >  ~/.edit-video-youtube-reaction

Usage:
  python rf.py [--data DIR] setup                 # install/refresh deps (idempotent)
  python rf.py [--data DIR] <reactforge args...>  # e.g. all projects/my-video
"""
from __future__ import annotations

import hashlib, os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIPELINE = HERE / "pipeline"
MOTION = HERE / "motion"


def data_dir(argv: list[str]) -> Path:
    if len(argv) >= 2 and argv[0] == "--data":
        d = argv[1]
        del argv[:2]
    else:
        d = os.environ.get("CLAUDE_PLUGIN_DATA", "")
    if not d or d.startswith("${"):  # unsubstituted placeholder when not run as a plugin
        d = str(Path.home() / ".edit-video-youtube-reaction")
    p = Path(d).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    return p


def venv_python(data: Path) -> Path:
    v = data / "venv"
    return v / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def digest(*files: Path) -> str:
    h = hashlib.sha256()
    for f in files:
        h.update(f.read_bytes())
    return h.hexdigest()


def stamp_ok(stamp: Path, value: str) -> bool:
    return stamp.is_file() and stamp.read_text() == value


def setup(data: Path) -> None:
    for tool in ("ffmpeg", "ffprobe", "yt-dlp", "node", "npm"):
        if not shutil.which(tool):
            sys.exit(f"THIẾU {tool} trên PATH — cài rồi chạy lại.")
    if sys.version_info < (3, 11):
        sys.exit("Cần Python >= 3.11")

    py = venv_python(data)
    if not py.exists():
        print("── tạo venv", flush=True)
        subprocess.check_call([sys.executable, "-m", "venv", str(data / "venv")])
        subprocess.check_call([str(py), "-m", "pip", "install", "-q", "-U", "pip"])

    py_stamp = data / ".pip-stamp"
    want = digest(PIPELINE / "pyproject.toml")
    if not stamp_ok(py_stamp, want):
        print("── cài thư viện Python", flush=True)
        subprocess.check_call([str(py), "-m", "pip", "install", "-q", str(PIPELINE)])
        subprocess.check_call([str(py), "-m", "playwright", "install", "chromium"])
        py_stamp.write_text(want)

    # Remotion resolves node_modules next to its sources, so mirror motion/ into the data dir.
    dst = data / "motion"
    shutil.copytree(MOTION, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("node_modules"))
    npm_stamp = data / ".npm-stamp"
    want = digest(MOTION / "package.json", MOTION / "package-lock.json")
    if not stamp_ok(npm_stamp, want) or not (dst / "node_modules").is_dir():
        print("── cài Remotion", flush=True)
        subprocess.check_call("npm ci --silent --no-audit --no-fund", cwd=dst, shell=True)
        npm_stamp.write_text(want)


def main() -> None:
    argv = sys.argv[1:]
    data = data_dir(argv)
    setup(data)
    if argv[:1] == ["setup"]:
        print(f"XONG. Dữ liệu cài ở: {data}")
        return
    env = dict(os.environ)
    # Current plugin code wins over the copy pip installed into the venv.
    env["PYTHONPATH"] = str(PIPELINE) + os.pathsep + env.get("PYTHONPATH", "")
    env["REMOTION_DIR"] = str(data / "motion")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    sys.exit(subprocess.call([str(venv_python(data)), "-m", "reactforge", *argv], env=env))


if __name__ == "__main__":
    main()
