"""Render overlay PNGs (foreground graphics + rounded-corner masks) from HTML via Playwright."""
from __future__ import annotations
import base64, html as H
from pathlib import Path
from .common import load_project, read_json, FONT_DIR, run

BASE_W = 1920


def layout_for(width: int) -> dict:
    s = width / BASE_W
    def r(x): return int(round(x * s))
    def e(x):  # even size (yuv420 needs even w/h)
        v = int(round(x * s)); return v - (v % 2)
    return {
        "w": r(1920), "h": r(1080), "s": s,
        "left": {"x": r(32), "y": r(32), "w": e(900), "h": e(506), "r": r(24)},
        "text_y": r(600),
        "head": {"x": r(964), "y": r(32), "w": e(924), "h": e(1016), "r": r(28)},
        "clip": {"x": r(40), "y": r(40), "w": e(1540), "h": e(866), "r": r(24)},
        "pip": {"x": r(1616), "y": r(830), "w": e(272), "h": e(154), "r": r(16)},
        "panel": {"x": r(32), "y": r(570), "w": e(900), "h": e(478), "r": r(24)},
        "side": {"x": r(32), "y": r(32), "w": e(900), "h": e(1016), "r": r(28)},
        "label": {"x": r(72), "y": r(72)},
        "note": {"x": r(72), "y": r(560), "w": r(820)},
        "sub_font": r(54), "sub_margin": r(36),
        "bg": "#0B0B10",
    }


def _font_css() -> str:
    def b64(p): return base64.b64encode((FONT_DIR / p).read_bytes()).decode()
    inter_b64 = b64('Inter-Variable.ttf') if (FONT_DIR / 'Inter-Variable.ttf').exists() else b64('BeVietnamPro-Regular.ttf')
    return (f"@font-face{{font-family:'NotionInter';src:url(data:font/ttf;base64,{inter_b64});font-weight:100 900;font-display:block}}"
            f"@font-face{{font-family:'BVP';src:url(data:font/ttf;base64,{b64('BeVietnamPro-Bold.ttf')});font-weight:700}}"
            f"@font-face{{font-family:'BVP';src:url(data:font/ttf;base64,{b64('BeVietnamPro-Regular.ttf')});font-weight:400}}")


def _img_data(path: Path) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()


COL = {"dung": ("#22C55E", "ĐÚNG"), "sai": ("#EF4444", "SAI"), "c3": ("#F59E0B", "CỘT 3"), "du_bao": ("#60A5FA", "CHƯA CHẤM")}


