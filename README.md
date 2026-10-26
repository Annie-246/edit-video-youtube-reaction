# Edit Video Youtube Reaction

Plugin Claude Code dựng video YouTube dạng react/phân tích: đưa kịch bản, file quay và link
video gốc, nhận về `out/final.mp4` 1080p đã cắt vấp, có motion graphic, phụ đề Việt,
logo và ảnh minh hoạ.

## Cài đặt: 3 bước, không cần biết kỹ thuật

1. Mở **Claude Code**.
2. Dán nguyên câu này rồi gửi:

   > Cài plugin này cho mình: https://github.com/Annie-246/edit-video-youtube-reaction — làm theo mục "Hướng dẫn cho Claude" trong README.

3. Claude cài xong sẽ nhắc bạn **tắt Claude Code rồi mở lại**. Mở lại là dùng được, và từ đó
   plugin **tự cập nhật** mỗi khi có bản mới, bạn không phải làm gì thêm.

Dùng: nói với Claude *"dựng video react"* hoặc *"edit video youtube reaction"*. Claude sẽ hỏi
kịch bản, file quay và link video gốc.

---

## Hướng dẫn cho Claude (Claude Code đọc mục này khi được nhờ cài)

Người nhờ cài thường không rành kỹ thuật: tự làm hết, giải thích ngắn bằng tiếng Việt, chỉ hỏi
khi cần họ bấm đồng ý. **Không `git clone` repo này** (bản clone không tự cập nhật).

1. **Đăng ký plugin + bật tự cập nhật.** Đọc `~/.claude/settings.json` (chưa có thì tạo `{}`), rồi
   **gộp** (không ghi đè các khoá đang có) hai mục sau:

   ```json
   {
     "extraKnownMarketplaces": {
       "edit-video-youtube-reaction": {
         "source": { "source": "github", "repo": "Annie-246/edit-video-youtube-reaction" },
         "autoUpdate": true
       }
     },
     "enabledPlugins": {
       "edit-video-youtube-reaction@edit-video-youtube-reaction": true
     }
   }
   ```

   Giữ file là JSON hợp lệ (đọc lại sau khi ghi).

