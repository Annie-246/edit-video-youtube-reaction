from __future__ import annotations
import argparse, sys
from pathlib import Path


def main(argv=None):
    ap = argparse.ArgumentParser(prog="reactforge", description="Dựng video react: mặt người + clip gốc + đồ hoạ")
    ap.add_argument("cmd", choices=["plan", "source", "subs", "align", "captions", "panel", "graphics", "render", "concat", "verify", "all", "doctor", "cards", "voice"])
    ap.add_argument("project", type=Path)
    ap.add_argument("--only", help="chỉ dựng 1 item (vd t03, c02)")
    ap.add_argument("--concat", action="store_true", help="tự động nối lại file cuối (tiện khi dùng kèm --only)")
    ap.add_argument("--force", action="store_true", help="làm lại bước này dù đã có kết quả")
    ap.add_argument("--rounds", type=int, default=2, help="verify: số vòng kiểm tra tối đa")
    ap.add_argument("--vmodel", default="medium", help="verify: model whisper nghe lại bản dựng")
    a = ap.parse_args(argv)
    p = a.project.resolve()
    if a.cmd == "doctor":
        from . import doctor
        doctor.main(p)
        return
    from . import cards, script_parser, source, subs, align, captions, panel, graphics, render, verify, voice
    steps = {"plan": lambda: script_parser.main(p), "source": lambda: source.main(p), "subs": lambda: subs.main(p, a.force),
             "align": lambda: align.main(p, a.force), "captions": lambda: captions.main(p), "panel": lambda: panel.main(p, a.only, a.force),
             "voice": lambda: voice.main(p, force=a.force), "cards": lambda: cards.main(p, a.only, a.force), "graphics": lambda: graphics.render_all(p, a.only),
             "render": lambda: render.main(p, a.only, concat=(not a.only or a.concat)), "concat": lambda: render.concat_only(p),
             "verify": lambda: verify.main(p, rounds=a.rounds, only=a.only, model=a.vmodel)}
    if a.cmd == "all":
        for k in ("plan", "source", "subs", "align", "captions", "panel", "cards", "graphics", "render", "verify"):
            print(f"── {k}"); steps[k]()
    else:
        steps[a.cmd]()


if __name__ == "__main__":
    main()
