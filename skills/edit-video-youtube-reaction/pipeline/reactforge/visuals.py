"""Visuals: real pictures and brand logos cut into the content frame, found and fetched by the AI.

  1. spot   AI reads every talk shown in the content frame (white layout / BUBBLE / MOTION) and
            picks: each brand, app or company the presenter names (its logo, once per video),
            and the concrete things worth showing as a real photo (an object, a place, a kind of
            person) → work/visuals_auto.json (edit or empty it freely).
  2. fetch  logos: logo library → Wikimedia Commons → Simple Icons. Photos: Pexels when
            PEXELS_API_KEY is set, else Openverse, else Wikimedia Commons. Logos are kept in
            <workspace>/logo-library for later videos; photos land in assets/auto/.
  3. place  panel.py cuts each one into the scene list where its anchor phrase is said and resumes
            the interrupted scene after it → work/visuals/<id>.json.

project.json "visuals": {"auto": false} turns the AI pass off.
"""
from __future__ import annotations
import json, os, re, urllib.parse, urllib.request
from pathlib import Path

from .common import load_env, load_project, read_json, run, write_json

UA = {"User-Agent": "reactforge/1.0 (video editing pipeline; local use)"}   # Wikimedia rejects anonymous agents
EVERY = 30.0          # about one photo moment per this many seconds of content-frame talk
LOGO_SECS, PHOTO_SECS = 3.2, 4.5
PHOTO_TPL = ["stack", "swipe", "wall", "photo"]   # rotated so two photo moments never look the same

SPOT = """Bạn là editor video YouTube tiếng Việt. Khung nội dung của video cần HÌNH THẬT để minh hoạ lời người dẫn, không chỉ đồ hoạ.
Đầu vào: lời người dẫn của từng đoạn (mã đoạn, rồi lời kèm mốc giây).
Chọn hai loại:
1. "logo": MỌI thương hiệu, ứng dụng, phần mềm, công ty, nền tảng được nhắc tên (vd CapCut, Shopee, TikTok, ChatGPT, Gemini). Mỗi tên chỉ một lần, ở lần nhắc đầu tiên.
2. "photo": thứ CỤ THỂ nhìn thấy được mà ảnh thật minh hoạ tốt hơn đồ hoạ: đồ vật, sản phẩm, địa điểm, bối cảnh, kiểu người, hoạt động. Tối đa {n} chỗ cho cả video, cách nhau ≥ 20 giây. KHÔNG chọn ý trừu tượng (chiến lược, lợi nhuận, cảm xúc), thao tác trên phần mềm, hay chỗ người dẫn đang đọc số liệu.
Quy tắc:
- "at" là 2–6 từ LIÊN TIẾP chép NGUYÊN VĂN từ lời của đoạn đó; với logo, "at" bắt đầu bằng chính tên thương hiệu.
- logo: "brand" là tên chuẩn quốc tế (vd "CapCut", "Google Gemini").
- photo: "q" là 2–4 từ khoá TIẾNG ANH để tìm ảnh stock (vd "flip flops sandals", "film set camera crew"); "caption" là chú thích tiếng Việt ≤ 7 từ.
Trả về DUY NHẤT JSON: {{"visuals":[{{"id":"t02","kind":"logo","at":"...","brand":"..."}},{{"id":"t03","kind":"photo","at":"...","q":"...","caption":"..."}}]}}"""


def _get(url: str, headers: dict | None = None) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers={**UA, **(headers or {})}), timeout=30) as resp:
        return resp.read()


def _json(url: str, headers: dict | None = None) -> dict:
    return json.loads(_get(url, headers).decode("utf-8"))


def _toks(s: str) -> list[str]:
    return [t for t in re.split(r"[^a-z0-9]+", s.lower()) if t]


def _slug(s: str) -> str:
    return "-".join(_toks(s))[:50] or "x"


def logo_library(project: Path, cfg: dict) -> Path:
    p = (cfg.get("visuals") or {}).get("logos") or os.environ.get("REACTFORGE_LOGO_LIB")
    lib = Path(p) if p else (project.parent.parent if project.parent.name == "projects" else project.parent) / "logo-library"
    lib.mkdir(parents=True, exist_ok=True)
    return lib


# ---------- logos ----------

def _commons_files(q: str, n: int, width: int) -> list[dict]:
    url = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6"
           f"&gsrlimit={n}&prop=imageinfo&iiprop=url|size|mime&iiurlwidth={width}&gsrsearch=" + urllib.parse.quote(q))
    pages = _json(url).get("query", {}).get("pages", {})
    return [{"title": p["title"], **p["imageinfo"][0]} for p in sorted(pages.values(), key=lambda p: p.get("index", 0)) if p.get("imageinfo")]


