---
name: edit-video-youtube-reaction
description: Edit Video Youtube Reaction — dựng video react/phân tích YouTube từ kịch bản markdown + bản quay đọc kịch bản + link video gốc. Tự cắt vấp, chữ nhảy theo từng từ, phụ đề Việt cho clip, đồ hoạ động Remotion, thẻ toàn màn hình và màn chuyển phần. Dùng khi cần biến một buổi quay talking-head thành video hoàn chỉnh. Kích hoạt khi người dùng nói "edit video youtube reaction", "dựng video react", "ghép clip gốc với mặt người", "làm video kiểu Thanh Trần", hoặc gõ /reactforge.
---

# Edit Video Youtube Reaction — dựng video react tự động

Đầu vào: kịch bản markdown, file quay bạn đọc kịch bản (nói lệch, vấp cũng được), link video gốc.
Đầu ra: `out/final.mp4` 1080p — khi bạn nói thì **chia đôi màn hình** (trái: hình minh hoạ +
đồ hoạ động; phải: mặt bạn + chữ nhảy theo từng từ), khi phát clip gốc thì **clip full khung +
phụ đề Việt + mặt bạn thu nhỏ góc phải**.

## Cài một lần

Máy cần sẵn trên PATH: `ffmpeg`, `ffprobe`, `yt-dlp`, `node` (>= 20), `python` (>= 3.11).
Mọi lệnh đều đi qua `rf.py`. Lần đầu nó tự tạo venv + cài Remotion vào thư mục dữ liệu bền
của plugin (không mất khi plugin tự cập nhật); các lần sau chỉ cài lại khi thư viện đổi.

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/edit-video-youtube-reaction/rf.py" --data "${CLAUDE_PLUGIN_DATA}" setup
```

(macOS/Linux dùng `python3`. Chạy ngoài plugin thì bỏ `--data`, dữ liệu nằm ở `~/.edit-video-youtube-reaction`.)

Khoá AI để dịch phụ đề và chấm chỗ cắt (đặt trong `<dự-án>/.env` hoặc `~/.env`):
- **Tối ưu nhất với Antigravity**: Đặt `GEMINI_API_KEY` (hoặc `GOOGLE_API_KEY`) — chạy siêu nhanh, rẻ, không bị lỗi token và dịch tiếng Việt cực chuẩn.
- Hoặc dùng **Claude**: Đặt `ANTHROPIC_API_KEY` hoặc dùng CLI `claude -p`.
- Không có khoá thì pipeline tự động rơi về thuật toán n-gram cắt vấp cục bộ.

## Quy trình phối hợp 6 bước (Bắt buộc)

1. **Bước 1 (Gửi đầu vào):** Người dùng gửi kịch bản (`script.md`) + video quay thô (`recording/take1.mp4`). Trong kịch bản có note các đoạn cần chèn đồ họa, hình ảnh đặc biệt.
2. **Bước 2 (AI Cắt thô):** AI chạy Whisper bóc băng, phân tích và cắt sạch vấp/lặp theo kịch bản.
3. **Bước 3 (Người dùng duyệt Cắt - Checkpoint 1):** AI gửi báo cáo các đoạn cắt cho người dùng duyệt xem nhịp điệu và nội dung đã chuẩn chưa. **DỪNG tại đây, không tự dựng đồ họa cho tới khi người dùng duyệt cắt.**
4. **Bước 4 (Nhận Note dựng):** Người dùng duyệt cắt và gửi thêm note dựng, yêu cầu chèn Motion Graphic hoặc hình minh họa. (Nếu không note, AI tự động áp dụng quy tắc mặc định: tối thiểu mỗi 10s có 1 đồ họa/minh họa mới).
5. **Bước 5 (AI Dựng hoàn chỉnh):** AI thiết kế và render Motion Graphic (3-5s), chèn ảnh minh họa (dùng Gemini nếu có yêu cầu), căn chỉnh phụ đề, ghép toàn bộ và xuất `out/final.mp4`.
6. **Bước 6 (Nghiệm thu):** Người dùng kiểm tra bản cuối và yêu cầu tinh chỉnh thêm nếu cần.

## Quy tắc Cắt gọt (Khóa cứng)

- **Nguyên tắc Ý cuối cùng:** Một ý người nói có thể nói lại vài lần $\rightarrow$ **chỉ giữ lại đoạn nói cuối cùng** (hoặc ý hoàn chỉnh nhất). Tuyệt đối không để lặp lại ý trong video.
- **Đệm an toàn (Không nuốt chữ):** Không được cắt chườm vào từ. Kết thúc mỗi ý và chuyển đoạn phải có khoảng đệm tự nhiên từ từ cuối đến phần sau, không cắt quá sát làm mất âm đầu/đuôi.

## Quy tắc Đồ hoạ & Nhịp điệu hình ảnh (Khóa cứng)

- **Quy tắc 10 giây:** Tối thiểu **mỗi 10 giây phải có một graphic hoặc minh họa mới**, không để khung hình đứng yên quá lâu gây nhàm chán.
- **Motion Graphic (React / Remotion, 3-5s):**
  - Mô tả đúng nội dung kịch bản, trực quan, logic, không rối mắt.
  - **Linh hoạt kết hợp 3 kiểu xuất hiện:**
    1. *Góc nhỏ bên trái phía dưới (`GFX:`):* Kích thước 900x478, nửa trên để màn hình/ảnh/b-roll, nửa phải là người nói.
    2. *1/2 Màn hình bên cạnh người nói (`SIDE:`):* Kích thước 900x1016, chiếm trọn toàn bộ nửa bên trái bên cạnh người nói, tối ưu cho quy trình dọc (bước 1-2-3), timeline, danh sách trọng tâm, biểu đồ so sánh hoặc sơ đồ công nghệ.
    3. *Graphic Full to toàn màn hình (`FULL:`):* Kích thước 1920x1080, chiếm trọn khung hình vài giây để nhấn mạnh luận điểm hoặc câu hỏi quan trọng.
    4. Không được chỉ dùng 1 kiểu gây nhàm chán.
  - **Linh hoạt phong cách:** 4 mẫu video (`mau-graphic-motion-1..4`) là tiêu chuẩn về phong cách thị giác (glassmorphism, neon gradient, viền phát sáng, chuyển động mượt, typography rõ nét). Ngoài 4 mẫu đó, AI linh hoạt code bất kỳ dạng Motion Graphic Remotion nào phù hợp nhất với kịch bản (phễu, quy trình, mindmap, bảng so sánh, số liệu...).
- **Quy chuẩn Font chữ & Typography (Notion Font):**
  - Luôn sử dụng font kiểu Notion (`NotionInter` / Inter) sạch sẽ, hiện đại, dễ đọc trên mọi thiết bị.
  - **Không viết hoa toàn bộ (All-Caps)** ở tiêu đề: Sử dụng chữ hoa đầu câu (Sentence / Title case) để người xem không bị đau mắt và tránh va chạm dấu tiếng Việt.
  - Line-height tối thiểu 1.24, khoảng đệm padding rộng rãi để không bao giờ bị cắt xén hoặc chạm vào dấu mũ, dấu thanh (Â, Ê, Ô, Ơ, Ư).
- **Phụ đề tiếng Việt bắt buộc cho clip gốc tiếng Anh:**
  - Tất cả các đoạn clip gốc tiếng Anh phải có phụ đề tiếng Việt (`work/subs/<id>.ass`) chạy dưới khung hình, cỡ chữ to rõ ràng (54px), font chuẩn tiếng Việt, căn lề dưới thoáng đãng.
  - Trường hợp không có file phụ đề `.vtt`, hệ thống tự động chạy Whisper bóc băng trực tiếp âm thanh clip và dịch nghĩa tự nhiên sang tiếng Việt.
- **Hình ảnh minh họa:** Dùng Gemini API (khoá `GEMINI_API_KEY` đặt trong `<dự-án>/.env` hoặc `~/.env`, không ghi vào file nào khác) để sinh ảnh trám video. **Chỉ sinh ảnh ở những đoạn người dùng note rõ**; đoạn không note thì dùng motion graphic hoặc b-roll theo quy tắc 10 giây.
- **Phản hồi của người dùng chỉ áp dụng cho video/phiên hiện tại.** Không tự sửa skill này vì một lời chê; muốn ghi chặt phải hỏi và được duyệt.


## Một dự án = một thư mục

```
video-cua-toi/
  project.json     # cấu hình (xem examples/project.json)
  script.md        # kịch bản (xem examples/script-mau.md)
  recording/       # take1.mp4 — file quay bạn đọc kịch bản
  assets/t01/      # tuỳ chọn: ảnh riêng cho đoạn t01 (chân dung, ảnh chụp sản phẩm…)
  screens/         # tự sinh: b-roll + ảnh chạy khung trái
  source/          # tự tải: clip gốc + phụ đề (tự động nghe bằng Whisper nếu không có .vtt)
  work/            # trung gian
  out/final.mp4
