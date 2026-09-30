"""Word-by-word karaoke captions for talk segments.

Script words are shown (correct spelling), timed by the whisper words of the recording:
matched words take the recognised timing; short unmatched runs are interpolated between anchors;
where the presenter clearly said something else (long ASR run vs few script words) the ASR words
are shown instead, so the caption follows what was actually said.
Output: work/captions/<talk_id>.ass with ASS \\k karaoke tags (times relative to the talk cut).
"""
from __future__ import annotations
import difflib, re
from pathlib import Path
from .align import normalize
from .common import load_project, read_json, sec_to_ass
from .graphics import layout_for

MAX_WORDS, MAX_CHARS, GAP_BREAK = 7, 34, 0.7
ADLIB_SEC_PER_WORD = 1.2   # script gap stretched beyond this → presenter ad-libbed → use ASR words
FILLER_SEC = 0.8           # inserted ASR-only run shorter than this (e.g. "à", "ờ") → dropped
PUNCT_END = re.compile(r"[.,;:!?…]$")


ASR_WORD_FIXES = {
    "thốc": "token", "cựn": "", "cửn": "", "tốc": "token", "cường": "",
    "clot": "Claude", "cloth": "Claude", "cloud": "Claude",
    "cach": "cache", "sonet": "Sonnet", "offput": "Opus",
    "xô": "so", "xánh": "sánh", "đứt": "đơn", "dưa": "rơi", "tổn": "tổng"
}

def clean_word(w: str) -> str:
    low = w.lower().strip(".,;:!?")
    if low in ASR_WORD_FIXES:
        repl = ASR_WORD_FIXES[low]
        return repl if repl else ""
    return w

def time_words(text: str, words: list[dict], start: float, end: float) -> list[dict]:
    sw = [w for w in text.split() if normalize(w)]
    sn = [normalize(w) for w in sw]
    aw = [w for w in words if w["e"] >= start - 0.3 and w["s"] <= end + 0.3]
    an = [normalize(w["w"]) for w in aw]
    out: list[dict] = []

    def gap(si: int, sj: int, ai: int, aj: int) -> list[dict]:
        g_s, g_a = sw[si:sj], aw[ai:aj]
        if not g_s and not g_a:
            return []
        a_t = aw[ai - 1]["e"] if ai > 0 else start
        b_t = aw[aj]["s"] if aj < len(aw) else end
        span = max(0.0, b_t - a_t)
        # Prioritize script words to ensure 100% correct spelling from script.md
        if g_s:
            step = span / len(g_s) if span > 0 else 0.25
            return [{"w": w, "s": a_t + k * step, "e": a_t + (k + 1) * step} for k, w in enumerate(g_s)]
        if g_a:
            if span < FILLER_SEC:
                return []
            res = []
            for x in g_a:
                cw = clean_word(x["w"])
                if cw:
                    res.append({"w": cw, "s": x["s"], "e": x["e"]})
            return res
        return []


    if aw:
        sm = difflib.SequenceMatcher(None, sn, an, autojunk=False)
        si = ai = 0
        for b in sm.get_matching_blocks():
            if b.size == 0:
                continue
            out += gap(si, b.a, ai, b.b)
            for k in range(b.size):
                out.append({"w": sw[b.a + k], "s": aw[b.b + k]["s"], "e": aw[b.b + k]["e"]})
            si, ai = b.a + b.size, b.b + b.size
        out += gap(si, len(sw), ai, len(aw))
    else:
        out = gap(0, len(sw), 0, 0)
    # monotonic, non-degenerate timings
    res, prev_e = [], start
    for w in out:
        s = max(w["s"], prev_e); e = max(w["e"], s + 0.05)
        res.append({"w": w["w"], "s": round(s, 3), "e": round(e, 3)}); prev_e = e
    return res


def group_lines(ws: list[dict]) -> list[list[dict]]:
    lines, cur, chars = [], [], 0
    for k, w in enumerate(ws):
        cur.append(w); chars += len(w["w"]) + 1
        nxt = ws[k + 1] if k + 1 < len(ws) else None
        brk = nxt is None or len(cur) >= MAX_WORDS or chars + len(nxt["w"]) > MAX_CHARS \
            or (nxt["s"] - w["e"] > GAP_BREAK) or (len(cur) >= 3 and PUNCT_END.search(w["w"]))
        if brk:
            lines.append(cur); cur, chars = [], 0
    return lines


