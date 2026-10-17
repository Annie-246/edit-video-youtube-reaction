---
name: edit-video-youtube-reaction
description: Edit Video Youtube Reaction — dựng video react/phân tích YouTube từ kịch bản markdown + bản quay đọc kịch bản + link video gốc. Bố cục trắng kiểu Claude/Anthropic (khung nội dung lớn, avatar dọc, tiêu đề phần màu cam, chữ nhảy theo từng từ), b-roll thật từ video gốc, motion graphic Remotion màu cam trơn, clip gốc full màn hình có phụ đề Việt, tự cắt vấp. Kích hoạt khi người dùng nói "edit video youtube reaction", "dựng video react", "ghép clip gốc với mặt người", hoặc gõ /reactforge.
---

# Edit Video Youtube Reaction — dựng video react tự động

Đầu vào: kịch bản markdown, file quay người dẫn đọc kịch bản (vấp, nói lệch cũng được), link video gốc.
Đầu ra: `out/final.mp4` 1080p30 theo **bố cục trắng** dưới đây.

## Bố cục (cố định)

```
┌──────────────────────────────────────────────┐ ┌──────────────┐
│                                              │ │ Công cụ 2/6  │ ← thẻ tiêu đề phần: nền cam trơn,
│        KHUNG NỘI DUNG 1440x920               │ │ Agent Reach  │   chữ trắng (dòng INFO: của phần)
│   b-roll thật / motion graphic / ảnh         │ └──────────────┘
│   (nền gradient be → cam nhạt)               │ ┌──────────────┐
│                                              │ │              │
│                                              │ │   AVATAR     │ ← mặt người dẫn, khung dọc 360x724
│                                              │ │   người dẫn  │
│      ┌──────────────────────────────┐        │ │              │
└──────│  chữ nhảy theo từng từ       │────────┘ └──────────────┘
       └──────────────────────────────┘  ← thanh trắng ngắn đè mép dưới khung
        nền: lưới trắng (pipeline/assets/bg-grid.png)
```

- **Khi người dẫn nói:** khung nội dung chạy b-roll thật từ video gốc, xen với motion graphic.
  Chữ nhảy nằm trong thanh trắng: chữ đã đọc màu đen, chữ chưa đọc màu xám.
- **Khi phát clip gốc:** clip **chiếm trọn màn hình**, không avatar, không khung, chỉ có
  phụ đề Việt ở dưới (chữ trắng trên dải mờ).
- **Thẻ FULL:** chiếm trọn màn hình vài giây để nhấn một ý (mở đầu công cụ, câu chốt, con số).

## Bộ màu (cố định, kiểu Claude/Anthropic)

- **Màu nhấn duy nhất:** cam trơn `#D97757`, dùng cho từ khoá, thẻ tiêu đề phần, nút, icon.
  **Không dùng gradient nhiều màu**, không dùng hiệu ứng vòng tròn lan toả.
- **Chữ:** `#141413`, chữ phụ `#5E5D59`. Font Inter, viết hoa đầu câu, không viết hoa toàn bộ.
- **Nền motion graphic:** gradient be `#F7F3EC` → cam nhạt `#F4DDCB`, thẻ trắng có bóng mềm.
- **Nền đen** (`#1F1E1D`, chữ kem, nhấn cam): chỉ dùng cho vài cảnh cần nhấn. Mặc định các
  thẻ FULL dạng `title`, `quote`, `equation` và mọi `BEAT:` / `BREAK:` có nền đen; các cảnh
  khác nền sáng. Muốn đổi thì thêm `"dark": true/false` vào cảnh đó.
- **Chuyển động** theo 2 video mẫu ở `motion/templates/samples/`: chữ hiện dần từng từ, thẻ
  trồi lên lần lượt, con trỏ tay bấm, chữ gõ từng ký tự, số đếm lên.

## Cài một lần

