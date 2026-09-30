#!/usr/bin/env bash
# Build one reactforge project end-to-end (whisper → Claude cuts → subs → panels → render), notify via Telegram,
# then optionally put the Mac to sleep. Runs detached; log in <project>/work/full.log.
# Usage: bash scripts/full_build.sh projects/<name> [--sleep]
set -u
cd "$HOME/reactforge"
P="$1"; SLEEP="${2:-}"
PY="$HOME/video_bot/.venv/bin/python"
LOG="$P/work/full.log"; mkdir -p "$P/work"
notify() { "$PY" scripts/tg_send.py "$1" >/dev/null 2>&1 || true; }
{
echo "=== FULL BUILD $(date '+%F %T') ==="
"$PY" -m reactforge plan "$P"
rm -f "$P/work/words.json" "$P/work/words_raw.json" "$P/work/align.json" "$P/work/silences.json" "$P/work/silences_fine.json" "$P/work/concat.txt"
rm -rf "$P/work/captions" "$P/work/panel" "$P/work/seg" "$P/work/judge"
( "$PY" -m reactforge source "$P" > "$P/work/source.log" 2>&1; echo "source exit $?" >> "$P/work/source.log" ) &
SRC=$!
echo "--- align: whisper 40 phút (VAD tắt) + nghe lại vùng nuốt + Claude chấm cắt  $(date +%T)"
"$PY" -m reactforge align "$P" || { notify "❌ Dựng trọn LỖI ở bước align, xem $P/work/full.log"; exit 1; }
echo "--- chờ tải clip  $(date +%T)"; wait $SRC; tail -3 "$P/work/source.log"
"$PY" -m reactforge source "$P" >> "$P/work/source.log" 2>&1 || true   # retry anything that failed
echo "--- subs  $(date +%T)"; "$PY" -m reactforge subs "$P" || echo "subs lỗi, tiếp tục"
echo "--- panel  $(date +%T)"; "$PY" -m reactforge panel "$P" || echo "panel lỗi, tiếp tục"
echo "--- graphics  $(date +%T)"; "$PY" -m reactforge graphics "$P"
echo "--- render  $(date +%T)"; "$PY" -m reactforge render "$P" || { notify "❌ Dựng trọn LỖI ở bước render, xem $P/work/full.log"; exit 1; }
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$P/out/final.mp4"); DI=${DUR%.*}
echo "--- final ${DUR}s  $(date +%T)"
cp "$P/out/final.mp4" "$HOME/Desktop/react-video-ai/260907-alex-hormozi-FULL-1080p.mp4"
ffmpeg -v error -y -ss 300 -t 90 -i "$P/out/final.mp4" -vf scale=1280:720 -c:v h264_videotoolbox -b:v 2500k -allow_sw 1 -c:a aac -b:a 128k -movflags +faststart "$P/out/sample_90s.mp4"
CUTS=$("$PY" -c "import json;a=json.load(open('$P/work/align.json'));t=[x for x in a if x.get('start') is not None];print(f\"{len(t)}/{len(a)} đoạn khớp, cắt {sum((x['end']-x['start'])-x.get('kept',x['end']-x['start']) for x in t):.0f}s\")")
"$PY" scripts/tg_send.py --video "$P/out/sample_90s.mp4" "✅ DỰNG TRỌN xong: $((DI/60)):$(printf '%02d' $((DI%60))) · $CUTS. Đây là mẫu 90s từ phút 5. File 1080p: Desktop/react-video-ai/260907-alex-hormozi-FULL-1080p.mp4 · báo cáo cắt: reactforge/$P/work/align_report.md"
echo "=== DONE $(date '+%F %T') ==="
} >> "$LOG" 2>&1
if [ "$SLEEP" = "--sleep" ]; then sync; sleep 30; pmset sleepnow; fi