def _ass_color(hex_rgb: str, alpha: int = 0) -> str:
    h = hex_rgb.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def build_ass(L: dict, accent: str, ws: list[dict], t0: float) -> str:
    s = L["s"]; hd = L["head"]
    font = int(46 * s)
    ml = hd["x"] + int(28 * s); mr = L["w"] - (hd["x"] + hd["w"]) + int(28 * s); mv = L["h"] - (hd["y"] + hd["h"]) + int(30 * s)
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {L['w']}
PlayResY: {L['h']}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Kara,Be Vietnam Pro,{font},{_ass_color(accent)},&H28FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,{2.6*s:.1f},{1.2*s:.1f},2,{ml},{mr},{mv},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = group_lines(ws)
    ev = []
    for li, ln in enumerate(lines):
        st = ln[0]["s"] - 0.10
        nxt_start = lines[li + 1][0]["s"] - 0.10 if li + 1 < len(lines) else None
        en = ln[-1]["e"] + 0.35
        if nxt_start is not None:
            en = min(en, nxt_start)
        parts = []
        for k, w in enumerate(ln):
            nxt = ln[k + 1]["s"] if k + 1 < len(ln) else None
            dur = (nxt - w["s"]) if nxt is not None else (w["e"] - w["s"])
            if k == 0:
                dur += 0.10  # the line appears 0.10s early
            txt = w["w"].replace("{", "(").replace("}", ")")
            parts.append(f"{{\\k{max(1, int(round(dur * 100)))}}}{txt}")
        ev.append(f"Dialogue: 0,{sec_to_ass(st - t0)},{sec_to_ass(en - t0)},Kara,,0,0,0,,{' '.join(parts)}")
    return head + "\n".join(ev) + "\n"


def remap_words(ws: list[dict], keep: list[list[float]]) -> list[dict]:
    """Move word times onto the cut timeline (0 = first kept frame); words inside a cut are dropped."""
    offs, acc = [], 0.0
    for s, e in keep:
        offs.append((s, e, acc)); acc += e - s
    def f(t):
        for s, e, a in offs:
            if s <= t <= e:
                return a + (t - s)
        return None
    out = []
    for w in ws:
        ns, ne = f(w["s"]), f(w["e"])
        if ns is None:
            nxt = [s for s, e, a in offs if s >= w["s"]]
            ns = f(nxt[0]) if nxt else None
        if ne is None:
            prv = [e for s, e, a in offs if e <= w["e"]]
            ne = f(prv[-1]) if prv else None
        if ns is None or ne is None or ne <= ns:
            continue
        out.append({"w": w["w"], "s": round(ns, 3), "e": round(ne, 3)})
    return out


def timed_words_for(item: dict, words: list[dict], al: dict) -> list[dict]:
    """Script words (plus ad-libbed ASR words) with times on the cut timeline of this talk."""
    keep = al.get("keep") or [[al["start"], al["end"]]]
    kept = [w for w in words if not w.get("unk") and any(s <= (w["s"] + w["e"]) / 2 <= e for s, e in keep)]
    ws = time_words(item["text"], kept, al["start"], al["end"])
    return remap_words(ws, keep)


def main(project: Path) -> None:
    cfg = load_project(project); L = layout_for(cfg["output"]["width"])
    plan = read_json(project / "work" / "plan.json")
    words = read_json(project / "work" / "words.json")
    align = {a["id"]: a for a in read_json(project / "work" / "align.json")}
    out = project / "work" / "captions"; out.mkdir(parents=True, exist_ok=True)
    for it in plan:
        if it["type"] != "talk":
            continue
        al = align.get(it["id"])
        if not al or al.get("start") is None:
            continue
        ws = timed_words_for(it, words, al)
        (out / f"{it['id']}.ass").write_text(build_ass(L, cfg["style"]["accent"], ws, 0.0), encoding="utf-8")
        n_lines = len(group_lines(ws))
        print(f"{it['id']}: {len(ws)} từ → {n_lines} dòng chữ nhảy → captions/{it['id']}.ass")