def _logo_commons(brand: str, dest: Path) -> Path | None:
    """Best file named after the brand: "<brand> logo/icon" with no extra words, SVG first
    (Commons rasterises it to PNG at any width)."""
    want = set(_toks(brand))
    best, score = None, 0.0
    for f in _commons_files(f"{brand} logo", 12, 800):
        if f["mime"] not in ("image/svg+xml", "image/png", "image/webp"):
            continue
        name = _toks(re.sub(r"^File:|\.[a-z]+$", "", f["title"], flags=re.I))
        if not want <= set(name):
            continue
        extra = [t for t in name if t not in want and t not in ("logo", "icon", "svg", "png", "2024", "2025")]
        sc = 3 * any(t in ("logo", "icon") for t in name) + (f["mime"] == "image/svg+xml") - 2 * len(extra)
        if sc > score:
            best, score = f, sc
    if not best:
        return None
    out = dest.with_suffix(".png")
    out.write_bytes(_get(best.get("thumburl") or best["url"]))
    return out


def _logo_simpleicons(brand: str, dest: Path) -> Path | None:
    try:
        svg = _get(f"https://cdn.jsdelivr.net/npm/simple-icons@13.21.0/icons/{''.join(_toks(brand))}.svg")
    except Exception:
        return None
    out = dest.with_suffix(".svg")
    out.write_bytes(svg)
    return out


def fetch_logo(lib: Path, brand: str) -> Path | None:
    dest = lib / _slug(brand)
    for ext in (".png", ".svg"):
        if dest.with_suffix(ext).exists():
            return dest.with_suffix(ext)
    for src in (_logo_commons, _logo_simpleicons):
        try:
            got = src(brand, dest)
        except Exception as e:
            print(f"   ⚠ logo {brand} ({src.__name__[6:]}): {str(e)[:80]}"); got = None
        if got:
            print(f"   ⬇ logo {brand} → {got.name}")
            return got
    return None


# ---------- photos ----------

def _photos_pexels(q: str, n: int) -> list[str]:
    key = os.environ.get("PEXELS_API_KEY")
    if not key:
        return []
    d = _json(f"https://api.pexels.com/v1/search?orientation=landscape&per_page={n}&query=" + urllib.parse.quote(q), {"Authorization": key})
    return [p["src"]["large2x"] for p in d.get("photos", [])]


def _on_topic(q: str, text: str) -> bool:
    """Open archives rank loosely (a desert snapshot for "two people talking"): keep a hit only if
    its title / tags carry every meaningful word of the query. No picture beats a wrong one."""
    want = {t for t in _toks(q) if len(t) > 2}
    return want <= set(_toks(text))


def _photos_openverse(q: str, n: int) -> list[str]:
    d = _json("https://api.openverse.org/v1/images/?aspect_ratio=wide&size=large&mature=false&category=photograph"
              f"&page_size=20&q=" + urllib.parse.quote(q))
    return [r["url"] for r in d.get("results", []) if r.get("url", "").lower().endswith((".jpg", ".jpeg"))
            and _on_topic(q, r.get("title", "") + " " + " ".join(t.get("name", "") for t in r.get("tags") or []))][:n]


def _photos_commons(q: str, n: int) -> list[str]:
    fs = _commons_files(f"filetype:bitmap {q}", 30, 1600)
    return [f["thumburl"] for f in fs if f["mime"] == "image/jpeg" and f["width"] >= f["height"] and _on_topic(q, f["title"])][:n]


def fetch_photos(dest: Path, q: str, n: int) -> list[Path]:
    dest.mkdir(parents=True, exist_ok=True)
    have = sorted(dest.glob(f"{_slug(q)}-*.jpg"))
    if len(have) >= n:
        return have[:n]
    words = q.split()
    # the full query first, then shorter ones: "storyboard sketch panels" → "storyboard sketch"
    tries = [(src, " ".join(words[:k])) for k in range(len(words), max(1, len(words) - 2), -1)
             for src in (_photos_pexels, _photos_openverse, _photos_commons)]
    for src, qq in tries:
        try:
            urls = src(qq, n)
        except Exception as e:
            print(f"   ⚠ ảnh \"{qq}\" ({src.__name__[8:]}): {str(e)[:80]}"); urls = []
        out = []
        for k, u in enumerate(urls):
            f = dest / f"{_slug(q)}-{k + 1}.jpg"
            try:
                raw = dest / f"_{f.stem}.bin"
                raw.write_bytes(_get(u))
                # re-encode: some hosts send webp/png under .jpg, and 4K stock photos bloat the props
                run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-vf", "scale='min(1600,iw)':-2", "-q:v", "3", str(f)])
                raw.unlink()
                out.append(f)
            except Exception as e:
                print(f"   ⚠ tải ảnh lỗi: {str(e)[:60]}")
        if len(out) >= min(2, n):
            print(f"   ⬇ ảnh \"{qq}\" ×{len(out)} ({src.__name__[8:]})")
            return out
        for f in out:
            f.unlink()
    return []


# ---------- spot ----------