def talk_fg_html(L: dict, item: dict, still: Path | None, accent: str, left_window: bool) -> str:
    s = L["s"]; lf, tx = L["left"], L["text_y"]
    sl = item["slide"]
    bullets = item.get("bullets")
    if bullets is None:
        st = item.get("score_state", {})
        bullets = []
        for col in ("dung", "sai", "c3", "du_bao"):
            for claim in st.get(col, [])[-2:]:
                bullets.append((col, claim))
        bullets = bullets[-4:]
        bullets_html = "".join(f'<li><span class="sq" style="background:{COL[c][0]}"></span><b style="color:{COL[c][0]}">{COL[c][1]}</b> — {H.escape(t)}</li>' for c, t in bullets)
    else:
        bullets_html = "".join(f'<li><span class="sq" style="background:{accent}"></span>{H.escape(b)}</li>' for b in bullets)
    left = "" if left_window or still is None or item.get("side") else f'<img class="still" src="{_img_data(still)}">'
    if item.get("gfx") or item.get("side"):  # an animated Panel or Side replaces the static text block
        return f"""<html><head><meta charset="utf-8"><style>{_font_css()}
html,body{{margin:0;width:{L['w']}px;height:{L['h']}px;background:transparent;overflow:hidden}}
.still{{position:absolute;left:{lf['x']}px;top:{lf['y']}px;width:{lf['w']}px;height:{lf['h']}px;object-fit:cover;border-radius:{lf['r']}px;filter:brightness(.55) saturate(.8)}}
</style></head><body>{left}</body></html>"""
    return f"""<html><head><meta charset="utf-8"><style>{_font_css()}
html,body{{margin:0;width:{L['w']}px;height:{L['h']}px;background:transparent;overflow:hidden}}
body{{font-family:'NotionInter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#fff}}
.still{{position:absolute;left:{lf['x']}px;top:{lf['y']}px;width:{lf['w']}px;height:{lf['h']}px;object-fit:cover;border-radius:{lf['r']}px;filter:brightness(.55) saturate(.8)}}
.kicker{{position:absolute;left:{lf['x']}px;top:{tx}px;font-size:{int(22*s)}px;letter-spacing:.08em;color:{accent};opacity:.95;font-weight:600}}
.kw{{position:absolute;left:{lf['x']}px;top:{tx+int(36*s)}px;width:{lf['w']}px;font-size:{int(58*s)}px;line-height:1.24;font-weight:700;letter-spacing:-.01em;padding:4px 0 8px 0;background:linear-gradient(90deg,{accent},#C4B5FD);-webkit-background-clip:text;color:transparent}}
.sub{{position:absolute;left:{lf['x']}px;top:{tx+int(36*s)}px;width:{lf['w']}px;font-size:{int(26*s)}px;line-height:1.35;color:rgba(255,255,255,.85)}}
ul{{position:absolute;left:{lf['x']}px;width:{lf['w']}px;list-style:none;margin:0;padding:0;font-size:{int(28*s)}px;line-height:1.45}}
li{{display:flex;gap:{int(14*s)}px;align-items:baseline;margin-bottom:{int(8*s)}px}}
.sq{{display:inline-block;width:{int(18*s)}px;height:{int(18*s)}px;border-radius:{int(4*s)}px;flex:none;position:relative;top:{int(2*s)}px}}
</style></head><body>{left}
<div class="kicker">{H.escape(sl.get('kicker',''))}</div>
<div class="kw" id="kw">{H.escape(sl.get('keyword',''))}</div>
<div class="sub" id="sub">{H.escape(sl.get('sub',''))}</div>
<ul id="ul">{bullets_html}</ul>
<script>
const kw=document.getElementById('kw'),sub=document.getElementById('sub'),ul=document.getElementById('ul');
let fs={int(58*s)};while(kw.scrollHeight>{int(240*s)}&&fs>{int(34*s)}){{fs-=2;kw.style.fontSize=fs+'px'}}
let y=kw.offsetTop+kw.offsetHeight+{int(14*s)};sub.style.top=y+'px';ul.style.top=(y+(sub.textContent?sub.offsetHeight+{int(22*s)}:{int(6*s)}))+'px';
</script></body></html>"""


def clip_fg_html(L: dict, item: dict, accent: str) -> str:
    s = L["s"]; lb = L["label"]
    label = item.get("label") or ""
    pill = (f'<div class="pill"><span class="dot"></span>{H.escape(label)}</div>' if label else "")
    return f"""<html><head><meta charset="utf-8"><style>{_font_css()}
html,body{{margin:0;width:{L['w']}px;height:{L['h']}px;background:transparent;overflow:hidden}}
.pill{{position:absolute;left:{lb['x']}px;top:{lb['y']}px;display:flex;align-items:center;gap:{int(10*s)}px;padding:{int(8*s)}px {int(16*s)}px;border-radius:{int(8*s)}px;background:rgba(10,10,16,.78);color:#fff;font:600 {int(22*s)}px 'NotionInter',sans-serif;letter-spacing:.08em;backdrop-filter:blur(6px)}}
.dot{{width:{int(12*s)}px;height:{int(12*s)}px;border-radius:50%;background:{accent}}}
</style></head><body>{pill}</body></html>"""