Máy cần sẵn trên PATH: `ffmpeg`, `ffprobe`, `yt-dlp`, `node` (>= 20), `python` (>= 3.11).
Mọi lệnh đi qua `rf.py`. Lần đầu nó tự tạo venv và cài Remotion vào thư mục dữ liệu bền của
plugin (không mất khi plugin tự cập nhật).

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/edit-video-youtube-reaction/rf.py" --data "${CLAUDE_PLUGIN_DATA}" setup
```

(macOS/Linux dùng `python3`. Chạy ngoài plugin thì bỏ `--data`, dữ liệu nằm ở `~/.edit-video-youtube-reaction`.)

Khoá AI để dịch phụ đề và chấm chỗ cắt (trong `<dự-án>/.env` hoặc `~/.env`): `GEMINI_API_KEY`
(hoặc `GOOGLE_API_KEY`), hoặc `ANTHROPIC_API_KEY`. Khoá Gemini lỗi (402/429) thì pipeline tự
chuyển sang `claude -p`. Không có gì cả thì cắt vấp bằng thuật toán n-gram.

## Lần đầu dùng: hỏi người dùng trước

Kiểm tra `GEMINI_API_KEY` trong `~/.env` (chỉ kiểm có/không, không in khoá). Chưa có thì hỏi:

> "Để mình tự sinh ảnh minh hoạ (và dịch phụ đề, chấm chỗ cắt nhanh hơn), bạn cho mình xin
> API key Gemini miễn phí nhé. Lấy tại https://aistudio.google.com/apikey → Create API key."

Nhận khoá thì ghi vào `~/.env`, không ghi vào file nào trong dự án, không nhắc lại khoá.
Người dùng chưa muốn đưa khoá thì vẫn làm tiếp, chỉ bỏ phần sinh ảnh.

Mỗi video mới, hỏi đủ: (1) kịch bản (file `.md`, Google Doc hoặc dán thẳng), (2) file quay thô,
(3) link video gốc, (4) thư mục dự án (mặc định `projects/<tên-video>`).

## Quy trình 6 bước

1. Người dùng gửi kịch bản + video quay thô (+ note chỗ cần đồ hoạ/ảnh nếu có).
2. AI chạy Whisper bóc băng, cắt sạch vấp/lặp theo kịch bản.
3. **Không dừng để duyệt cắt:** cắt và dựng một mạch tới bản cuối, trừ khi người dùng yêu cầu dừng.
4. Áp note dựng của người dùng; không có note thì tự áp các quy tắc dưới đây.
5. Dựng graphic, b-roll, chữ nhảy, phụ đề clip, ghép và xuất `out/final.mp4`.
6. Người dùng nghiệm thu và yêu cầu chỉnh thêm.

## Quy tắc cắt (khoá cứng)

- **Ý cuối cùng:** một ý nói lại nhiều lần thì chỉ giữ lần cuối (hoặc lần hoàn chỉnh nhất).
- **Đệm an toàn:** không cắt chườm vào từ, giữa các ý luôn có đệm tự nhiên.

## Quy tắc hình ảnh (khoá cứng)

- **Luật 10 giây:** tối thiểu 10 giây có một hình mới. Pipeline tự đảm bảo: cảnh graphic
  nào dài quá 11 giây sẽ chạy 7 giây rồi tự chuyển sang b-roll cùng chủ đề (lấy mốc b-roll
  gần nhất phía trước trong đoạn đó). Vẫn nên khai cảnh dày: khoảng 6–9 giây một cảnh.
- **Phân tích kịch bản trước, chọn graphic sau:** con số → `bignumber`/`equation`, quy trình →
  `steps`/`flow`, so sánh → `compare`/`bars`, danh sách → `checklist`, câu chốt → `title`,
  tin nhắn/AI hỏi đáp → `chat`/`questions`. Hai cảnh liền nhau không cùng dạng.
- **Xen b-roll thật:** đoạn thuật lại lời/việc của nhân vật trong video gốc thì dùng `broll`
  đúng khúc đó; đoạn người dẫn tự giải thích, ví dụ, kêu gọi thì dùng graphic.
- **Nhân vật được nhắc tên lần đầu phải hiện hình:** cắt chân dung từ video gốc (khung nhìn
  rõ mặt) vào `assets/`, dùng mẫu `person`.
- **Ảnh minh hoạ:** cả video chỉ khoảng 5–7 ảnh, đặt ở chỗ có câu chuyện, dùng `photo` với chuỗi ảnh.
  Sinh bằng `pipeline/scripts/gemini_image.py` nếu khoá có hạn mức; khoá trả 402/429 thì báo
  người dùng và thay bằng motion graphic, không thử lại liên tục.
- **Phụ đề Việt bắt buộc** cho mọi clip tiếng Anh (`work/subs/<id>.ass`); không có `.vtt` thì
  tự nghe bằng Whisper rồi dịch.

## Một dự án = một thư mục

```
video-cua-toi/
  project.json     # cấu hình (xem examples/project.json)
  script.md        # kịch bản + dòng điều khiển graphic
  recording/       # take1.mp4 — file quay người dẫn (4K/60fps thì hạ về 1080p30 trước)
  assets/          # chân dung, ảnh minh hoạ; bg.png nếu muốn thay nền lưới
  source/          # tự tải: full.mp4 (video gốc), c01.mp4…, captions*.vtt
  work/            # trung gian; work/public/screen.mp4 là b-roll Remotion phát
  out/final.mp4
