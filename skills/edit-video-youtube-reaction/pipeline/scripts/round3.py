import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from reactforge import captions, panel, render, verify
P = pathlib.Path(sys.argv[1]).resolve()
ids = sys.argv[2].split(",")
allc = []
for tid in ids:
    ch, lines = verify.check_round(P, 3, "medium", only=tid)
    for l in lines:
        print(" ", l, flush=True)
    allc += ch
if allc:
    print("dựng lại:", allc, flush=True)
    captions.main(P)
    for tid in allc:
        panel.main(P, only=tid, force=True)
        render.main(P, only=tid)
    render.concat_only(P)
    print("đã nối lại final.mp4", flush=True)
else:
    print("VÒNG 3 SẠCH — không còn chỗ nào phải cắt", flush=True)
