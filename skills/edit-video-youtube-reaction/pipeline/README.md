# reactforge — dựng video react tự động

Đầu vào: kịch bản markdown (từ skill `/react-script`), bản ghi hình anh đọc kịch bản (nói lệch chút cũng được), link video gốc.
Đầu ra: `out/final.mp4` 1080p — bố cục kiểu Thanh Trần: khi anh nói thì **chia đôi màn hình** (trái: khung hình video gốc + chữ khoá + bảng điểm; phải: mặt anh), khi phát clip gốc thì **clip full khung + phụ đề Việt + mặt anh thu nhỏ góc phải + nhãn + thẻ kiểm chứng**.

## Cài 1 lần
```bash
bash setup.sh            # cần sẵn ffmpeg, yt-dlp, node
```
Khoá Claude để dịch phụ đề: `ANTHROPIC_API_KEY` trong `<project>/.env` hoặc `~/.env` (không có thì giữ tiếng Anh).

## Một dự án = một thư mục
```
my-video/
  project.json     # cấu hình (xem examples/zitron-test/project.json)
  script.md        # kịch bản — có [CLIP mm:ss–mm:ss], **Anh (x:xx):**, **Bảng điểm:**
  recording/       # take1.mp4 (một hoặc nhiều file, đọc theo thứ tự kịch bản)
  screens/         # tuỳ chọn: t03.mp4 = quay màn hình cho đoạn t03 (thay khung trái)
  source/          # tự tải: c01.mp4… + captions + thumb
  work/            # trung gian (plan, align, subs, gfx, seg)
  out/final.mp4
```

## Chạy
```bash
PY=.venv/bin/python
$PY -m reactforge plan     my-video   # kịch bản → work/plan.json (xem lại thứ tự talk/clip)
$PY -m reactforge source   my-video   # tải đúng các đoạn clip cần (yt-dlp) + phụ đề gốc
$PY -m reactforge subs     my-video   # dịch phụ đề Việt cho từng clip → .ass
$PY -m reactforge align    my-video   # whisper nghe bản ghi → khớp từng đoạn → work/align_report.md (ĐỌC!) + tự sinh captions
$PY -m reactforge captions my-video   # chữ nhảy theo từng từ khi anh nói → work/captions/tXX.ass (chạy lại sau khi sửa align.json)
$PY -m reactforge panel    my-video   # đồ hoạ chuyển động góc dưới trái từ các dòng GFX: (Remotion) → work/panel/tXX.mp4
$PY -m reactforge cards    my-video   # thẻ toàn màn hình FULL:/BEAT:/BREAK: (Remotion) → work/cards/*.mp4
$PY -m reactforge graphics my-video   # HTML → PNG (slide, nhãn, thẻ kiểm chứng, mặt nạ bo góc)
$PY -m reactforge render   my-video   # ffmpeg dựng từng đoạn → nối → out/final.mp4
$PY -m reactforge all      my-video   # cả chuỗi bước
$PY -m reactforge doctor   my-video   # KIỂM TRƯỚC KHI GIAO — thoát mã 1 nếu thiếu thứ gì
$PY -m reactforge render   my-video --only t03   # dựng lại 1 đoạn
```

## Kịch bản: các dòng điều khiển (tuỳ chọn)
- Trong đoạn nói: `SLIDE: chữ khoá | dòng nhỏ trên | dòng phụ` và `BULLETS: a; b; c` (không có thì lấy tiêu đề mục + bảng điểm tích luỹ).
- Sau dòng `[CLIP …]`: `LABEL: DỰ BÁO` (nhãn góc trái) và `NOTE: …` (thẻ kiểm chứng hiện 8 giây cuối clip).
- `[MÀN HÌNH: …]` → nếu có file `screens/<id>.mp4` thì khung trái phát màn hình đó suốt đoạn.

