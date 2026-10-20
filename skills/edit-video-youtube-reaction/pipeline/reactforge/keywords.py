"""Keyword captions for FACE talks (Greg Isenberg style).

No running subtitles: every few seconds a 2–5 word phrase appears word by word at chest height,
one or two words of it in clay. AI picks the phrases by WORD INDEX (it cannot invent timings);
a heuristic fills any stretch longer than MAX_GAP so the 10-second rule always holds — a new
keyword phrase counts as a new visual.
Cached in work/keywords/<talk_id>.json; edit it by hand and the next run keeps it as long as the
words of the talk did not change.
"""
from __future__ import annotations
from pathlib import Path
from .common import read_json, write_json

MAX_GAP = 9.0     # seconds without a phrase (or card / meme) before the filler steps in
MIN_GAP = 2.0
MAX_LEN = 5

SYSTEM = """Bạn là editor chọn CHỮ TỪ KHOÁ hiện trên màn hình cho video người nói tiếng Việt (kiểu Greg Isenberg: không có phụ đề chạy liên tục, chỉ thỉnh thoảng hiện một cụm ngắn ở ngang ngực người nói).
Đầu vào: lời người nói, mỗi từ có số thứ tự và mốc giây.
Chọn các CỤM 2–5 từ LIÊN TIẾP, chép nguyên văn, mang ý chính của câu: con số, tên riêng, khái niệm, câu chốt, lời hứa hẹn.
Trong mỗi cụm chọn 1–2 từ để TÔ MÀU (thường là danh từ / con số / tính từ mạnh ở cuối cụm).
Đánh dấu "big": true cho khoảng 1/3 số cụm đắt nhất: có con số, hoặc câu chốt mà phần tô màu rất ngắn (≤ 2 từ) — cụm này hiện chữ tô màu thật to.
Quy tắc nhịp: hai cụm liên tiếp cách nhau 3–8 giây; TUYỆT ĐỐI không để quá 9 giây không có cụm nào (kể cả đầu và cuối đoạn). Không chọn từ đệm, từ nối, câu vô nghĩa khi đứng riêng.
Trả về DUY NHẤT JSON: {"phrases":[{"from":<số thứ tự từ đầu>,"to":<số thứ tự từ cuối, bao gồm>,"hl":[<số thứ tự từ tô màu>],"big":<true|false>}]}"""

STOP = {"và", "là", "thì", "mà", "của", "có", "cho", "với", "này", "đó", "nó", "một", "những", "các", "được", "để", "khi", "nếu", "rồi", "cũng", "đã", "sẽ", "đang", "ạ", "à", "ờ", "nhé", "nha"}


def shown(w: str) -> str:
    """The word as it appears on screen: script spelling and case, no trailing punctuation."""
    return w.strip(".,;:!?…\"'“”()")


def _bare(w: str) -> str:
    return shown(w).lower()


def _valid(p: dict, n: int) -> bool:
    try:
        i, j = int(p["from"]), int(p["to"])
    except (KeyError, TypeError, ValueError):
        return False
    return 0 <= i <= j < n and j - i < MAX_LEN


def _pick_near(ws: list[dict], t: float, lo: float, hi: float) -> dict | None:
    """A 3-word phrase around time t (kept inside lo..hi), highlighting its longest content word."""
    cand = [k for k, w in enumerate(ws) if lo <= w["s"] and w["e"] <= hi]
    if len(cand) < 2:
        return None
    k = min(cand, key=lambda x: abs(ws[x]["s"] - t))
    i = max(cand[0], k - 1); j = min(cand[-1], i + 2)
    body = [x for x in range(i, j + 1) if _bare(ws[x]["w"]) not in STOP] or list(range(i, j + 1))
    return {"from": i, "to": j, "hl": [max(body, key=lambda x: len(_bare(ws[x]["w"])))]}


