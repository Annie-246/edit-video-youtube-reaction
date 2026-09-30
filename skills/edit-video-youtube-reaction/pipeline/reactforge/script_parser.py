"""Parse kich-ban.md (react script markdown) into an ordered plan of items.

Item types:
  talk  — presenter speaks (text = what anh reads; slide = left panel content)
  clip  — cut from the source video [CLIP mm:ss–mm:ss]
  score — scoreboard update (**Bảng điểm:** line)
Optional lines inside a talk block:  SLIDE: keyword | kicker | sub    BULLETS: a; b; c
Optional lines inside a clip paragraph: LABEL: text    NOTE: text
"""
from __future__ import annotations
import re
from pathlib import Path
from .common import hms_to_sec, write_json

CLIP_RE = re.compile(r"`?\[CLIP\s+(\d{1,2}:\d{2}(?::\d{2})?)\s*[–—-]\s*(\d{1,2}:\d{2}(?::\d{2})?)\]`?")
BOLD_CLIP_RE = re.compile(r"\*\*CLIP\s+(\d{1,2}:\d{2}(?::\d{2})?)\s*[–—-]\s*(\d{1,2}:\d{2}(?::\d{2})?)\.?\s*\*\*")
TALK_RE = re.compile(r"^\*\*Anh\s*\(([\d:]+)\)\s*:\*\*\s*(.*)$")
SCORE_RE = re.compile(r"^\*\*Bảng điểm:\*\*\s*(.*)$")
H2_RE = re.compile(r"^##\s+(.*)$")
TAG_RE = re.compile(r"`\[(?:[^\[\]]|\[[^\]]*\])*\]`|\[(SỐ THẬT|CÂU THẬT|KIỂM|ĐÃ KIỂM|ED)[^\]]*\]")
SCREEN_RE = re.compile(r"`?\[MÀN HÌNH:?\s*([^\]]*)\]`?")
PILL_RE = re.compile(r"\*\*([^*]+)\*\*")

COLS = {"dung": "ĐÚNG", "sai": "SAI", "c3": "CỘT 3", "du_bao": "CHƯA CHẤM"}


def _col_of(label: str) -> str:
    u = label.upper()
    if u.startswith("ĐÚNG NHƯNG") or "CỘT 3" in u or u.startswith("COT 3"):
        return "c3"
    if u.startswith("SAI"):
        return "sai"
    if u.startswith("DỰ BÁO") or u.startswith("CHƯA CHẤM") or u.startswith("THÌ TƯƠNG LAI") or u.startswith("CHƯA KIỂM"):
        return "du_bao"
    if u.startswith("ĐÚNG"):
        return "dung"
    return "c3"


def _clean_spoken(t: str) -> str:
    t = SCREEN_RE.sub("", t)
    t = TAG_RE.sub("", t)
    t = re.sub(r"\\(?=[~!.()\[\]#-])", "", t)
    t = re.sub(r"\*\*|__|`", "", t)
    t = re.sub(r"(?<!\w)\*(?!\s)", "", t); t = re.sub(r"(?<!\s)\*(?!\w)", "", t)
    t = re.sub(r"^\s*(?:- |\d+\.\s+)", "", t)
    return re.sub(r"\s+", " ", t).strip()


def _section_title(h: str) -> tuple[str, str]:
    """'2. "AI LÀ CÚ LỪA" + VÒNG TIỀN XOAY — dừng lâu #1' -> (num, title)"""
    h = re.sub(r"\*\*|\\(?=[~!.()])", "", h)
    m = re.match(r"^(\d+)\.\s*(.*)$", h.strip())
    num = m.group(1) if m else ""
    title = re.sub(r'["“”]', "", (m.group(2) if m else h).split("—")[0]).strip()
    return num, title



