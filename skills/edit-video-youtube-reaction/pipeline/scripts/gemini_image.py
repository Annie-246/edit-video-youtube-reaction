#!/usr/bin/env python3
"""Generate one illustration with the Gemini API (stdlib only).

Key: GEMINI_API_KEY (or GOOGLE_API_KEY) from the environment, <project>/.env or ~/.env.
Model: $GEMINI_IMAGE_MODEL, default gemini-2.5-flash-image.

Usage:
  python gemini_image.py --project projects/my-video --out assets/t03/hero.png \
      [--aspect 16:9] "prompt in English or Vietnamese"
"""
from __future__ import annotations

import argparse, base64, json, os, sys, urllib.error, urllib.request
from pathlib import Path


def load_key(project: Path) -> str:
    for k in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        if os.environ.get(k):
            return os.environ[k]
    for env in (project / ".env", Path.home() / ".env"):
        if not env.is_file():
            continue
        for line in env.read_text(encoding="utf-8").splitlines():
            k, _, v = line.partition("=")
            if k.strip() in ("GEMINI_API_KEY", "GOOGLE_API_KEY") and v.strip():
                return v.strip().strip('"').strip("'")
    sys.exit("Chưa có GEMINI_API_KEY — đặt trong <dự-án>/.env hoặc ~/.env")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=Path, default=Path("."))
    ap.add_argument("--out", required=True, help="path relative to the project, e.g. assets/t03/hero.png")
    ap.add_argument("--aspect", default="16:9")
    ap.add_argument("prompt")
    a = ap.parse_args()

    model = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
    body = {
        "contents": [{"parts": [{"text": a.prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": a.aspect}},
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": load_key(a.project)},
    )
    try:
        resp = json.load(urllib.request.urlopen(req, timeout=180))
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")[:600]
        hint = " (hết hạn mức free — đợi rồi thử lại, hoặc đổi GEMINI_IMAGE_MODEL)" if e.code == 429 else ""
        sys.exit(f"Gemini lỗi {e.code}{hint}: {msg}")

    for cand in resp.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            data = part.get("inlineData") or part.get("inline_data")
            if data and data.get("data"):
                out = a.project / a.out
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(base64.b64decode(data["data"]))
                print(out)
                return
    sys.exit(f"Gemini không trả ảnh: {json.dumps(resp, ensure_ascii=False)[:600]}")


if __name__ == "__main__":
    main()
