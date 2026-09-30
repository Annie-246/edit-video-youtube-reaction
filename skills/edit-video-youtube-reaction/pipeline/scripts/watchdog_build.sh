#!/usr/bin/env bash
# Warn on Telegram if the full build has not finished after N seconds (default 3h). Detached.
LOG="$1"; LIMIT="${2:-10800}"
sleep "$LIMIT"
if ! grep -q "=== DONE" "$LOG" 2>/dev/null; then
  LAST=$(tail -2 "$LOG" 2>/dev/null | tr '\n' ' ' | cut -c1-200)
  "$HOME/video_bot/.venv/bin/python" "$HOME/reactforge/scripts/tg_send.py" "⚠️ Dựng trọn quá 3 tiếng chưa xong. Dòng log cuối: $LAST — xem $LOG"
fi
