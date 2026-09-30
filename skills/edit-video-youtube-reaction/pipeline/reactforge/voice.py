"""Optional: synthesise the presenter's lines with ElevenLabs (cloned voice) when there is no real recording.
Produces work/voice/<id>.mp3 per talk item and work/voice/all.wav (items joined with pauses) — feed all.wav to HeyGen
(skill /heygen) to get a talking-head video, then drop that video into recording/."""
from __future__ import annotations
import os
from pathlib import Path
from .common import load_project, read_json, run, load_env, ffprobe_duration

API = "https://api.elevenlabs.io/v1/text-to-speech/{voice}"


def tts(text: str, out: Path, voice: str, model: str, key: str) -> None:
    import httpx
    r = httpx.post(API.format(voice=voice), headers={"xi-api-key": key, "Accept": "audio/mpeg"},
                   json={"text": text, "model_id": model, "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}, timeout=300)
    if r.status_code != 200:
        raise RuntimeError(f"ElevenLabs {r.status_code}: {r.text[:300]}")
    out.write_bytes(r.content)


def split_sentences(text: str) -> list[str]:
    import re
    parts = re.split(r"(?<=[.!?…:])\s+", text.strip())
    return [x.strip() for x in parts if x.strip()]


def chunk_text(text: str, max_chars: int) -> list[str]:
    """Group sentences into chunks of at most max_chars (HeyGen web only auto-confirms audio ≤ ~45s)."""
    chunks, buf = [], ""
    for sent in split_sentences(text):
        if buf and len(buf) + 1 + len(sent) > max_chars:
            chunks.append(buf); buf = sent
        else:
            buf = (buf + " " + sent).strip()
    if buf: chunks.append(buf)
    return chunks


def main(project: Path, pause: float = 1.2, force: bool = False, chunk_s: float | None = None) -> None:
    chunk_s = float(os.environ.get("REACTFORGE_CHUNK_S", chunk_s or 45.0))
    load_env(project)
    cfg = load_project(project)
    key, voice = os.environ.get("ELEVENLABS_API_KEY"), os.environ.get("ELEVENLABS_VOICE_ID")
    model = os.environ.get("ELEVENLABS_MODEL", "eleven_v3")
    engine = os.environ.get("REACTFORGE_TTS")
    if not engine:
        engine = "say"
        if key and voice:
            import httpx
            try:
                ok = httpx.get("https://api.elevenlabs.io/v1/user/subscription", headers={"xi-api-key": key}, timeout=20).status_code == 200
            except Exception:
                ok = False
            engine = "eleven" if ok else "say"
            if not ok: print("⚠ khoá ElevenLabs không hợp lệ (401)")
    if engine == "say":
        print("⚠ không có khoá ElevenLabs → dùng giọng máy macOS (say -v Linh) — chỉ để thử pipeline")
    plan = read_json(project / "work" / "plan.json")
    vd = project / "work" / "voice"; vd.mkdir(parents=True, exist_ok=True)
    parts, chunks_meta = [], []
    chars_per_s = float(os.environ.get("REACTFORGE_CHARS_PER_S", "13"))  # đo 03/09: giọng Linh 180wpm ≈ 13 ký tự/giây
    max_chars = int(chunk_s * chars_per_s)

    def synth(text: str, mp3: Path) -> None:
        if engine == "say":
            aiff = mp3.with_suffix(".aiff")
            run(["say", "-v", os.environ.get("SAY_VOICE", "Linh"), "-r", "180", "-o", str(aiff), text])
            run(["ffmpeg", "-v", "error", "-y", "-i", str(aiff), "-c:a", "libmp3lame", "-b:a", "160k", str(mp3)]); aiff.unlink()
        else:
            tts(text, mp3, voice, model, key)

    for it in plan:
        if it["type"] != "talk": continue
        for ci, ctext in enumerate(chunk_text(it["text"], max_chars), 1):
            mp3 = vd / f"{it['id']}_{ci:02d}.mp3"
            if force or not mp3.exists():
                synth(ctext, mp3)
            dur = ffprobe_duration(mp3)
            if dur > chunk_s + 8 and len(split_sentences(ctext)) > 1:  # quá dài → chia đôi theo câu
                half = chunk_text(ctext, max(80, len(ctext) // 2 + 20))
                for hj, htext in enumerate(half, 1):
                    m2 = vd / f"{it['id']}_{ci:02d}{chr(96 + hj)}.mp3"; synth(htext, m2)
                    d2 = ffprobe_duration(m2); print(f"{it['id']} khúc {ci}{chr(96 + hj)}: {d2:.1f}s"); parts.append(m2); chunks_meta.append({"id": it["id"], "file": m2.name, "dur": d2, "text": htext})
                mp3.unlink(); continue
            print(f"{it['id']} khúc {ci}: {mp3.name} ({dur:.1f}s, {len(ctext)} ký tự)")
            parts.append(mp3); chunks_meta.append({"id": it["id"], "file": mp3.name, "dur": dur, "text": ctext})
    from .common import write_json
    write_json(vd / "chunks.json", chunks_meta)
    sil = vd / "pause.wav"
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{pause}", "-c:a", "pcm_s16le", str(sil)])
    wavs = []
    for p in parts:
        w = p.with_suffix(".wav"); run(["ffmpeg", "-v", "error", "-y", "-i", str(p), "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", str(w)]); wavs.append(w)
    lst = vd / "list.txt"
    lst.write_text("".join(f"file '{sil}'\nfile '{w}'\n" for w in wavs) + f"file '{sil}'\n", encoding="utf-8")
    allw = vd / "all.wav"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c:a", "pcm_s16le", str(allw)])
    run(["ffmpeg", "-v", "error", "-y", "-i", str(allw), "-c:a", "libmp3lame", "-b:a", "192k", str(vd / "all.mp3")])
    print(f"→ {allw} ({ffprobe_duration(allw):.1f}s) + all.mp3 — đưa vào HeyGen để dựng mặt")
