"""Claude as the editor: reads the script + the whisper transcript of one talk and marks what to cut.

Whisper gives words with timestamps; it cannot tell a rhetorical repeat from a restart, a paraphrase
from a stumble, or "11 nghìn" from "11.000". Claude can. It answers with WORD INDICES (never times),
so it cannot invent timestamps; we convert indices to cut points halfway between neighbouring words.
"""
from __future__ import annotations
import json, os, re
from pathlib import Path
from .common import load_env

MODEL = os.environ.get("REACTFORGE_JUDGE_MODEL", "claude-opus-5")

SYSTEM = """Bạn là người dựng video (editor) chuyên nghiệp cắt bản ghi talking-head tiếng Việt.
Đầu vào: KỊCH BẢN người dẫn định đọc, và LỜI THẬT do máy nhận dạng (mỗi từ có số thứ tự và mốc giây; giữa các từ có ghi chú quãng nghỉ / tiếng không ra chữ).
Nhiệm vụ: đánh dấu những chỗ PHẢI CẮT để lời nghe liền mạch, tự nhiên:
1. KHÓA QUY TẮC CỨNG - GIỮ Ý CUỐI CÙNG: Một ý người nói có thể nói vài lần (đọc lại, thử lại, vấp rồi sửa) -> BẮT BUỘC chỉ giữ lại đoạn nói CUỐI CÙNG (hoặc ý hoàn chỉnh nhất). Tuyệt đối không để lặp lại ý trong video.
2. ĐỆM AN TOÀN - KHÔNG CẮT CHƯỜM VÀO TỪ: Ranh giới cắt phải rơi vào quãng nghỉ tự nhiên. Kết thúc mỗi ý và chuyển đoạn phải chừa khoảng đệm từ từ cuối đến phần sau, tuyệt đối không cắt sát làm nuốt âm, cụt chữ hoặc mất từ đầu/đuôi.
3. CẮT BỎ: Nói sai rồi tự sửa ("à không", "ý là"), từ đệm đứng riêng ("ờ", "à", "ừm"), tiếng rác không ra chữ, câu nói ngoài lề cho ekip ("quay lại nhé", "đoạn này cắt đi").
4. KHÔNG CẮT: Điệp từ lặp có chủ ý đã ghi rõ trong kịch bản; nói lệch từ so với kịch bản nhưng vẫn trôi chảy; cách đọc số. Khi không chắc chắn vấp, KHÔNG cắt.
Trả về DUY NHẤT một JSON: {"cuts":[{"from":<số thứ tự từ đầu>,"to":<số thứ tự từ cuối, bao gồm>,"why":"đọc lại|đọc hụt|sửa lời|đệm|ngoài lề","note":"≤12 từ"}],"review":["ghi chú cho người dựng nếu có chỗ đáng ngờ"]}"""


def _fmt_words(words: list[dict], silences: list[list[float]] | None) -> str:
    out = []
    for i, w in enumerate(words):
        if i > 0:
            gap = w["s"] - words[i - 1]["e"]
            if gap >= 0.5:
                silent = sum(max(0.0, min(b, w["s"]) - max(a, words[i - 1]["e"])) for a, b in (silences or []))
                kind = "im lặng" if silent >= gap - 0.3 else "có tiếng nhưng không ra chữ"
                out.append(f"   [{kind} {gap:.1f}s]")
        mark = " ~" if w.get("zoom") and not w.get("unk") else ""
        out.append(f"#{i} [{w['s']:.1f}] {w['w']}{mark}" if not w.get("unk") else f"#{i} [{w['s']:.1f}–{w['e']:.1f}] [tiếng không rõ, có nói nhưng không nghe ra chữ]")
    return "\n".join(out)


def _extract_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0) if m else text)


CLI_MODEL = os.environ.get("REACTFORGE_CLI_MODEL", "opus")