def spot(project: Path, plan: list[dict], words: list[dict], align: dict) -> list[dict]:
    from .captions import timed_words_for
    from .judge import ask, _extract_json
    blocks, total = [], 0.0
    for it in plan:
        al = align.get(it["id"])
        # logos and photos are graphics, and graphics only go full screen: MOTION talks only
        if it["type"] != "talk" or it.get("mode") != "motion" or not al or al.get("start") is None:
            continue
        ws = timed_words_for(it, words, al)
        total += al.get("kept") or (al["end"] - al["start"])
        lines = [f"[{ws[k]['s']:.0f}s] " + " ".join(w["w"] for w in ws[k:k + 12]) for k in range(0, len(ws), 12)]
        blocks.append(f"## {it['id']}\n" + "\n".join(lines))
    if not blocks:
        return []
    n = max(1, round(total / EVERY))
    text, _ = ask(project, SPOT.format(n=n), "\n\n".join(blocks), max_tokens=3000)
    out = _extract_json(text).get("visuals", [])
    photos = [v for v in out if v.get("kind") == "photo"][:n]
    return [v for v in out if v.get("kind") == "logo"] + photos


# ---------- step ----------

def main(project: Path, force: bool = False) -> None:
    cfg = load_project(project); load_env(project)
    work = project / "work"
    plan = read_json(work / "plan.json")
    out = work / "visuals"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.json"):
        old.unlink()
    auto = work / "visuals_auto.json"
    if not (cfg.get("visuals") or {}).get("auto", True):
        print("visuals: tắt (project.json → visuals.auto = false)"); return
    if force or not auto.exists():
        words = read_json(work / "words.json")
        align = {a["id"]: a for a in read_json(work / "align.json")}
        try:
            write_json(auto, spot(project, plan, words, align))
        except Exception as e:
            print(f"⚠ AI chưa chọn được hình minh hoạ ({str(e)[:80]})")
            write_json(auto, [])
    lib = logo_library(project, cfg)
    per: dict[str, list[dict]] = {}
    seen: set[str] = set()
    n_photo = 0
    motion = {it["id"] for it in plan if it.get("type") == "talk" and it.get("mode") == "motion"}
    for v in read_json(auto):
        if not v.get("id") or not v.get("at") or v["id"] not in motion:
            continue
        if v.get("kind") == "logo":
            brand = v.get("brand", "").strip()
            if not brand or brand.lower() in seen:
                continue
            seen.add(brand.lower())
            f = fetch_logo(lib, brand)
            if not f:
                print(f"⚠ không tìm được logo {brand} — bỏ qua"); continue
            scene = {"template": "logo", "secs": LOGO_SECS, "props": {"src": str(f), "name": brand}}
        elif v.get("kind") == "photo" and v.get("q"):
            tpl = PHOTO_TPL[n_photo % len(PHOTO_TPL)]
            fs = fetch_photos(project / "assets" / "auto", v["q"], 8 if tpl in ("wall", "swipe") else 4)
            if not fs:
                print(f"⚠ không tìm được ảnh \"{v['q']}\" — bỏ qua"); continue
            n_photo += 1
            cap = {"kicker": v.get("caption", "")} if tpl == "swipe" else {"caption": v.get("caption", "")}
            scene = {"template": tpl, "secs": PHOTO_SECS, "props": {"images": [str(x) for x in fs], **cap}}
        else:
            continue
        per.setdefault(v["id"], []).append({"at": v["at"], **scene})
    for tid, vs in per.items():
        write_json(out / f"{tid}.json", vs)
    _sheet(work, [x for vs in per.values() for x in vs])
    print(f"→ {sum(len(v) for v in per.values())} hình tự chèn trong {len(per)} đoạn · kho logo: {lib}")


def _sheet(work: Path, items: list[dict]) -> None:
    """First picture of every auto visual in work/visuals_sheet.jpg — look before you ship."""
    if not items:
        return
    d = work / "visuals" / "sheet"; d.mkdir(parents=True, exist_ok=True)
    for old in d.glob("*.jpg"):
        old.unlink()
    k = 0
    for it in items:
        src = it["props"].get("src") or it["props"]["images"][0]
        if src.endswith(".svg"):
            continue   # ffmpeg cannot read SVG; Remotion draws it
        k += 1
        # logos are often black on transparent: lay them on white, a JPEG would turn the alpha black
        run(["ffmpeg", "-v", "error", "-y", "-i", src, "-f", "lavfi", "-i", "color=white:s=480x270", "-frames:v", "1", "-filter_complex",
             "[0:v]scale=440:250:force_original_aspect_ratio=decrease[a];[1:v][a]overlay=(W-w)/2:(H-h)/2", str(d / f"{k:03d}.jpg")])
        print(f"   {k}. {it['template']} @\"{it['at']}\" — {it['props'].get('name') or it['props'].get('caption', '')}")
    if k:
        cols = min(4, k); rows = -(-k // cols)
        run(["ffmpeg", "-v", "error", "-y", "-framerate", "1", "-i", str(d / "%03d.jpg"), "-vf", f"tile={cols}x{rows}", "-frames:v", "1", str(work / "visuals_sheet.jpg")])