def note_html(L: dict, text: str) -> str:
    s = L["s"]; n = L["note"]
    return f"""<html><head><meta charset="utf-8"><style>{_font_css()}
html,body{{margin:0;width:{L['w']}px;height:{L['h']}px;background:transparent;overflow:hidden}}
.card{{position:absolute;left:{n['x']}px;top:{n['y']}px;width:{n['w']}px;background:#fff;color:#111;border-radius:{int(14*s)}px;padding:{int(18*s)}px {int(24*s)}px;font-family:'NotionInter',sans-serif;box-shadow:0 {int(10*s)}px {int(40*s)}px rgba(0,0,0,.45)}}
.h{{display:flex;align-items:center;gap:{int(10*s)}px;font-size:{int(20*s)}px;font-weight:700;letter-spacing:.08em;color:#1D4ED8;margin-bottom:{int(8*s)}px}}
.h:before{{content:'';width:{int(14*s)}px;height:{int(14*s)}px;border-radius:50%;background:#1D4ED8}}
.t{{font-size:{int(28*s)}px;line-height:1.35}}
</style></head><body><div class="card"><div class="h">Kiểm chứng</div><div class="t">{H.escape(text)}</div></div></body></html>"""



def break_html(L: dict, title: str, accent: str, kicker: str) -> str:
    """Full-frame chapter card. Black, silent, a beat of rest between sections."""
    s = L["s"]
    return f"""<html><head><meta charset="utf-8"><style>{_font_css()}
html,body{{margin:0;width:{L['w']}px;height:{L['h']}px;background:{L['bg']};overflow:hidden}}
body{{font-family:'NotionInter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center}}
.k{{font-size:{int(24*s)}px;letter-spacing:.14em;color:{accent};font-weight:600;margin-bottom:{int(24*s)}px}}
.t{{font-size:{int(76*s)}px;font-weight:700;line-height:1.24;text-align:center;max-width:{int(1500*s)}px;letter-spacing:-.01em;padding:8px 0}}
.r{{margin-top:{int(38*s)}px;width:{int(180*s)}px;height:{int(6*s)}px;border-radius:{int(3*s)}px;background:linear-gradient(90deg,{accent},#C4B5FD)}}
</style></head><body><div class="k">{H.escape(kicker)}</div><div class="t">{H.escape(title)}</div><div class="r"></div></body></html>"""


def full_html(L: dict, props: dict, accent: str) -> str:
    """Full-frame card that takes over the split layout — used to let a question land."""
    s = L["s"]
    kick = H.escape(props.get("kicker", ""))
    sub = H.escape(props.get("sub", ""))
    return f"""<html><head><meta charset="utf-8"><style>{_font_css()}
html,body{{margin:0;width:{L['w']}px;height:{L['h']}px;background:{L['bg']};overflow:hidden}}
body{{font-family:'NotionInter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;
background:radial-gradient(120% 90% at 50% 0%,#16162a 0%,{L['bg']} 60%)}}
.k{{font-size:{int(24*s)}px;letter-spacing:.14em;color:{accent};font-weight:600;margin-bottom:{int(26*s)}px}}
.t{{font-size:{int(74*s)}px;font-weight:700;line-height:1.24;text-align:center;max-width:{int(1440*s)}px;letter-spacing:-.01em;padding:8px 0;
background:linear-gradient(90deg,#fff 55%,{accent});-webkit-background-clip:text;color:transparent}}
.s{{margin-top:{int(30*s)}px;font-size:{int(30*s)}px;line-height:1.35;color:rgba(255,255,255,.80);text-align:center;max-width:{int(1200*s)}px}}
</style></head><body>
{'<div class="k">' + kick + '</div>' if kick else ''}
<div class="t" id="t">{H.escape(props.get('title',''))}</div>
{'<div class="s">' + sub + '</div>' if sub else ''}
<script>const t=document.getElementById('t');let fs={int(74*s)};
while(t.scrollHeight>{int(560*s)}&&fs>{int(36*s)}){{fs-=2;t.style.fontSize=fs+'px'}}</script>
</body></html>"""


def mask_html(w: int, h: int, r: int) -> str:
    return f"<html><body style='margin:0;background:#000;width:{w}px;height:{h}px;overflow:hidden'><div style='width:{w}px;height:{h}px;border-radius:{r}px;background:#fff'></div></body></html>"