def ask(project: Path, system: str, user: str, max_tokens: int = 8000) -> tuple[str, dict]:
    """Ask LLM (Gemini / Anthropic / CLI).
    Prioritizes GEMINI_API_KEY (native in Antigravity / Gemini) then ANTHROPIC_API_KEY.
    """
    load_env(project)
    # 1. Google Gemini API (native Antigravity support, zero extra dependencies)
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if gemini_key:
        import time, urllib.request, json
        g_model = os.environ.get("REACTFORGE_GEMINI_MODEL", "gemini-2.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{g_model}:generateContent?key={gemini_key}"
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"{system}\n\n---\n\n{user}"}]}
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": max_tokens
            }
        }
        for attempt in range(4):
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    candidates = res.get("candidates", [])
                    if not candidates:
                        raise RuntimeError("Gemini không trả về kết quả")
                    parts = candidates[0].get("content", {}).get("parts", [])
                    text = "".join(p.get("text", "") for p in parts)
                    return text, {"in": len(user) // 4, "out": len(text) // 4, "via": f"gemini ({g_model})"}
            except Exception as e:
                err_str = str(e)
                if any(code in err_str for code in ["429", "Too Many Requests", "503", "Service Unavailable", "500"]) and attempt < 4:
                    wait_s = (attempt + 1) * 25
                    print(f"   ⏳ Gemini API ({err_str[:60]}), chờ {wait_s}s để hết chu kỳ quota...")
                    time.sleep(wait_s)
                    continue
                print(f"   ⚠ Gemini API ({e}) → thử phương án khác")
                break

    # 2. Anthropic API
    if os.environ.get("ANTHROPIC_API_KEY") and os.environ.get("REACTFORGE_FORCE_CLI") != "1":
        try:
            import anthropic
            client = anthropic.Anthropic()
            kwargs = dict(model=MODEL, max_tokens=max_tokens, system=system, messages=[{"role": "user", "content": user}])
            try:
                r = client.messages.create(**kwargs, extra_headers={"anthropic-beta": "server-side-fallback-2026-07-01"}, extra_body={"fallbacks": "default"})
            except anthropic.BadRequestError as e:
                if "credit balance" in str(e):
                    raise
                r = client.messages.create(**kwargs)
            if getattr(r, "stop_reason", "") == "refusal":
                raise RuntimeError("Claude từ chối yêu cầu này")
            text = "".join(getattr(b, "text", None) or "" for b in r.content)
            return text, {"in": r.usage.input_tokens, "out": r.usage.output_tokens, "via": "anthropic-api"}
        except Exception as e:
            if "credit balance" not in str(e):
                print(f"   ⚠ Anthropic API: {e}")
            else:
                print("   (API hết credit → dùng gói Claude Code qua CLI)")

    # 3. Claude Code CLI
    import subprocess, shutil
    cli_cmd = shutil.which("claude") or ("claude.cmd" if os.name == "nt" else "claude")
    try:
        r = subprocess.run([cli_cmd, "-p", "--model", CLI_MODEL], input=f"{system}\n\n---\n\n{user}",
                           capture_output=True, text=True, timeout=900, shell=(os.name == "nt"))
        if r.returncode != 0:
            raise RuntimeError(f"claude CLI lỗi: {r.stderr[-400:]}")
        return r.stdout, {"in": len(user) // 4, "out": len(r.stdout) // 4, "via": "claude-cli"}
    except Exception as e:
        raise RuntimeError("Không tìm thấy GEMINI_API_KEY hoặc ANTHROPIC_API_KEY trong .env và không gọi được CLI") from e


def judge_talk(project: Path, script_text: str, words: list[dict], silences: list[list[float]] | None) -> dict:
    """Ask Claude which word ranges to cut. Returns {"cuts": [...], "review": [...], "usage": {...}}."""
    user = f"KỊCH BẢN:\n{script_text}\n\nLỜI THẬT (số thứ tự · giây · từ):\n{_fmt_words(words, silences)}"
    text, usage = ask(project, SYSTEM, user)
    data = _extract_json(text)
    return {"cuts": data.get("cuts", []), "review": data.get("review", []), "usage": usage, "model": MODEL}


def cuts_to_times(cuts: list[dict], words: list[dict], start: float, end: float) -> list[dict]:
    """Word-index ranges → time ranges with edges halfway between neighbouring words."""
    out = []
    n = len(words)
    for c in cuts:
        try:
            i, j = int(c["from"]), int(c["to"])
        except (KeyError, ValueError, TypeError):
            continue
        if i < 0 or j >= n or j < i:
            continue
        cs = (words[i - 1]["e"] + words[i]["s"]) / 2 if i > 0 else max(start, words[i]["s"] - 0.15)
        ce = (words[j]["e"] + words[j + 1]["s"]) / 2 if j + 1 < n else min(end, words[j]["e"] + 0.15)
        out.append({"s": round(cs, 3), "e": round(ce, 3), "why": f"claude: {c.get('why', '')}",
                    "text": " ".join(w["w"] for w in words[i:j + 1])[:160] + (f" — {c['note']}" if c.get("note") else "")})
    return out