## Cách quay để khớp tốt
- Đọc theo đúng thứ tự kịch bản, mỗi đoạn nghỉ ~1 giây. Lệch/thừa/thiếu từ không sao — khớp mờ theo từ.
- Quay ngang 16:9; mặt ở giữa hoặc chỉnh `recording.cx` (0 = trái, 1 = phải) trong project.json.
- Nhiều file take → liệt kê theo thứ tự trong `recording.files`.
- Xem `work/align_report.md`: đoạn nào khớp < 50% thì đọc lại đoạn đó rồi chạy `align --force`.

## Đã kiểm chứng thật (03/09/2026)
Dự án `examples/zitron-test`: 3 đoạn nói (giọng máy đọc kịch bản có lệch từ) + 2 clip Ed Zitron 720p → whisper khớp 83–94%, phụ đề dịch bằng Claude, render 1080p bằng videotoolbox trong 75 giây cho 222 giây video.

## Chữ nhảy theo lời (captions)
- Khi anh nói, dưới ô mặt có dòng chữ chạy từng từ (karaoke ASS `\k`): từ đang nói đổi sang màu accent, từ chưa nói màu trắng mờ.
- Chữ lấy từ **kịch bản** (đúng chính tả), thời gian lấy từ whisper. Chỗ anh nói khác kịch bản nhiều (ad-lib) thì hiện đúng lời whisper nghe được; từ đệm ngắn ("à", "ờ") bỏ qua.
- Chỉnh cỡ chữ/màu/vị trí trong `reactforge/captions.py` (`build_ass`), chỉnh cách ngắt dòng bằng `MAX_WORDS`, `MAX_CHARS`, `GAP_BREAK`.
- Bản ghi 4K/60fps nên chuyển về 1080p30 trước khi render (nhanh gấp nhiều lần): `ffmpeg -hwaccel videotoolbox -i take.mp4 -vf scale=1920:1080,fps=30 -c:v h264_videotoolbox -b:v 16M -c:a aac work/recording.mp4`.

## Cắt vấp (align) — Claude làm giám khảo
- Whisper chỉ chuyển giọng thành chữ có mốc giây (chạy **tắt VAD** + không nối ngữ cảnh, nếu không whisper sẽ "nuốt" câu đọc hụt). Quyết định cắt do **Claude** (`reactforge/judge.py`, model `claude-opus-5`, đổi bằng `REACTFORGE_JUDGE_MODEL`): đọc kịch bản + lời thật (từng từ có số thứ tự, kèm ghi chú quãng nghỉ / "có tiếng không ra chữ" đo từ audio), trả về các khoảng cắt theo **số thứ tự từ** (không bịa mốc giây) với lý do: đọc lại · đọc hụt · sửa lời · đệm · ngoài lề. Giữ lần đọc cuối, không cắt lặp có chủ ý / nói lệch trôi chảy / cách đọc số. Kết quả thô ở `work/judge/tXX.json`, ghi chú "👀 Claude lưu ý" trong `align_report.md` (vd. câu kết lửng cần quay bù).
- Tắt Claude (dùng thuật toán n-gram): `"cut_judge": "off"` trong project.json; không có `ANTHROPIC_API_KEY` thì tự rơi về thuật toán. Chi phí ≈ 9k token vào / 1k ra cho 1 đoạn 4 phút.
- Im lặng > 1s (đo bằng ffmpeg silencedetect, `work/silences.json`) co còn 0,4s; quãng có tiếng mà không ra chữ ≥ 0,7s cắt ("lẩm bẩm").

## (cũ) Cắt vấp bằng thuật toán
- `align` so lời whisper với kịch bản: đoạn anh đọc lại (từ ngữ trùng với kịch bản ngay quanh đó, dài ≥ 0,45s) và im lặng > 1s bị đánh dấu cắt; cắt đặt giữa hai từ nên rơi vào chỗ im lặng. Kết quả `keep` (các khoảng giữ) ghi trong `work/align.json`, danh sách chỗ cắt trong `work/align_report.md` — **đọc mục "Chỗ đã cắt"** trước khi render; cắt nhầm thì sửa tay `keep` rồi chạy `captions`, `panel`, `render --only tXX`.
- Tắt hẳn: `"clean_cuts": false` trong project.json. Ngưỡng ở đầu `reactforge/align.py` (`MIN_CUT`, `MAX_GAP`, `GAP_KEEP`, `HIT_RATIO`).
- Chữ nhảy và Panel đều tính theo mốc thời gian SAU khi cắt.

