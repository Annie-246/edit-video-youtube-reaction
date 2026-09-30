# Edit Video Youtube Reaction

Plugin Claude Code dựng video YouTube dạng react/phân tích: từ kịch bản markdown + file quay
đọc kịch bản + link video gốc ra `out/final.mp4` 1080p — cắt vấp, chữ nhảy theo từng từ,
phụ đề Việt cho clip gốc, motion graphic Remotion (góc nhỏ / nửa màn hình / full màn hình).

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

## Dùng

Nói với Claude: "edit video youtube reaction" / "dựng video react", hoặc gọi skill
`/edit-video-youtube-reaction:edit-video-youtube-reaction`. Quy trình chi tiết ở
[skills/edit-video-youtube-reaction/SKILL.md](skills/edit-video-youtube-reaction/SKILL.md).

## Cập nhật plugin (người bảo trì)

Sửa file trong repo → commit → push lên `main`. Plugin không khai `version`, nên mọi commit
mới đều được coi là bản cập nhật.
