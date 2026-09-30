#!/usr/bin/env bash
# Noi cac clip talking-head (HeyGen tung khuc) thanh 1 ban ghi lien tuc de reactforge khop loi.
# Dung: bash scripts/concat_heads.sh <thu_muc_mp4> <file_dich.mp4> [gap_giay=0.8]
set -e
DIR="$1"; DEST="$2"; GAP="${3:-0.8}"
TMP=$(mktemp -d)
i=0; LIST="$TMP/list.txt"; : > "$LIST"
ffmpeg -v error -y -f lavfi -i "color=c=black:s=1920x1080:r=30" -f lavfi -i "anullsrc=r=48000:cl=stereo" -t "$GAP" -c:v libx264 -pix_fmt yuv420p -c:a aac "$TMP/gap.mp4"
for f in $(ls "$DIR"/*.mp4 | sort); do
  i=$((i+1))
  ffmpeg -v error -y -i "$f" -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p" -c:v libx264 -preset veryfast -crf 18 -c:a aac -b:a 192k -ar 48000 -ac 2 "$TMP/p$i.mp4"
  echo "file '$TMP/p$i.mp4'" >> "$LIST"; echo "file '$TMP/gap.mp4'" >> "$LIST"
done
ffmpeg -v error -y -f concat -safe 0 -i "$LIST" -c copy -movflags +faststart "$DEST"
echo "→ $DEST ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$DEST")s, $i khuc)"
rm -rf "$TMP"