## Cổng kiểm tra (`doctor`) — chạy tự động trước mỗi lần render trọn bài

Pipeline này từng **hỏng êm**: đoạn nào thiếu dữ liệu thì in một dòng log rồi dựng tiếp. Đó là
cách ba phút đầu của một video 32 phút đi ra ngoài với khung trái đứng im — log có ghi, không ai đọc.

`reactforge/doctor.py` đối chiếu từng item trong plan với thứ nó đã khai và **chặn** nếu thiếu:

- đoạn nói: có align, có captions, có panel nếu khai `GFX:`, có thẻ nếu khai `FULL:`/`BEAT:`
- **ảnh chạy khung trái: nếu một số đoạn có mà đoạn khác không → LỖI** (chính là bug đã ship)
- clip: có file gốc, có phụ đề Việt (cảnh báo riêng nếu phụ đề còn nguyên tiếng Anh)
- màn chuyển: có hình
- đoạn đã dựng: hình và tiếng phải bằng nhau tới mili giây

`render` gọi `doctor.preflight()` khi dựng trọn bài (không gọi khi `--only`, vì lúc đó là cố ý dựng lẻ).
Thiếu thứ gì thì thoát **mã 1** và không dựng đoạn nào.

## Thẻ toàn màn hình: `FULL:` · `BEAT:` · `BREAK:`

Ba thứ dùng chung composition `Card` (Remotion, 1920×1080, nền sao + quầng sáng theo màu kênh),
chỉ khác giọng điệu:

```
BREAK: Việc thứ nhất — Để AI tự chấm bài
FULL: @"càng mở nhiều AI" {"secs":3.6,"kicker":"CÂU HỎI 1","title":"Vì sao càng mở nhiều AI…?"}
BEAT: @"vẫn một mình bạn" {"secs":3.2,"title":"Sau tất cả, vẫn một mình bạn ngồi duyệt…","emoji":"😮‍💨"}
```

- `BREAK:` đứng riêng một dòng ngay sau tiêu đề `## N.` → một cảnh riêng, **tiếng im hoàn toàn**,
  dài theo `output.break_secs` (mặc định 2,6 giây). Vừa báo phần mới, vừa cho tai nghỉ.
- `FULL:` nằm trong đoạn nói → che trọn khung trong `secs` giây kể từ lúc người dẫn nói tới `@"câu"`.
- `BEAT:` y hệt `FULL:` nhưng đặt sẵn `style":"beat"` — chữ nghiêng, to hơn, có chỗ cho một emoji.
  Tên khác là để người **viết kịch bản** biết đây là chỗ cho một câu đọng lại, không phải thêm thông tin.

Không có node/Remotion thì tự rơi về ảnh tĩnh PNG do `graphics.py` sinh.


