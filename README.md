# Edit Video Youtube Reaction

Plugin Claude Code dựng video YouTube dạng react/phân tích: từ kịch bản markdown + file quay
đọc kịch bản + link video gốc ra `out/final.mp4` 1080p theo bố cục trắng kiểu Claude/Anthropic:
khung nội dung lớn (b-roll thật + motion graphic màu cam trơn), avatar dọc, thẻ tiêu đề phần,
chữ nhảy theo từng từ, clip gốc full màn hình có phụ đề Việt, tự cắt vấp.

Ngoài bố cục trắng còn có:

- **3 chế độ màn hình kiểu Greg Isenberg:** `FACE` (người nói full màn, chỉ hiện cụm từ khoá),
  `BUBBLE` (nội dung trong khung bo góc trên nền lưới, ô mặt nhỏ bên phải), `MOTION` (motion
  graphic tràn màn, không người).
- **Tự chèn meme** (tìm, tải, cất vào kho `meme-library/`), **logo thương hiệu** được nhắc tên
  (kho `logo-library/`) và **ảnh thật** minh hoạ.
- **Bộ motion studio:** swipe ảnh, dải màu, ảnh trôi, chữ khổng lồ, nút viên thuốc, quỹ đạo,
  thanh gõ prompt, giao diện app 3D; mỗi mẫu có bản sáng / tối.
- Sting chuyển phần và outro kiểu showreel.

## Cài đặt

Trong Claude Code:

```
/plugin marketplace add Annie-246/edit-video-youtube-reaction
/plugin install edit-video-youtube-reaction@edit-video-youtube-reaction
```

### Bật tự động cập nhật (mỗi người làm một lần)

Marketplace bên thứ ba mặc định **tắt** auto-update. Bật bằng:

`/plugin` → tab **Marketplaces** → chọn `edit-video-youtube-reaction` → **Enable auto-update**

Hoặc dán vào `~/.claude/settings.json` (cài + bật auto-update một lần):

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

Từ đó mỗi lần repo có commit mới, Claude Code tự kéo bản mới khi khởi động.

## Máy cần có

`ffmpeg`, `ffprobe`, `yt-dlp`, `node` >= 20, `python` >= 3.11 trên PATH.
Lần chạy đầu plugin tự tạo venv Python + cài Remotion vào thư mục dữ liệu của plugin
(`~/.claude/plugins/data/...`), không mất khi plugin cập nhật.

Lần đầu dùng, Claude sẽ xin **API key Gemini miễn phí** (lấy tại https://aistudio.google.com/apikey)
để tự sinh ảnh minh hoạ chèn vào video, rồi lưu vào `~/.env`. Không đưa khoá vẫn dựng được,
chỉ không có ảnh AI.

Khuyên có thêm `PEXELS_API_KEY` (miễn phí, lấy ngay tại https://www.pexels.com/api/) trong `~/.env`
để ảnh minh hoạ tự chèn là ảnh stock đẹp; không có thì lấy từ Openverse / Wikimedia (ít và cũ hơn).

## Dùng

Nói với Claude: "edit video youtube reaction" / "dựng video react", hoặc gọi skill
`/edit-video-youtube-reaction:edit-video-youtube-reaction`. Quy trình chi tiết ở
[skills/edit-video-youtube-reaction/SKILL.md](skills/edit-video-youtube-reaction/SKILL.md).

## Cập nhật plugin (người bảo trì)

Sửa file trong repo → commit → push lên `main`. Plugin không khai `version`, nên mọi commit
mới đều được coi là bản cập nhật.