```

## Chạy

- **Trên Windows**:
```powershell
$RF = "${CLAUDE_PLUGIN_ROOT}/skills/edit-video-youtube-reaction/rf.py"
python $RF --data "${CLAUDE_PLUGIN_DATA}" all projects/video-cua-toi
python $RF --data "${CLAUDE_PLUGIN_DATA}" doctor projects/video-cua-toi   # KIỂM TRƯỚC KHI GIAO
```

- **Khi chỉ sửa lẻ 1 đoạn và muốn tự động ghép lại file cuối**:
```powershell
python $RF --data "${CLAUDE_PLUGIN_DATA}" render projects/video-cua-toi --only t03 --concat
# Hoặc chỉ nối lại các seg đã có:
python $RF --data "${CLAUDE_PLUGIN_DATA}" concat projects/video-cua-toi
```

## ⚠️ Quy tắc số một: đọc `doctor`, đừng đọc log

Pipeline này từng **hỏng êm**. Đoạn nào thiếu dữ liệu thì in một dòng log rồi dựng tiếp.
Đó là cách ba phút đầu của một video 32 phút đã đi ra ngoài với khung trái đứng im — log
có ghi, không ai đọc.

`doctor` đối chiếu từng item trong kịch bản với thứ nó đã khai, và `render` gọi nó **tự động**
trước mỗi lần dựng trọn bài. Thiếu gì thì **thoát mã 1 và không dựng đoạn nào**:

- đoạn nói: có khớp lời, có chữ nhảy, có panel nếu khai `GFX:`, có thẻ nếu khai `FULL:`/`BEAT:`
- **ảnh chạy khung trái: một số đoạn có mà đoạn khác không → LỖI** (chính là bug đã ship)
- clip: có file gốc, có phụ đề Việt (cảnh báo riêng nếu phụ đề còn nguyên tiếng Anh)
- đoạn đã dựng: hình và tiếng phải bằng nhau tới mili giây

`render --only tXX` thì bỏ qua cổng này, vì lúc đó là cố ý dựng lẻ.

## Kịch bản: các dòng điều khiển

| Dòng | Việc |
|---|---|
| `## N. Tiêu đề` | mở một phần mới |
| `[CLIP 0:02:03–0:03:23]` | phát clip gốc kèm phụ đề Việt |
| `LABEL: QUẢN LÝ VI MÔ` | nhãn góc trái của clip ngay trên |
| `SLIDE: chữ khoá \| dòng nhỏ \| dòng phụ` | khối chữ tĩnh khung trái |
| `GFX: <mẫu> {json}` | đồ hoạ động góc dưới trái (900x478) |
| `SIDE: <mẫu> {json}` | đồ hoạ động 1/2 màn hình cạnh người nói (900x1016) |
| `FULL: @"câu neo" {json}` | thẻ chiếm trọn khung vài giây (1920x1080) |
| `BEAT: @"câu neo" {json}` | như FULL nhưng giọng cảm xúc, cho emoji |
| `BREAK: Tên phần` | màn chuyển đen, **tiếng im hoàn toàn** |
| `[MÀN HÌNH: 1:52–2:18]` | chạy **b-roll thật** từ video gốc ở khung trái (nhiều dòng = nối tiếp) |
| `[MÀN HÌNH: …]` | dạng chữ tự do: dùng `screens/<id>.mp4` bạn tự dựng |

