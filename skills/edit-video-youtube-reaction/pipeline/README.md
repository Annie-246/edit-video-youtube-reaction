# reactforge — pipeline

Logic dựng của skill `edit-video-youtube-reaction`. Hướng dẫn dùng và quy chuẩn ở
[../SKILL.md](../SKILL.md); mẫu đồ hoạ ở [../motion/TEMPLATES.md](../motion/TEMPLATES.md).

| Bước | Module | Làm gì |
|---|---|---|
| plan | `script_parser.py` | kịch bản → `work/plan.json` (đoạn nói, clip, break; SIDE/FULL/INFO) |
| source | `source.py` | tải video gốc, cắt clip, dựng `work/public/screen.mp4` (b-roll, crop webcam) |
| subs | `subs.py` | phụ đề Việt cho clip (vtt hoặc Whisper → dịch) |
| align | `align.py`, `judge.py` | Whisper nghe bản quay, khớp kịch bản, AI chấm chỗ cắt → `work/align.json` |
| captions | `captions.py` | chữ nhảy theo từ (ASS) trong thanh trắng dưới khung nội dung |
| panel | `panel.py` | dòng SIDE → cảnh Remotion `Main` cho khung nội dung; luật 10 giây tự tách cảnh |
| cards | `cards.py` | thẻ FULL / BEAT / BREAK (Remotion `Main` 1920x1080) |
| graphics | `graphics.py` | lớp khung: viền, thẻ tiêu đề phần, thanh chữ; mask bo góc |
| render | `render.py` | ghép từng đoạn bằng ffmpeg rồi nối `out/final.mp4` |
| verify | `verify.py` | nghe lại bản dựng, cắt thêm chỗ sót, dựng lại đúng đoạn đó |
| doctor | `doctor.py` | chặn render nếu thiếu thứ kịch bản đã khai |

Bố cục (toạ độ) nằm ở `graphics.layout_for`. Remotion ở `../motion/src/light/`.