def _as_beat(rest: str) -> str:
    """A BEAT directive is a FULL directive that asked for the 'beat' style."""
    import json as _json
    m = re.search(r"\{.*\}", rest, re.S)
    if not m:
        return rest
    try:
        props = _json.loads(m.group(0))
    except ValueError:
        return rest
    props.setdefault("style", "beat")
    return rest[:m.start()] + _json.dumps(props, ensure_ascii=False)


def parse_script(md_path: Path) -> list[dict]:
    lines = md_path.read_text(encoding="utf-8").split("\n")
    items: list[dict] = []
    sec_num, sec_title = "", ""
    started = False  # set at the first numbered "## N." section; prose before it is front matter
    cur: dict | None = None  # current talk item

    def close():
        nonlocal cur
        if cur:
            cur["text"] = " ".join(x for x in cur["_lines"] if x).strip()
            del cur["_lines"]
            if cur["text"]:
                items.append(cur)
        cur = None

    for raw in lines:
        line = raw.rstrip()
        if H2_RE.match(line):
            h_text = H2_RE.match(line).group(1)
            if "PHỤ LỤC" in h_text.upper():
                close()
                break
            close(); sec_num, sec_title = _section_title(h_text)
            if sec_num: started = True
            continue
        if line.strip() == "---" or line.startswith("# "):
            close(); continue
        s = line.strip()
        m = TALK_RE.match(s)
        if m:
            close()
            cur = {"type": "talk", "section": sec_num, "title": sec_title, "planned": m.group(1),
                   "slide": {"keyword": sec_title.upper(), "kicker": ("MỞ MÀN" if sec_num == "0" else f"ĐIỂM DỪNG {sec_num}"), "sub": ""},
                   "bullets": None, "screens": [], "_lines": []}
            if m.group(2):
                cur["_lines"].append(_clean_spoken(m.group(2)))
            continue
        if s.startswith("BREAK:"):
            # a silent full-frame chapter card; gives the ear a rest between sections
            close()
            items.append({"type": "break", "section": sec_num, "title": s[6:].strip()})
            continue
        if s.startswith("**→") or s.startswith("→"):  # production note to anh, not spoken
            continue
        clip_m = re.search(r"\[?CLIP\s+(\d{1,2}:\d{2}(?::\d{2})?)\s*[–—-]\s*(\d{1,2}:\d{2}(?::\d{2})?)\]?", s, re.IGNORECASE)
        if clip_m and "CLIP" in s.upper() and not s.startswith("|") and not ("BẢNG CLIP" in s.upper()):
            close()
            for cm in re.finditer(r"\[?CLIP\s+(\d{1,2}:\d{2}(?::\d{2})?)\s*[–—-]\s*(\d{1,2}:\d{2}(?::\d{2})?)\]?", s, re.IGNORECASE):
                items.append({"type": "clip", "section": sec_num, "title": sec_title,
                              "start": hms_to_sec(cm.group(1)), "end": hms_to_sec(cm.group(2)), "label": "", "note": ""})
            continue
        if s.startswith("LABEL:") and items and items[-1]["type"] == "clip":
            items[-1]["label"] = s[6:].strip(); continue
        if s.startswith("NOTE:") and items and items[-1]["type"] == "clip":
            items[-1]["note"] = s[5:].strip(); continue
        sm = SCORE_RE.match(s)
        if sm:
            close()
            entries = []
            for part in re.split(r"\s+·\s+|\.\s+(?=[A-ZĐ\"“])", sm.group(1)):
                if "→" not in part:
                    continue
                claim, label = part.rsplit("→", 1)
                claim = re.sub(r"[\"“”]|\*\*|`", "", claim).strip()
                pm = PILL_RE.search(label)
                lab = (pm.group(1) if pm else label).strip().rstrip(".")
                entries.append({"claim": claim, "col": _col_of(lab), "label": lab})
            if entries:
                items.append({"type": "score", "section": sec_num, "entries": entries})
            continue
        if cur is None and started and not s.startswith(("|", "<", "LABEL:", "NOTE:")) \
                and not (s.startswith("*") and s.endswith("*") and not s.startswith("**")):
            # prose without an explicit **Anh (x:xx):** line → implicit talk block (Google-Doc style scripts)
            kick = "MỞ MÀN" if sec_num == "0" else (f"ĐIỀU {sec_num}" if sec_num else sec_title.upper()[:24])
            cur = {"type": "talk", "section": sec_num, "title": sec_title, "planned": "",
                   "slide": {"keyword": sec_title.upper(), "kicker": kick, "sub": ""},
                   "bullets": None, "screens": [], "_lines": []}
        if cur is not None:
            if s.startswith("GFX:"):
                cur.setdefault("gfx", []).append(s[4:].strip()); continue
            if s.startswith("SIDE:"):
                cur.setdefault("side", []).append(s[5:].strip()); continue
            if s.startswith("FULL:"):
                cur.setdefault("full", []).append(s[5:].strip()); continue
            if s.startswith("BEAT:"):
                # same machinery as FULL, different tone — the name is for whoever writes the
                # script: it marks a place to let a line land, not another fact to show.
                cur.setdefault("full", []).append(_as_beat(s[5:].strip())); continue
            if s.startswith("SLIDE:"):
                parts = [p.strip() for p in s[6:].split("|")]
                cur["slide"]["keyword"] = parts[0] if parts and parts[0] else cur["slide"]["keyword"]
                if len(parts) > 1: cur["slide"]["kicker"] = parts[1]
                if len(parts) > 2: cur["slide"]["sub"] = parts[2]
                continue
            if s.startswith("BULLETS:"):
                cur["bullets"] = [b.strip() for b in s[8:].split(";") if b.strip()]; continue
            for scm in SCREEN_RE.finditer(s):
                cur["screens"].append(scm.group(1).strip())
            if s.startswith("`[MÀN HÌNH") or s.startswith("[MÀN HÌNH"):
                continue
            if s.startswith("**Bảng điểm") or s.startswith("## "):
                continue
            cur["_lines"].append(_clean_spoken(s))
    close()
    # ids + cumulative scoreboard state attached to each talk item
    state = {"dung": [], "sai": [], "c3": [], "du_bao": []}
    n_talk = n_clip = n_break = 0
    for it in items:
        if it["type"] == "talk":
            n_talk += 1; it["id"] = f"t{n_talk:02d}"
            it["score_state"] = {k: list(v) for k, v in state.items()}
        elif it["type"] == "clip":
            n_clip += 1; it["id"] = f"c{n_clip:02d}"
        elif it["type"] == "break":
            n_break += 1; it["id"] = f"b{n_break:02d}"
        else:
            for e in it["entries"]:
                state[e["col"]].append(e["claim"])
    return items


def main(project: Path) -> list[dict]:
    from .common import load_project
    cfg = load_project(project)
    items = parse_script(project / cfg.get("script", "script.md"))
    write_json(project / "work" / "plan.json", items)
    talks = [i for i in items if i["type"] == "talk"]; clips = [i for i in items if i["type"] == "clip"]
    breaks = [i for i in items if i["type"] == "break"]
    print(f"plan: {len(items)} items — {len(talks)} talk, {len(clips)} clip, {len(breaks)} break, "
          f"{len(items)-len(talks)-len(clips)-len(breaks)} score")
    for it in items:
        if it["type"] == "talk":
            print(f"  {it['id']} talk  [{it['section']}] {len(it['text'].split())} từ | slide: {it['slide']['keyword']} | screens: {len(it['screens'])}")
        elif it["type"] == "clip":
            print(f"  {it['id']} clip  {it['start']:.0f}s–{it['end']:.0f}s ({it['end']-it['start']:.0f}s)")
        elif it["type"] == "break":
            print(f"  {it['id']} break \u2014 {it['title']}")
        else:
            print(f"  score {[ (e['col'], e['claim'][:30]) for e in it['entries'] ]}")
    return items