def render_all(project: Path, only: str | None = None) -> None:
    from playwright.sync_api import sync_playwright
    cfg = load_project(project); accent = cfg["style"]["accent"]
    L = layout_for(cfg["output"]["width"])
    # A source that carries its own permanent lower-third collides with our clip label;
    # move ours out of the way per project rather than shifting the layout for everyone.
    if (cfg.get("style") or {}).get("label_xy"):
        x, y = cfg["style"]["label_xy"]
        L["label"] = {"x": int(round(x * L["s"])), "y": int(round(y * L["s"]))}
    plan = read_json(project / "work" / "plan.json")
    g = project / "work" / "gfx"; g.mkdir(parents=True, exist_ok=True)
    clips_meta = read_json(project / "source" / "clips.json") if (project / "source" / "clips.json").exists() else {}
    thumb = project / "source" / "thumb.jpg"
    # stills: first frame of each clip (for the talk slide that follows it)
    last_still = thumb if thumb.exists() else None
    jobs: list[tuple[Path, str, int, int]] = []
    # extract a still for every clip first, so early talk items can fall back to the first clip's still
    for it in plan:
        if it["type"] != "clip": continue
        src = project / "source" / clips_meta.get(it["id"], {}).get("file", f"{it['id']}.mp4")
        still = g / f"{it['id']}_still.jpg"
        if src.exists() and not still.exists():
            off = clips_meta.get(it["id"], {}).get("offset", 0.0)
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{off + 1.0:.2f}", "-i", str(src), "-frames:v", "1", "-q:v", "3", str(still)])
        if last_still is None and still.exists():
            last_still = still
    for it in plan:
        if it["type"] == "clip":
            src = project / "source" / clips_meta.get(it["id"], {}).get("file", f"{it['id']}.mp4")
            still = g / f"{it['id']}_still.jpg"
            if src.exists() and not still.exists():
                off = clips_meta.get(it["id"], {}).get("offset", 0.0)
                run(["ffmpeg", "-v", "error", "-y", "-ss", f"{off + 1.0:.2f}", "-i", str(src), "-frames:v", "1", "-q:v", "3", str(still)])
            if still.exists(): last_still = still
            it["_still"] = still
            if not only or only == it["id"]:
                jobs.append((g / f"{it['id']}_fg.png", clip_fg_html(L, it, accent), L["w"], L["h"]))
                if it.get("note"):
                    jobs.append((g / f"{it['id']}_note.png", note_html(L, it["note"]), L["w"], L["h"]))
        elif it["type"] == "talk":
            it["_still"] = last_still
            screen = (project / "screens" / f"{it['id']}.mp4").exists()
            if not only or only == it["id"]:
                jobs.append((g / f"{it['id']}_fg.png", talk_fg_html(L, it, last_still, accent, left_window=screen), L["w"], L["h"]))
                from .panel import parse_full
                for k, line in enumerate(it.get("full") or []):
                    f = parse_full(line)
                    if f:
                        jobs.append((g / f"{it['id']}_full{k}.png", full_html(L, f["props"], accent), L["w"], L["h"]))
        elif it["type"] == "break":
            if not only or only == it["id"]:
                kick = f"PHẦN {it['section']}" if it.get("section") else ""
                jobs.append((g / f"{it['id']}_break.png", break_html(L, it["title"], accent, kick), L["w"], L["h"]))
    for name, box in (("mask_head", L["head"]), ("mask_left", L["left"]), ("mask_clip", L["clip"]), ("mask_pip", L["pip"]), ("mask_panel", L["panel"]), ("mask_side", L["side"])):
        jobs.append((g / f"{name}.png", mask_html(box["w"], box["h"], box["r"]), box["w"], box["h"]))
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": L["w"], "height": L["h"]}, device_scale_factor=1)
        for out, html_s, w, h in jobs:
            tmp = g / (out.stem + ".html"); tmp.write_text(html_s, encoding="utf-8")
            pg.set_viewport_size({"width": w, "height": h})
            pg.goto(tmp.resolve().as_uri()); pg.wait_for_timeout(150)
            # masks and the full-frame cards are opaque by design; the overlay layers are not
            opaque = out.name.startswith("mask_") or "_break" in out.name or "_full" in out.name
            pg.screenshot(path=str(out), omit_background=not opaque, clip={"x": 0, "y": 0, "width": w, "height": h})
            tmp.unlink(missing_ok=True)
        b.close()
    print(f"{len(jobs)} ảnh đồ hoạ → {g}")