`@"câu neo"` = cảnh bắt đầu đúng lúc người dẫn nói tới câu đó (dò trong lời thật, không phải
kịch bản). Không tìm thấy thì chia đều thời gian và in cảnh báo.

### Mẫu đồ hoạ chuẩn (`GFX:`, `SIDE:`, và `FULL:`)

Chi tiết cú pháp xem tại [motion/TEMPLATES.md](motion/TEMPLATES.md):
- **4 Mẫu chuẩn theo video mẫu (`motion/templates/samples/`):**
  - `bars`: Cột tăng trưởng phát sáng (Mẫu 1)
  - `trend`: Hai đường xu hướng so sánh đối chiếu (Mẫu 2)
  - `system_flow`: Dashboard trình duyệt & luồng quyết định AI (Mẫu 3)
  - `clock_cycle`: Chu kỳ 24/7 & tác vụ xoay quanh đồng hồ (Mẫu 4)
- **Mẫu mở rộng & 1/2 màn hình:** `steps` (quy trình dọc 1-2-3) · `compare` (so sánh 2 chiều) · `image` (minh họa Gemini/B-roll)
- **Mẫu chữ & số:** `card` · `bignumber` · `list` · `quote` · `twoline`
- **Mẫu hệ thống:** `bots` · `flow` · `dashboard`