2. **Kiểm tra phần mềm cần có**: `ffmpeg`, `ffprobe`, `yt-dlp`, `node` (>= 20), `python` (>= 3.11),
   `git`. Thiếu cái nào thì xin phép người dùng một câu rồi cài:
   - Windows: `winget install -e --id Gyan.FFmpeg` · `yt-dlp.yt-dlp` · `OpenJS.NodeJS.LTS` ·
     `Python.Python.3.12` · `Git.Git` (thêm `--accept-source-agreements --accept-package-agreements`).
   - macOS: `brew install ffmpeg yt-dlp node python git` (chưa có Homebrew thì hướng dẫn cài từ https://brew.sh).
   - Linux: dùng trình quản lý gói của máy (`apt`, `dnf`…).

3. **Báo người dùng**: "Xong rồi, bạn tắt Claude Code và mở lại nhé. Lần đầu dựng video mình sẽ
   tự cài thêm phần dựng hình (mất vài phút)." Nếu vừa cài phần mềm ở bước 2 thì nhắc mở lại cả
   cửa sổ terminal / máy để PATH nhận phần mềm mới.

4. Không xin API key lúc cài. Lần đầu dùng, skill tự hỏi khoá Gemini (tuỳ chọn).

---

## Plugin làm được gì

- **Bố cục trắng** kiểu Claude/Anthropic: khung nội dung lớn (b-roll thật + motion graphic cam
  đất), avatar dọc, thẻ tiêu đề phần, chữ nhảy theo từng từ, clip gốc full màn có phụ đề Việt.
- **3 chế độ màn hình kiểu Greg Isenberg:** `FACE` (người nói full màn, chỉ hiện cụm từ khoá),
  `BUBBLE` (nội dung trong khung bo góc trên nền lưới, ô mặt nhỏ bên phải), `MOTION` (motion
  graphic tràn màn, không người).
- **Tự chèn logo thương hiệu** được nhắc tên
  (kho `logo-library/`) và **ảnh thật** minh hoạ.
- **Bộ motion studio:** swipe ảnh, dải màu, ảnh trôi, chữ khổng lồ, nút viên thuốc, quỹ đạo,
  thanh gõ prompt, giao diện app 3D; mỗi mẫu có bản sáng / tối.
- Tự cắt vấp, sting chuyển phần và outro kiểu showreel.

## Khoá API (tuỳ chọn, đều miễn phí)

Lưu trong `~/.env`, Claude tự hỏi khi cần:

- `GEMINI_API_KEY` (https://aistudio.google.com/apikey): sinh ảnh minh hoạ AI, dịch phụ đề nhanh hơn.
- `PEXELS_API_KEY` (https://www.pexels.com/api/): ảnh stock đẹp cho phần tự chèn ảnh; không có
  thì lấy từ Openverse / Wikimedia (ít và cũ hơn).

Không có khoá nào vẫn dựng được video.

## Cài thủ công (nếu muốn tự gõ lệnh)

```
/plugin marketplace add Annie-246/edit-video-youtube-reaction
/plugin install edit-video-youtube-reaction@edit-video-youtube-reaction
```

Rồi bật tự cập nhật: `/plugin` → tab **Marketplaces** → `edit-video-youtube-reaction` →
**Enable auto-update** (marketplace bên thứ ba mặc định tắt).

Lần chạy đầu plugin tự tạo venv Python + cài Remotion vào thư mục dữ liệu của plugin
(`~/.claude/plugins/data/...`), không mất khi plugin cập nhật. Quy trình chi tiết ở
[skills/edit-video-youtube-reaction/SKILL.md](skills/edit-video-youtube-reaction/SKILL.md).

## Muốn tự chỉnh sửa skill?

Repo này chỉ chủ repo được sửa. Bạn không push được vào đây và repo không nhận pull request
chỉnh sửa. Muốn đổi theo ý mình thì làm bản riêng:

1. **Đừng sửa thẳng trong thư mục plugin** (`~/.claude/plugins/cache/...`): lần tự cập nhật
   kế tiếp sẽ ghi đè mất hết.
2. Bấm **Fork** trên GitHub (hoặc tải repo về), rồi nhờ Claude:

   > Clone skill trong https://github.com/<tài-khoản-của-bạn>/edit-video-youtube-reaction vào
   > `~/.claude/skills/` làm bản riêng của mình — làm theo mục "Muốn tự chỉnh sửa skill?" trong README.

3. Từ đó bạn sửa thoải mái trên bản của mình. Bản riêng **không tự cập nhật** theo repo gốc;
   muốn lấy tính năng mới thì tự kéo về (GitHub có nút **Sync fork**).

**Hướng dẫn cho Claude khi cài bản riêng:**

- Chép thư mục `skills/edit-video-youtube-reaction/` vào `~/.claude/skills/<tên-mới>/` (đặt tên
  khác, ví dụ `edit-video-youtube-reaction-rieng`) và đổi `name:` trong `SKILL.md` cho khớp.
- Trong `SKILL.md`, thay mọi `${CLAUDE_PLUGIN_ROOT}/skills/edit-video-youtube-reaction` bằng
  đường dẫn tuyệt đối tới thư mục vừa chép, và bỏ `--data "${CLAUDE_PLUGIN_DATA}"` (dữ liệu sẽ
  nằm ở `~/.edit-video-youtube-reaction`).
- Nếu máy đang cài bản plugin, hỏi người dùng có muốn tắt nó không (`/plugin` → tắt
  `edit-video-youtube-reaction`) để hai bản không cùng nhận một yêu cầu.

## Cập nhật plugin (người bảo trì)

Sửa file trong repo → commit → push lên `main`. Plugin không khai `version`, nên mọi commit
mới đều được coi là bản cập nhật; máy đã bật auto-update tự kéo bản mới khi mở Claude Code.