def fill_gaps(ws: list[dict], phrases: list[dict], total: float) -> list[dict]:
    """Insert heuristic phrases until no stretch is longer than MAX_GAP."""
    for _ in range(50):
        ph = sorted(phrases, key=lambda p: p["from"])
        marks = [0.0] + [x for p in ph for x in (ws[p["from"]]["s"], ws[p["to"]]["e"])] + [total]
        holes = [(marks[k], marks[k + 1]) for k in range(0, len(marks) - 1, 2) if marks[k + 1] - marks[k] > MAX_GAP]
        if not holes:
            return ph
        a, b = holes[0]
        p = _pick_near(ws, (a + b) / 2, a + 0.3, b - 0.3)
        if not p:
            return ph
        phrases = ph + [p]
    return sorted(phrases, key=lambda p: p["from"])


def _ask(project: Path, ws: list[dict]) -> list[dict]:
    from .judge import ask, _extract_json
    lines = [f"#{k} [{w['s']:.1f}] {w['w']}" for k, w in enumerate(ws)]
    text, _ = ask(project, SYSTEM, "LỜI NGƯỜI NÓI:\n" + "\n".join(lines), max_tokens=3000)
    return _extract_json(text).get("phrases", [])


def style_of(p: dict, ws: list[dict]) -> str:
    """'stack' (keyword huge under a small context line) for numbers and short punchlines,
    'line' otherwise. A keyword too long to stand alone at that size stays on the line."""
    hl = sorted(p["hl"])
    key = " ".join(shown(ws[k]["w"]) for k in hl)
    big = p.get("big") or any(c.isdigit() for c in key)
    # splitting the phrase around a keyword in its middle reads as nonsense
    # ("một hoàn chỉnh / workflow"), so the keyword must be one run at either end
    edge = hl == list(range(hl[0], hl[-1] + 1)) and (hl[0] == p["from"] or hl[-1] == p["to"])
    return "stack" if big and edge and len(key) <= 16 else "line"


def keys_props(phrases: list[dict], ws: list[dict]) -> list[dict]:
    """Phrases in the shape the Remotion `Keys` composition draws."""
    return [{"s": round(p["s"], 3), "e": round(p["e"] + 0.7, 3), "style": style_of(p, ws),
             "words": [{"w": shown(ws[k]["w"]), "t": round(ws[k]["s"], 3), "hl": k in p["hl"]} for k in range(p["from"], p["to"] + 1)]}
            for p in phrases]


def pick(project: Path, item: dict, ws: list[dict], total: float) -> list[dict]:
    """Phrases with times on the cut timeline: [{from,to,hl,s,e,text}]."""
    cache = project / "work" / "keywords" / f"{item['id']}.json"
    sig = " ".join(w["w"] for w in ws)
    if cache.exists():
        c = read_json(cache)
        if c.get("words") == sig:
            return c["phrases"]
    try:
        raw = [p for p in _ask(project, ws) if _valid(p, len(ws))]
    except Exception as e:
        print(f"   ⚠ {item['id']}: AI chọn từ khoá lỗi ({str(e)[:60]}) → tự chọn theo nhịp")
        raw = []
    # drop overlaps and phrases crowding the previous one
    clean: list[dict] = []
    for p in sorted(raw, key=lambda p: int(p["from"])):
        i, j = int(p["from"]), int(p["to"])
        if clean and (i <= clean[-1]["to"] or ws[i]["s"] - ws[clean[-1]["to"]]["e"] < MIN_GAP):
            continue
        hl = [int(h) for h in p.get("hl", []) if i <= int(h) <= j] or [j]
        clean.append({"from": i, "to": j, "hl": hl, "big": bool(p.get("big"))})
    phrases = fill_gaps(ws, clean, total)
    for p in phrases:
        p["s"] = ws[p["from"]]["s"]; p["e"] = ws[p["to"]]["e"]
        p["text"] = " ".join(shown(ws[k]["w"]) if k not in p["hl"] else f"*{shown(ws[k]['w'])}*" for k in range(p["from"], p["to"] + 1))
    write_json(cache, {"words": sig, "phrases": phrases})
    return phrases