```text
GFX: @"tăng trưởng bứt phá" bars {"kicker":"KẾT QUẢ","headline":"Doanh thu tăng gấp 6 lần"}
SIDE: @"bốn bước cốt lõi" steps {"kicker":"QUY TRÌNH","headline":"4 Bước Thực Hiện"}
SIDE: @"so sánh trực quan" compare {"kicker":"ĐỐI ĐẦU","leftTitle":"Thủ công","rightTitle":"AI"}
FULL: @"quy trình tự động" {"secs":3.8,"style":"system_flow","kicker":"KIỂM DUYỆT","title":"Tự động hóa 100% bằng AI"}
FULL: @"tiết kiệm toàn bộ thời gian" {"secs":4.0,"style":"clock_cycle","kicker":"24/7","title":"Hệ thống vận hành không ngừng nghỉ"}
```

## Cắt vấp — Claude làm giám khảo

Whisper chỉ đổi giọng thành chữ có mốc giây (**tắt VAD**, không nối ngữ cảnh — bật lên là nó
"nuốt" luôn câu đọc hụt). Quyết định cắt do **Claude** đọc kịch bản + lời thật rồi trả về
**số thứ tự từ**, không bịa mốc giây. Giữ lần đọc cuối; không cắt lặp có chủ ý, nói lệch
trôi chảy, hay cách đọc số.

Sau khi dựng, `verify` **nghe lại chính file đã dựng** để bắt chỗ cắt chưa sạch ở mối nối,
chạy nhiều vòng tới khi không còn gì. Vòng này từng bắt thêm 27 chỗ mà vòng đầu bỏ sót.

## Những cái bẫy đã trả giá

- **Whisper bịa lời tiếng Việt.** Gặp khoảng im lặng là nó chèn "Hãy đăng ký kênh…",
  "Xin chào", "Hẹn gặp lại". Một bản ghi 31 phút có 52 lần "Ghiền Mì Gõ". Chúng gần như
  không chiếm thời lượng nên cắt đi là vô hại, nhưng **đừng tin số từ** làm thước đo.
- **`loudnorm` đẩy mốc thời gian của tiếng lên ~2 khung.** Cắt đuôi tiếng bằng `atrim=end=<giây>`
  (tính theo mốc tuyệt đối) là hụt đúng chừng ấy mỗi đoạn — cộng lại **nửa giây** trên
  video 28 đoạn. Phải `asetpts=N/SR/TB` dựng lại mốc từ số mẫu **trước** khi cắt.
  `apad=whole_dur` KHÔNG thay thế được: nó không kết thúc luồng tiếng, `-frames:v` cắt ngang tuỳ lúc.
- **Cắt phải căn về lưới khung hình.** Video chỉ cắt được ở khung, tiếng cắt được ở mẫu;
  không căn thì sai số dồn qua từng mối nối.
## Khung trái: b-roll thật thay vì ảnh đứng im

`[MÀN HÌNH: 1:52–2:18]` trong một đoạn nói sẽ cắt đúng khúc đó của video gốc và cho **chạy**
ở khung trái. Khai nhiều dòng thì chúng nối tiếp nhau, lặp lại cho đủ độ dài đoạn nói.

Ảnh bạn tự bỏ vào `assets/<id>/` (headline, chân dung, ảnh sản phẩm) luôn chạy trước b-roll.
**Đoạn nào đã có ảnh riêng thì pipeline không lấy thêm khung từ video gốc nữa** — nếu không,
một cảnh phim trường Trung Quốc sẽ rơi vào giữa đoạn đang nói về quảng cáo máy xay.

Hai tuỳ chọn trong `project.json` đi kèm:

```json
"source": {
  "crop_bottom": 0.25,                    // cắt dải phụ đề cháy sẵn khỏi khung trái
  "cover_bottom": {"y": 0.75, "h": 0.25}  // phủ dải đó trên clip, rồi vẽ phụ đề của mình lên
}
```

- **Bản đăng lại thường cháy sẵn phụ đề vào hình.** Đặt `source.cover_bottom` để phủ dải đó,
  nếu không phụ đề Việt của bạn thành lớp chữ thứ ba.
- **Bản quay 4K/60fps phải hạ về 1080p30 trước khi dựng**, nhanh hơn nhiều lần.
- **Nguồn có lower-third thường trực** thì dời nhãn của mình bằng `style.label_xy`.

## Bảo mật

- Không ghi khoá vào file nào trong dự án; đọc từ `.env` lúc chạy.
- Chỉ tải video từ link bạn đưa; không đăng nhập tài khoản nào.
- Clip gốc dùng theo kiểu trích dẫn có bình luận — tự chịu trách nhiệm về bản quyền
  và dẫn nguồn trong phần mô tả.