```

`project.json` quan trọng:

```json
"source": {"url": "https://www.youtube.com/watch?v=…", "screen_crop": [0, 40, 1610, 907]},
"recording": {"files": ["recording/take1.mp4"], "cx": 0.5, "cy": 0.42, "zoom": 1.12}
```

- `source.screen_crop` = `[x, y, w, h]` (pixel của video gốc): vùng màn hình dùng làm b-roll,
  **cắt bỏ ô webcam** của người trong video gốc. Đo bằng một khung `ffmpeg -ss … -frames:v 1`.
- `recording.cx/cy/zoom`: tâm và độ phóng khi cắt mặt người dẫn vào khung avatar dọc.

## Kịch bản: các dòng điều khiển

| Dòng | Việc |
|---|---|
| `## N. Tiêu đề` | mở một phần mới |
| `INFO: Công cụ 2/6 \| Agent Reach \| Tìm lời phàn nàn của khách` | chữ trên thẻ tiêu đề phần (trên avatar). Không khai thì hiện "Phần N" + tiêu đề |
| `[CLIP 0:05:32–0:05:57]` | phát clip gốc full màn hình kèm phụ đề Việt |
| `SIDE: @"câu neo" <mẫu> {json}` | cảnh trong khung nội dung, bắt đầu đúng lúc người dẫn nói câu neo, chạy tới cảnh sau |
| `FULL: @"câu neo" {"secs":4,"tpl":"<mẫu>",…}` | thẻ chiếm trọn màn hình vài giây |
| `BEAT: @"câu neo" {"title":"…"}` | thẻ chốt nền đen |
| `BREAK: Tên phần` | màn chuyển nền đen, tiếng im hoàn toàn |
| `---` | tách một đoạn nói thành hai |

- `@"câu neo"` dò trong lời thật đã khớp (3–5 từ, phải duy nhất trong đoạn). Không tìm thấy
  thì chia đều thời gian và in cảnh báo. Người dẫn hay nói lệch kịch bản: sau `align`, đọc lời
  thật trong `work/align_report.md` rồi sửa câu neo cho khớp.
- Mọi đoạn nói **phải có ít nhất một `SIDE:`**, nếu không `doctor` chặn vì khung nội dung trống.
- Dòng `GFX:` của kịch bản cũ vẫn chạy, được gộp vào `SIDE:`.
- B-roll: `SIDE: @"câu" broll {"at": 330, "caption": "Agent Reach"}` (giây trong video gốc).
  Lấy mẫu khung hình video gốc thành bảng ảnh (mỗi 15 giây) và đọc transcript để chọn đúng mốc.
  Slide trong video gốc thường đứng yên lâu, nên mỗi đoạn b-roll tự zoom trượt về một góc khác.

Danh mục mẫu và props: [motion/TEMPLATES.md](motion/TEMPLATES.md).