## Đồ hoạ góc dưới trái (Panel, Remotion)
- Trong đoạn nói, thêm các dòng `GFX:`; khi có GFX thì khối chữ tĩnh (kicker/chữ khoá/bullets) được thay bằng Panel chuyển động 900×478 ở góc dưới trái, ảnh tĩnh clip vẫn ở góc trên trái.
  ```
  GFX: card {"kicker":"MỞ MÀN","title":"Alex Hormozi","sub":"Đừng chạy theo AI"}
  GFX: @"16 doanh nghiệp" bignumber {"kicker":"ACQUISITION.COM","value":250,"unit":"triệu đô/năm","headline":"16 doanh nghiệp","sub":"≈ 18 tỷ mỗi ngày"}
  GFX: @"11 trợ lý ảo" compare {"headline":"…","rows":[{"label":"11 trợ lý ảo","value":11000,"display":"11.000 đô"},{"label":"Hệ thống AI","value":350000,"display":"350.000 đô","highlight":true}],"footnote":"…"}
  ```
  `@"câu"` = cảnh bắt đầu đúng lúc anh nói tới câu đó (tìm trong lời thật); không có thì cảnh đầu bắt đầu từ 0, các cảnh không tìm thấy câu được chia đều. Mẫu chữ: `card` · `bignumber` · `list` (items) · `quote` (text, sub) · `compare` (rows label/value/display/highlight) · `twoline` (first, second).
  Mẫu **hình vẽ** (minh hoạ ý, thay vì chiếu lại ảnh chụp nguồn): `bots` (count, you, headline, sub) · `browser` (tiles, highlight, caption) · `dashboard` (points[], headline, rows[{label,value}]) · `flow` (steps[]). Kèm `kicker` tuỳ chọn cho mọi mẫu.
- Mã Panel ở `~/remotion-explainer/src/Panel.tsx` (composition `Panel`, kích thước/fps/màu lấy từ props). Đổi thư mục Remotion bằng `REMOTION_DIR`. Render 12s mất ~8s trên M4.
- Parser cũng đọc được kịch bản kiểu Google Doc của Thảo: `## **N. Tiêu đề**`, dòng `**CLIP h:mm:ss–h:mm:ss.** mô tả`, đoạn văn không cần `**Anh (x:xx):**` (tự thành đoạn nói), dòng `**→ ghi chú**` bị bỏ qua.

## Kiểm tra sau khi dựng (verify) — bắt buộc trước khi giao
```bash
$PY -m reactforge verify my-video            # 2 vòng, tự dựng lại đoạn có cắt mới
$PY scripts/verify_rebuild.py my-video       # kiểm 1 vòng → dựng lại TOÀN BỘ → kiểm vòng 2 → Telegram
```
- Vòng cắt đầu chỉ nhìn bản ghi gốc, nên cắt hụt là còn nguyên trong bản dựng. Bước này **nghe lại chính file đã dựng** (`work/seg/tXX.mov`), dò cụm lặp gần nhau mà kịch bản không lặp, rồi để Claude quyết chỗ nào thật sự phải cắt thêm; cắt được trừ trên trục thời gian ĐÃ CẮT rồi ánh xạ ngược về bản ghi gốc (`verify.out_to_src`).
- Kết quả: `work/verify_report.md` (cắt thêm gì, 👀 Claude lưu ý gì), `work/verify/tXX.judge.json` (thô).
- Whisper vẫn khử lặp ở bước này, nên `listen()` dùng lại `refine_words` — nếu không sẽ "nghe" thấy bản dựng sạch trong khi thực tế còn lặp.

## Khớp hình–tiếng
- Video chỉ cắt được tại biên khung, audio cắt tại mẫu bất kỳ. Nếu để nguyên, mỗi mối nối lệch tới 1 khung (33ms) và **dồn lại trong đoạn** — 13 mối nối là gần nửa giây, đúng triệu chứng "tiếng lệch hình" nghe được ở giữa bài.
- `render_talk` snap mọi mốc `keep` về lưới khung (`q()`), chốt độ dài đoạn theo số khung nguyên (`-frames:v`), và ép audio dài đúng bằng đó (`apad` + `atrim=end`). `render_clip` làm tương tự.
- Kiểm nhanh: `ffprobe -select_streams v:0/a:0 -show_entries stream=duration` trên từng `work/seg/*.mov` — chênh phải ≤ 1 khung.

## Khi API hết credit
`judge.ask()` tự chuyển sang gọi `claude -p --model opus` (tính vào gói Claude Code, không tốn credit API). Ép dùng CLI: `REACTFORGE_FORCE_CLI=1`.
