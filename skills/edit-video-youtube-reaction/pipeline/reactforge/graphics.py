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
    # White layout (this project): one big 16:9 frame on the left for b-roll / graphics / clips,
    # the presenter in a portrait card top-right, word captions under the big frame.
    main = {"x": r(40), "y": r(40), "w": e(1440), "h": e(920), "r": r(30)}
    head = {"x": r(1520), "y": r(236), "w": e(360), "h": e(724), "r": r(26)}
    return {
        "w": r(1920), "h": r(1080), "s": s,
        "left": dict(main), "main": dict(main), "side": dict(main),
        # source clips play full screen, no presenter, no frame
        "clip": {"x": 0, "y": 0, "w": r(1920), "h": r(1080), "r": 0},
        "head": dict(head), "pip": dict(head),
        # Only frames with the presenter sit on the white grid. BUBBLE: the scenes in one big rounded
        # card (orange gradient rim, soft shadow underneath), presenter in a small card on the right.
        # MOTION has no presenter: the scenes fill the screen.
        "screen": {"bubble": {"x": r(40), "y": r(40), "w": e(1500), "h": e(1000), "r": r(30)},
                   "motion": {"x": 0, "y": 0, "w": r(1920), "h": r(1080), "r": 0}},
        "bubble": {"x": r(1562), "y": r(300), "w": e(336), "h": e(400), "r": r(28)},
        # MOTION: the presenter in a small round bubble, bottom-right, over the full-screen graphics
        "dot": {"d": e(270), "m": r(56), "rim": max(2, r(7))},
        "rim": max(2, r(5)), "shadow": {"dy": r(20), "blur": r(22), "alpha": 0.36},
        "info": {"x": r(1520), "y": r(40), "w": e(360), "h": e(176), "r": r(24)},
        # word captions sit in a short white pill straddling the bottom edge of the main frame
        "cap": {"x": r(260), "y": r(921), "w": e(1000), "h": e(78), "r": r(39)},
        "text_y": r(600),
        "panel": {"x": r(40), "y": r(40), "w": e(900), "h": e(478), "r": r(24)},
        "label": {"x": r(76), "y": r(76)},
        "note": {"x": r(76), "y": r(560), "w": r(820)},
        "sub_font": r(52), "sub_margin": r(56),
        "bg": "#FFFFFF",
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


GRAD = "#D97757"  # solid Claude orange


def frame_html(L: dict, info_kicker: str, info_title: str, info_sub: str = "", footer: str = "") -> str:
    """Transparent overlay: white borders + soft shadows around the main frame and the presenter
    card, and the small info card under the presenter (current tool / source)."""
    s = L["s"]; m, h, inf, cp = L["main"], L["head"], L["info"], L["cap"]
    bw, hb = int(8 * s), int(6 * s)
    info = ""
    if info_title:
        info = f"""<div class="info"><div class="k"><span class="dot"></span>{H.escape(info_kicker)}</div>
<div class="t">{H.escape(info_title)}</div>{'<div class="s">' + H.escape(info_sub) + '</div>' if info_sub else ''}</div>"""
    return f"""<html><head><meta charset="utf-8"><style>{_font_css()}
html,body{{margin:0;width:{L['w']}px;height:{L['h']}px;background:transparent;overflow:hidden;font-family:'NotionInter',sans-serif}}
.fr{{position:absolute;box-sizing:border-box;border:{bw}px solid #fff;border-radius:{m['r'] + bw}px;
box-shadow:0 {int(18*s)}px {int(50*s)}px rgba(80,50,30,.20),0 0 0 1px rgba(217,119,87,.10)}}
.hd{{position:absolute;box-sizing:border-box;border:{hb}px solid #fff;border-radius:{h['r'] + hb}px;
box-shadow:0 {int(14*s)}px {int(40*s)}px rgba(80,50,30,.22),0 0 0 1px rgba(217,119,87,.12)}}
.info{{position:absolute;left:{inf['x']}px;top:{inf['y']}px;width:{inf['w']}px;height:{inf['h']}px;box-sizing:border-box;padding:{int(22*s)}px {int(26*s)}px;
display:flex;flex-direction:column;justify-content:center;background:{GRAD};border-radius:{inf['r']}px;
box-shadow:0 {int(16*s)}px {int(40*s)}px rgba(217,119,87,.35)}}
.k{{display:flex;align-items:center;gap:{int(8*s)}px;font-size:{int(20*s)}px;font-weight:600;color:rgba(255,255,255,.88);line-height:1.3}}
.dot{{width:{int(10*s)}px;height:{int(10*s)}px;border-radius:50%;background:#fff}}
.t{{margin-top:{int(4*s)}px;font-size:{int(40*s)}px;font-weight:800;letter-spacing:-.02em;line-height:1.24;padding-bottom:2px;color:#fff}}
.s{{margin-top:{int(2*s)}px;font-size:{int(19*s)}px;color:rgba(255,255,255,.9);line-height:1.35}}
.cp{{position:absolute;left:{cp['x']}px;top:{cp['y']}px;width:{cp['w']}px;height:{cp['h']}px;border-radius:{cp['r']}px;background:#fff;
box-shadow:0 {int(12*s)}px {int(34*s)}px rgba(80,50,30,.18),0 0 0 1px rgba(217,119,87,.14);display:flex;align-items:center;justify-content:center;gap:{int(10*s)}px;
font-size:{int(22*s)}px;font-weight:600;color:#5E5D59}}
.cp .dot{{background:{GRAD}}}
</style></head><body>
<div class="fr" style="left:{m['x']-bw}px;top:{m['y']-bw}px;width:{m['w']+2*bw}px;height:{m['h']+2*bw}px"></div>
<div class="hd" style="left:{h['x']-hb}px;top:{h['y']-hb}px;width:{h['w']+2*hb}px;height:{h['h']+2*hb}px"></div>
{info}
<div class="cp">{'<span class="dot"></span>' + H.escape(footer) if footer else ''}</div>
</body></html>"""


def section_info(item: dict) -> tuple[str, str, str]:
    """Title card text: the section's INFO: line, else "Phần N" + the section heading."""
    if item.get("info"):
        k, t, sub = item["info"]
        return k, t or item.get("title", ""), sub
    num = str(item.get("section", ""))
    return ("Mở đầu" if num == "0" else (f"Phần {num}" if num else "")), item.get("title", ""), ""


def talk_fg_html(L: dict, item: dict, still, accent: str, left_window: bool) -> str:
    k, t, sub = section_info(item)
    return frame_html(L, k, t, sub)


def clip_fg_html(L: dict, item: dict, accent: str) -> str:
    """Clips play full screen; nothing is drawn over them except their subtitles."""
    return f"<html><body style='margin:0;width:{L['w']}px;height:{L['h']}px;background:transparent'></body></html>"


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
    for name, box in (("mask_head", L["head"]), ("mask_left", L["left"]), ("mask_clip", L["clip"]), ("mask_pip", L["pip"]), ("mask_panel", L["panel"]), ("mask_side", L["side"]), ("mask_main", L["main"])):
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