```text
## 2. Agent Reach
INFO: Công cụ 2/6 | Agent Reach | Tìm lời phàn nàn của khách
FULL: {"secs":3.6,"tpl":"tool","num":"02","name":"Agent Reach","icon":"search","desc":"AI đọc YouTube, Reddit, X giúp bạn","tag":"Repo GitHub · Miễn phí"}
SIDE: broll {"at": 300, "caption": "Tìm ý tưởng, nghiên cứu thị trường"}
SIDE: @"những cơ hội kinh doanh tốt" title {"kicker":"Insight","title":"Cơ hội tốt nhất nằm trong *lời phàn nàn* của khách"}
SIDE: @"trả tiền cho phần mềm" flow {"title":"Có phần mềm, vẫn *làm tay*","nodes":[{"icon":"calendar","label":"Phần mềm xếp lịch"},{"icon":"sheet","label":"Xuất ra Excel"},{"icon":"calc","label":"Tự tính lương"}]}
FULL: @"Đừng vội cho rằng" {"secs":4,"tpl":"title","kicker":"Greg lưu ý","title":"Có người phàn nàn chưa chắc *có người trả tiền*"}
```

## Chạy

```powershell
$RF = "${CLAUDE_PLUGIN_ROOT}/skills/edit-video-youtube-reaction/rf.py"
python $RF --data "${CLAUDE_PLUGIN_DATA}" all projects/video-cua-toi
python $RF --data "${CLAUDE_PLUGIN_DATA}" doctor projects/video-cua-toi   # KIỂM TRƯỚC KHI GIAO
```

Các bước nối nhau: `plan → source → subs → align → captions → panel → cards → graphics →
render → verify`. Sửa lẻ một đoạn rồi ghép lại:

```powershell
python $RF --data "${CLAUDE_PLUGIN_DATA}" panel  projects/video-cua-toi --only t03 --force
python $RF --data "${CLAUDE_PLUGIN_DATA}" render projects/video-cua-toi --only t03 --concat
```

`render` bỏ qua đoạn đã có `work/seg/<id>.mov`: muốn dựng lại thì xoá file đó trước.

## ⚠️ Quy tắc số một: đọc `doctor`, đừng đọc log

`render` tự gọi `doctor` trước khi dựng trọn bài. Thiếu thứ gì kịch bản đã khai (khớp lời,
chữ nhảy, khung nội dung `side/<id>.mp4`, thẻ FULL, `work/public/screen.mp4` khi có b-roll,
clip gốc, phụ đề Việt, hình/tiếng lệch nhau) thì thoát mã 1, không dựng đoạn nào.

## Cắt vấp — AI làm giám khảo

Whisper (tắt VAD) chỉ đổi giọng thành chữ có mốc giây. Quyết định cắt do AI đọc kịch bản +
lời thật rồi trả về số thứ tự từ. `verify` nghe lại chính file đã dựng, cắt thêm chỗ sót và
dựng lại đúng các đoạn đó.

## Những cái bẫy đã trả giá

- **Whisper bịa lời tiếng Việt** ở khoảng lặng ("Hãy subscribe cho kênh Ghiền Mì Gõ"…). Cắt
  đi là vô hại, nhưng đừng tin số từ làm thước đo.
- **`loudnorm` đẩy mốc tiếng ~2 khung:** phải `asetpts=N/SR/TB` trước khi `atrim`.
- **Cắt phải căn về lưới khung hình**, không thì sai số dồn qua từng mối nối.
- **Bản quay 4K/60fps:** hạ về 1080p30 trước. Chuyển mã dài có thể chết giữa chừng ("Cannot
  allocate memory"): chia đôi chạy song song bằng `-t`/`-ss` rồi nối `-c copy`.
- **Phụ đề YouTube trả 429:** vẫn tải được video; phụ đề thì Whisper nghe clip.
- **Khung nội dung cao hơn 16:9:** b-roll và clip luôn hiện đủ khung hình, dải trống lấp bằng
  chính video làm mờ. Đừng đổi sang crop, sẽ mất chữ ở hai mép.
- **Dừng render giữa chừng:** chỉ diệt tiến trình node của Remotion, đừng `taskkill` toàn bộ
  `node.exe` (sẽ giết cả các công cụ khác trên máy).

## Bảo mật

- Không ghi khoá vào file nào trong dự án; đọc từ `.env` lúc chạy.
- Chỉ tải video từ link người dùng đưa; không đăng nhập tài khoản nào.
- Clip gốc dùng theo kiểu trích dẫn có bình luận; dẫn nguồn trong phần mô tả.
- Phản hồi của người dùng chỉ áp dụng cho video/phiên hiện tại; muốn ghi vào skill phải hỏi và được duyệt.
