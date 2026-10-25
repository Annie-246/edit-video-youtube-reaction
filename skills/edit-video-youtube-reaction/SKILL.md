---
name: edit-video-youtube-reaction
description: Edit Video Youtube Reaction — dựng video react/phân tích YouTube từ kịch bản markdown + bản quay đọc kịch bản + link video gốc. Bố cục trắng kiểu Claude/Anthropic (khung nội dung lớn, avatar dọc, tiêu đề phần màu cam, chữ nhảy theo từng từ) xen 3 chế độ kiểu Greg Isenberg (người nói full màn chỉ hiện từ khoá, b-roll full màn có ô mặt nhỏ, motion graphic full màn không người), b-roll thật từ video gốc, motion graphic Remotion màu cam đất, sting chuyển phần/outro kiểu showreel, tự tìm và chèn meme kèm kho meme dùng lại, clip gốc full màn hình có phụ đề Việt, tự cắt vấp. Kích hoạt khi người dùng nói "edit video youtube reaction", "dựng video react", "ghép clip gốc với mặt người", hoặc gõ /reactforge.
---

# Edit Video Youtube Reaction — dựng video react tự động

Đầu vào: kịch bản markdown, file quay người dẫn đọc kịch bản (vấp, nói lệch cũng được), link video gốc.
Đầu ra: `out/final.mp4` 1080p30 theo **bố cục trắng** dưới đây.

## Bố cục (cố định)

```
┌──────────────────────────────────────────────┐ ┌──────────────┐
│                                              │ │ Công cụ 2/6  │ ← thẻ tiêu đề phần: nền cam trơn,
│        KHUNG NỘI DUNG 1440x920               │ │ Agent Reach  │   chữ trắng (dòng INFO: của phần)
│   chỉ quay màn hình / b-roll thật            │ └──────────────┘
│   (nền gradient be → cam nhạt)               │ ┌──────────────┐
│                                              │ │              │
│                                              │ │   AVATAR     │ ← mặt người dẫn, khung dọc 360x724
│                                              │ │   người dẫn  │
│      ┌──────────────────────────────┐        │ │              │
└──────│  chữ nhảy theo từng từ       │────────┘ └──────────────┘
       └──────────────────────────────┘  ← thanh trắng ngắn đè mép dưới khung
        nền: lưới trắng (pipeline/assets/bg-grid.png)
```

- **Bố cục trắng này chỉ dùng cho source quay màn hình** (`broll`, `screen`, `rec`). Nó không phải
  theme chính. Chữ nhảy nằm trong thanh trắng: chữ đã đọc màu đen, chữ chưa đọc màu xám.
- **Khi phát clip gốc:** clip **chiếm trọn màn hình**, không avatar, không khung, chỉ có
  phụ đề Việt ở dưới (chữ trắng trên dải mờ).
- **Thẻ FULL:** chiếm trọn màn hình vài giây để nhấn một ý (mở đầu công cụ, câu chốt, con số).

### Luật bố cục (khoá cứng)

- **Đoạn nào có motion graphic thì motion graphic phải full màn:** đoạn `MOTION:` hoặc thẻ `FULL:` /
  `BEAT:`. Không đặt motion graphic (title, flow, logo, ảnh, số liệu…) vào khung nhỏ cạnh avatar.
- **Bố cục có người dạng card nhỏ** (bố cục trắng, `BUBBLE:`) **chỉ dùng với source quay màn hình.**
- Video xoay vòng linh hoạt giữa ba thứ: **người nói full màn** (`FACE:`, có thể kèm `OVER:`) ·
  **motion graphic full màn** (`MOTION:`) · **bố cục avatar + quay màn hình** (mặc định / `BUBBLE:`).
  Không để một kiểu chạy suốt video.
- `doctor` chặn đoạn bố cục trắng / `BUBBLE:` có `SIDE:` không phải `broll` / `screen` / `rec`.
  Bước `visuals` (tự chèn logo, ảnh) chỉ chèn vào đoạn `MOTION:`.

### Bốn chế độ cho một đoạn nói (đổi bằng một dòng trong đoạn)

| Dòng | Màn hình | Chữ | Hợp với |
|---|---|---|---|
| *(không khai)* | bố cục trắng ở trên, **chỉ chạy quay màn hình** | chữ nhảy theo từng từ | thuật lại / demo trên quay màn hình |
| `FACE:` | người nói **chiếm cả màn**; mỗi chỗ cắt và mỗi ~7 giây đổi cỡ cảnh rộng ↔ chặt (punch-in 1.15) | **chỉ cụm từ khoá** 2–5 từ, AI tự chọn (xem "Chữ từ khoá FACE"), cộng lớp `OVER:` nếu khai | hook, câu chuyện, quan điểm, kêu gọi |
| `BUBBLE:` | **nền lưới trắng**; quay màn hình trong một khung bo góc lớn 1500x1000 bên trái, mặt người trong **ô bo góc nhỏ 336x400 bên phải**. Cả hai khung có viền cam gradient (`#F0B49A → #D97757 → #B5532F`) và bóng đổ mềm phía dưới | không có | bình luận dài trên quay màn hình |
| `MOTION:` | **motion graphic tràn kín màn** 1920x1080, không nền lưới, không khung; người nói nằm trong **bubble tròn nhỏ góc phải dưới** (Ø 270px, viền cam gradient, bóng mềm, khung lấy rộng thấy cả nền và áo) | không có | **mọi đoạn có motion graphic**: sơ đồ, số liệu, logo, mục lục, câu chốt |

- Mỗi video nên trộn: hook bằng `FACE:`, thân bài xen `FACE:` / `MOTION:` / bố cục avatar + quay màn hình.
  Một đoạn nói vừa cần graphic vừa cần quay màn hình thì tách bằng `---` thành hai đoạn.
- `FACE:` không dùng `SIDE:`; muốn chen đồ hoạ thì dùng `OVER:` (đè lên người), `FULL:` / `BEAT:` hoặc meme.
- `BUBBLE:` / `MOTION:` bắt buộc có `SIDE:` như bố cục trắng; mỗi cảnh ≤ 10 giây (`doctor` cảnh báo).

### Lớp `OVER:` (chỉ ở đoạn `FACE:`)

Graphic đè lên người nói, cùng lớp trong suốt với chữ từ khoá. Cú pháp như `FULL:`:
`OVER: @"câu neo" {"secs":3,"tpl":"<mẫu>", …}`. Lớp nào chiếm mép dưới hoặc cả khung (`stats`, `dots`,
`blurtitle`) thì cụm từ khoá trùng giờ tự nhường (cắt ngắn hoặc bỏ).

| Mẫu | Dùng khi | Props |
|---|---|---|
| `stats` | 2–3 con số dưới ngực, đếm lên cùng lúc, lóe cam khi chạm đích (hook có số liệu) | `items:[{label,value,prefix,suffix,decimals}]` |
| `dots` | "3 điều cần nhớ" mà vẫn giữ mặt người. **Chỉ chữ, không card:** câu của ý đang nói ở dưới, dẫn bằng số to màu cam; các ý đã nói lùi lên trên thành dòng nhỏ mờ (`pills` = tên ngắn của từng ý) | `n`, `active`, `text`, `pills:[…]` |
| `status` | nhãn trạng thái nhỏ phía trên ("6 giờ", "Đang dựng…") | `text`, `spin`, `side:"right"` |
| `blurtitle` | câu lớn đặt trên chính người nói, **người nói tự nhoè** suốt lớp này (thay cho cắt hẳn sang thẻ) | `kicker`, `title` (có `*nhấn*`) |
| `orbit` | **ảnh xoay vòng 3D quanh người**: ảnh vòng ra sau thì khuất sau người, vòng ra trước thì đè lên (tự tách nền người bằng rembg). Chỉ thỉnh thoảng, ở đoạn có ảnh, 3–6 giây | `images:[…]` (6–8 ảnh), `cx`, `cy` (0.7 = ngang ngực), `rx`, `ry`, `speed`, `card` |
- **Nền lưới trắng chỉ dành cho khung có mặt người** (bố cục trắng, `BUBBLE:`). Khung không người
  (`MOTION:`, thẻ `FULL:`, clip gốc, chuyển phần) tràn kín màn.
- Viền và bóng của `BUBBLE:` vẽ một lần thành `work/gfx/rim_<chế độ>_<cỡ>.png`
  (kích thước khung ở `layout_for` → `screen`, `bubble`, `rim`, `shadow`). Bố cục trắng gốc giữ nguyên.
- Cỡ cảnh `FACE:` chỉnh trong `project.json` → `recording.face: {"cx":0.5,"cy":0.45,"zoom":1.0,"punch":1.15}`;
  ô mặt `BUBBLE:` → `recording.bubble: {"cx":0.5,"cy":0.42,"zoom":1.25}`; bubble tròn `MOTION:` →
  `recording.dot: {"cx":0.5,"cy":0.5,"zoom":1.0}` (zoom 1 = lấy cả chiều cao khung, thấy nền và áo; mẫu nào
  có nội dung sát góc phải dưới thì chừa chỗ cho bubble). Bản quay 1080p phóng 1.15
  hơi mềm; quay 4K thì thoải mái.
- Từ khoá `FACE:` lưu ở `work/keywords/<id>.json` (sửa tay được, giữ nguyên khi lời không đổi).

### Chữ từ khoá FACE (vẽ bằng Remotion, không dùng phụ đề ASS)

Bước `captions` chỉ chọn cụm; bước `panel` vẽ lớp chữ trong suốt `work/keys/<id>.webm` (VP8 có
alpha) bằng composition `Keys`, `render` đè lên mặt người. Hai kiểu, tự chọn theo từng cụm:

- **Cho chữ nổi trên mọi nền** (áo trắng là ca khó nhất): mỗi cụm kéo theo một dải đen mờ dâng
  từ mép dưới (hiện/tắt cùng cụm) **và** một lớp bóng đậm ôm sát từng nét chữ.
- **Dòng (`line`, mặc định):** một dòng Inter ExtraBold (800) cỡ ~112px ở 1080p, chữ trắng,
  từ khoá gradient cam đất. Dòng được kéo ngang gần tới mép khung (lề 80px), **không bó
  trong bề ngang người nói**; câu dài thì tự co cỡ cho vừa một dòng.
- **Chồng (`stack`):** chữ dẫn nhỏ (~66px) + từ khoá cực to (~200px, Inter Black) — cho con số và
  câu chốt ngắn, khoảng 1/3 số cụm (AI đánh `"big": true`; có chữ số thì tự bật). Chỉ dùng khi từ
  khoá liền nhau và nằm **đầu hoặc cuối** cụm (từ khoá đứng đầu thì nằm trên chữ dẫn); từ khoá
  nằm giữa cụm hoặc dài hơn 16 ký tự thì tự về kiểu dòng, vì tách ra đọc vô nghĩa.
- Chữ hiện từng từ đúng lúc nói (mờ → rõ, trồi lên), từ khoá nảy nhẹ; hết cụm thì mờ đi.

## Bộ màu: dark theme toàn bộ (cố định)

Học từ video mẫu "học thêm motion graphics (2)".

- **Nền:** than gần đen `#161514`, quầng cam ấm loang từ mép dưới, góc tối dần. Áp cho mọi motion
  graphic, thẻ FULL, và cả bố cục avatar + quay màn hình (nền lưới tối `pipeline/assets/bg-grid-dark.png`,
  khung viền tối, thanh chữ nhảy tối: chữ đã đọc màu kem, chưa đọc màu xám).
- **Màu nhấn duy nhất:** cam đất `#D97757` (khối cam dùng gradient nhẹ cùng tông). Không dùng màu khác.
- **Chữ:** kem `#FAF9F5`, chữ phụ `#C9C5BC`, chữ mờ `#9A968E`. Font Inter, viết hoa đầu câu.
- **Chiều sâu vừa phải, không "ảo":** card có nền chuyển nhẹ sáng trên tối dưới, đường sáng mảnh mép trên,
  viền mảnh, bóng đổ vừa. Chỉ danh sách chương (`chapters`) được nổi khối mạnh hơn.
- **Nhãn nhỏ phía trên tiêu đề** (`kicker`: "Quy trình", "Hạn chót"…) là **chữ trơn** in hoa giãn chữ có chấm
  cam, **không bọc capsule**. Capsule chỉ dùng khi chính nó là nội dung (mẫu `pills`). Đừng lạm dụng capsule.
- Cảnh nào thật sự cần nền sáng thì ghim `"dark": false`.
- **Chuyển động** theo 2 video mẫu ở `motion/templates/samples/`: chữ hiện dần từng từ, thẻ
  trồi lên lần lượt, con trỏ tay bấm, chữ gõ từng ký tự, số đếm lên.
- **Danh sách chương (học từ video mẫu 2):**
  - Đầu video, khi người dẫn kể "video này có…": `SIDE: @"câu neo" chapters {"mode":"intro"}` trong đoạn
    `MOTION:`. Danh sách tự lấy từ các dòng `BREAK:` của kịch bản; các dòng nhoè vào rồi sáng lần lượt
    (`"times":[giây…]` cho khớp đúng lúc nhắc từng chương, không có thì cách `per` khung).
  - Mỗi `BREAK:` **tự thành màn quay lại danh sách**: khung đẩy nhẹ vào chương mới, dòng đó khoanh viền cam
    phát sáng, chương đã qua có tick, còn lại mờ. Ảnh nhỏ mỗi dòng là một khung hình quay màn hình đầu tiên
    của chương đó; chương không có quay màn hình thì dùng icon. `BREAK:` im lặng.
- **Outro** (`OUTRO:`) giữ kiểu showreel: chữ trồi có bóng lặp, tiếng whoosh + trầm tự tổng hợp.
  **Không có intro**: video vào thẳng lời người dẫn.

## Quy tắc SFX (khoá cứng)

Mọi SFX chèn vào video **bắt buộc theo `references/sound-effects-guide.md`** (bảng luật L1–L23, Phần 2). Đọc file đó trước khi chèn tiếng.

- Guide chỉ dùng làm quy tắc (khi nào chèn, loại gì, đặt ở đâu). **Nguồn lấy file SFX vẫn là myinstants trước, ElevenLabs sau**; các kho trong cột "Nghe thử" của guide chỉ để nghe tham khảo, không phải nguồn tải.
- Mỗi SFX phải trỏ về một sự kiện L1–L22. Không có sự kiện thì không tiếng. Điểm cắt thường / jump cut dọn lời (L23) mặc định **im lặng**.
- SFX nhỏ hơn giọng; chỉ Impact/Boom được nhỉnh hơn nhưng không át lời. Một khoảnh khắc chỉ một SFX chính; cùng loại sự kiện dùng cùng một mẫu tiếng.
- Mật độ talking head: khoảng 3–6 điểm SFX mỗi phút ở đoạn có nhiều phần tử hiện, đoạn nói liền mạch gần như 0; Impact lớn 1–3 lần cả video.
- Không đặt đỉnh SFX đè lên âm tiết bắt buộc nghe rõ (giá, số, hướng dẫn).
- Dựng xong phải liệt kê lại toàn bộ SFX đã chèn kèm mốc thời gian và mã luật (L-số) để kiểm tra.

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
   Bước `memes` tự tìm chỗ chèn meme, tải meme, cất vào kho; **xem `work/memes_sheet.jpg`** rồi
   bỏ / thay meme sai ý trước khi giao.
   Bước `visuals` tự chèn logo thương hiệu và ảnh thật; **xem `work/visuals_sheet.jpg`** rồi bỏ
   ảnh sai ý (sửa `work/visuals_auto.json`, chạy lại `visuals` rồi `panel --force`).
5. Dựng graphic, b-roll, chữ nhảy, phụ đề clip, ghép và xuất `out/final.mp4`.
6. Người dùng nghiệm thu và yêu cầu chỉnh thêm.

## Quy tắc cắt (khoá cứng)

- **Ý cuối cùng:** một ý nói lại nhiều lần thì chỉ giữ lần cuối (hoặc lần hoàn chỉnh nhất).
- **Đệm an toàn:** không cắt chườm vào từ, giữa các ý luôn có đệm tự nhiên.

## Quy tắc hình ảnh (khoá cứng)

- **Luật 10 giây:** tối thiểu 10 giây có một hình mới. Ở `FACE:`, mỗi cụm từ khoá mới, thẻ FULL
  hoặc meme đều tính là một hình mới (AI chọn từ khoá giữ nhịp ≤ 9 giây, thiếu thì tự chèn). Pipeline tự đảm bảo: cảnh graphic
  nào dài quá 11 giây sẽ chạy 7 giây rồi tự chuyển sang b-roll cùng chủ đề (lấy mốc b-roll
  gần nhất phía trước trong đoạn đó). Vẫn nên khai cảnh dày: khoảng 6–9 giây một cảnh.
- **Phân tích kịch bản trước, chọn graphic sau:** con số → `bignumber`/`equation`, quy trình →
  `steps`/`flow`, so sánh → `compare`/`bars`, danh sách → `checklist`, câu chốt → `title`,
  tin nhắn/AI hỏi đáp → `chat`/`questions`. Hai cảnh liền nhau không cùng dạng.
  Bộ mẫu học từ video mẫu: giá cũ → giá mới `pricecut`, tổng chi phí/thời gian `receipt`, hạn chót
  `calendar`/`countdown`/`lock`, video nhiều bước `tracker`, công cụ nhận gì làm ra gì `hub`, khối
  lượng dữ liệu `folder`, cắt ậm ừ `transcript`, kế hoạch dựng `scriptclip`, gợi tò mò ý thứ hai
  `reveal`, xu hướng `linechart`, trước/sau `beforeafter`, gõ prompt `promptui`, đang xuất / chờ xử lý
  `progress`, tài liệu thật `doctilt`, bằng chứng xã hội `comments`.
- **Tư duy chọn cảnh (đọc `references/tu-duy-dung-motion.md` trước khi khai cảnh):**
  - Mỗi câu hỏi "người xem cần **tin / thấy / hiểu / nhớ**?": tin → `FACE:`; thấy → b-roll / giao
    diện / ảnh thật; hiểu → sơ đồ, icon ẩn dụ; nhớ → con số / câu chốt. Không cần gì → không cảnh mới.
  - Tỉ lệ mặt người theo chức năng đoạn: demo/hướng dẫn ít mặt, quan điểm/kêu gọi nhiều mặt.
    Không để quá ~40 giây liền không thấy mặt người.
  - Mỗi `title` đúng **một** cụm `*nhấn*`, là từ cảm xúc / kết quả / con số.
  - Câu neo: `bignumber` neo vào 3–5 từ **trước** con số (số đếm xong đúng lúc được nói); `title`/`BEAT:`
    neo vào đầu câu (chữ hiện trước lời).
  - Một khái niệm giữ một icon suốt video; video nhiều phần thì `agenda` sau hook, `recap` cuối khớp
    đúng các mục đã hứa.
- **Xen b-roll thật:** đoạn thuật lại lời/việc của nhân vật trong video gốc thì dùng `broll`
  đúng khúc đó (bố cục avatar); đoạn người dẫn tự giải thích, ví dụ thì dùng graphic **full màn**
  (`MOTION:` / `FULL:`); đoạn quan điểm, kêu gọi thì `FACE:`.
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
| `SIDE: @"câu neo" <mẫu> {json}` | cảnh của đoạn, bắt đầu đúng lúc người dẫn nói câu neo, chạy tới cảnh sau. Đoạn `MOTION:` → mẫu motion bất kỳ (full màn); bố cục trắng / `BUBBLE:` → chỉ `broll` / `screen` / `rec` |
| `FULL: @"câu neo" {"secs":4,"tpl":"<mẫu>",…}` | thẻ chiếm trọn màn hình vài giây |
| `OVER: @"câu neo" {"secs":3,"tpl":"stats",…}` | graphic đè lên người nói, chỉ ở đoạn `FACE:` (xem "Lớp OVER") |
| `BEAT: @"câu neo" {"title":"…"}` | thẻ chốt nền đen |
| `BREAK: Tên phần` | màn quay lại danh sách chương, zoom vào chương mới (tên phần = tên dòng), tiếng im |
| `---` | tách một đoạn nói thành hai |
| `FACE:` / `BUBBLE:` / `MOTION:` | chế độ màn hình của đoạn nói (xem bảng bốn chế độ) |
| `MEME: @"câu neo" {"q":"surprised pikachu","mood":"shock","secs":2,"mode":"part"}` | chèn meme ngay sau câu chứa câu neo (khai tay; AI vẫn tự chọn thêm) |
| `OUTRO: Tiêu đề \| dòng phụ` | sting kết (đặt cuối cùng) |

- `@"câu neo"` dò trong lời thật đã khớp (3–5 từ, phải duy nhất trong đoạn). Không tìm thấy
  thì chia đều thời gian và in cảnh báo. Người dẫn hay nói lệch kịch bản: sau `align`, đọc lời
  thật trong `work/align_report.md` rồi sửa câu neo cho khớp.
- Mọi đoạn nói không phải `FACE:` **phải có ít nhất một `SIDE:`**, nếu không `doctor` chặn vì khung nội dung trống.
- Dòng `GFX:` của kịch bản cũ vẫn chạy, được gộp vào `SIDE:`.
- B-roll: `SIDE: @"câu" broll {"at": 330, "caption": "Agent Reach"}` (giây trong video gốc).
  Lấy mẫu khung hình video gốc thành bảng ảnh (mỗi 15 giây) và đọc transcript để chọn đúng mốc.
  Slide trong video gốc thường đứng yên lâu, nên mỗi đoạn b-roll tự zoom trượt về một góc khác.

Danh mục mẫu và props: [motion/TEMPLATES.md](motion/TEMPLATES.md).

## Ảnh thật và logo: tự tìm, tự chèn

Logo và ảnh thật là graphic nên chỉ tự chèn vào đoạn `MOTION:` (full màn). Bố cục avatar chỉ chạy quay màn hình; `FACE:` không có.

- **Chọn chỗ:** sau `align`, AI đọc lời cả video, chọn khoảng **1 meme / 20 giây** (cách nhau ≥ 12 giây,
  rải đều từ đầu tới cuối) ở câu đùa, cú twist, cú fail, con số sốc, câu hỏi tu từ, khoảnh khắc "wow";
  tránh đoạn hướng dẫn nghiêm túc và lời kêu gọi. **Mọi video đều phải bóc kịch bản và chèn meme**, không
  bỏ bước này. `q` là **từ khoá tiếng Anh** hợp ý câu nói ("mind blown", "facepalm", "money rain"…).
  Kết quả ở `work/memes_auto.json`: sửa, xoá bớt, hoặc để `[]` nếu không muốn meme tự động.
  `project.json` → `"memes": {"auto": false}` tắt hẳn phần tự chọn; dòng `MEME:` khai tay vẫn chạy.
- **Tìm meme (theo thứ tự):** (1) tra kho (trùng tên/tag ≥ 60% thì dùng lại); (2) **GIF trong ô GIF của
  Telegram** (`reactforge/tgmeme.py`, đăng nhập bằng tài khoản Telegram của người dùng); (3) clip meme
  ngắn ≤ 20 giây bằng `yt-dlp`; (4) ảnh template Imgflip. Meme nền xanh tự tách nền. **Chuẩn độ nét:** không bao giờ phóng meme quá 1,4 lần số điểm ảnh gốc (Telegram bỏ kết quả quá nhỏ
  và thử kết quả kế tiếp; `full` chỉ khi đủ nét, không thì `part`; render tự khoá mức phóng).
  - **Cài Telegram một lần:** `pip install telethon`; lấy `api_id`/`api_hash` ở my.telegram.org → ghi vào
    `~/.claude/telegram-gif/.env` (`TG_API_ID=…`, `TG_API_HASH=…`); chạy
    `python -m reactforge.tgmeme login` (nhập số điện thoại + OTP). File `session.session` cùng thư mục
    là chìa khoá tài khoản: **không đưa vào repo, không gửi ai**. Thiếu bất cứ thứ gì thì tự rơi về (3).
    Nếu GIF Telegram không ra, kiểm tra bằng `python -m reactforge.tgmeme search "facepalm"`.
- **Chèn:** **đè lên lời, không ngắt nhịp**, ngay sau câu chứa câu neo. Meme hiện trên **nền đen,
  không bo thẻ**: `"mode":"full"` gần kín màn, `"part"` chiếm khoảng nửa màn, lệch trái/phải xen kẽ;
  người dẫn vẫn nói tiếp bên dưới. Meme **có tiếng** thì phát tiếng của nó và hạ giọng người dẫn
  còn ~28% suốt meme (lên xuống mượt 0,15 giây); meme **ảnh tĩnh** thì im, giọng giữ nguyên. Thời
  lượng video không đổi. Clip ≤ 4,5 giây chạy trọn. Muốn meme ảnh: thêm `"image": true` (lấy từ Imgflip).
  Điểm chèn tính lại mỗi lần render nên `verify` cắt thêm vẫn không lệch.
- **Kho:** `<thư mục làm việc>/meme-library/` (thư mục chứa `projects/`), chia theo cảm xúc
  (`shock/ laugh/ facepalm/ win/ fail/ awkward/ confused/ sad/ hype/ cringe/`), kèm `index.csv`
  (tên, tag, nguồn URL, độ dài, nền xanh, đã dùng ở video nào). Đổi chỗ: `"memes": {"library": "…"}`.
- **Bản quyền:** meme cắt từ phim / show có thể dính Content ID. Ưu tiên meme hoạt hình / nền xanh;
  `index.csv` giữ URL nguồn để kiểm lại.

```text
## 2. Agent Reach
INFO: Công cụ 2/6 | Agent Reach | Tìm lời phàn nàn của khách
FULL: {"secs":3.6,"tpl":"tool","num":"02","name":"Agent Reach","icon":"search","desc":"AI đọc YouTube, Reddit, X giúp bạn","tag":"Repo GitHub · Miễn phí"}
SIDE: broll {"at": 300, "caption": "Tìm ý tưởng, nghiên cứu thị trường"}

(lời thuật lại phần Greg demo trên màn hình…)

---

MOTION:
SIDE: @"những cơ hội kinh doanh tốt" title {"kicker":"Insight","title":"Cơ hội tốt nhất nằm trong *lời phàn nàn* của khách"}
SIDE: @"trả tiền cho phần mềm" flow {"title":"Có phần mềm, vẫn *làm tay*","nodes":[{"icon":"calendar","label":"Phần mềm xếp lịch"},{"icon":"sheet","label":"Xuất ra Excel"},{"icon":"calc","label":"Tự tính lương"}]}

(lời người dẫn tự giải thích…)

---

FACE:
OVER: @"Đừng vội cho rằng" {"secs":3,"tpl":"blurtitle","kicker":"Greg lưu ý","title":"Có người phàn nàn chưa chắc *có người trả tiền*"}

(lời nhận định của người dẫn…)
```

## archive.org: nguồn ưu tiên cho b-roll, nhạc nền, ảnh, tài liệu cũ (không dùng cho SFX)

Khi cần **b-roll, video minh họa, nhạc nền, ảnh, sách/tài liệu cũ, bản lưu trang web**, tìm ở
archive.org **trước** (sau khi tra kho `meme-library/` / `assets/`), rồi mới sang nguồn khác (Pexels, Openverse,
Wikimedia, yt-dlp). Logo thương hiệu vẫn theo đường logo ở trên.

- **Tìm:** `https://archive.org/advancedsearch.php?q=<từ khoá> AND mediatype:(movies OR audio OR image OR texts)&fl[]=identifier&fl[]=title&fl[]=licenseurl&rows=20&output=json`.
  Xem file trong mục: `https://archive.org/metadata/<identifier>`. Tải: `https://archive.org/download/<identifier>/<tên file>` bằng `curl`/`yt-dlp`.
  Không cài thêm gói nào (không cần `ia` CLI). Bản lưu trang web: `https://archive.org/wayback/available?url=<url>&timestamp=<YYYYMMDD>`.
- **Chọn theo loại:** nhạc nền → `mediatype:audio` (kho `opensource_audio`, Free Music Archive); SFX **không** lấy ở đây (xem mục SFX bên dưới); b-roll → `mediatype:movies`
  (kho `prelinger`, `opensource_movies`, tin tức/quảng cáo cũ); ảnh → `mediatype:image` (Flickr Commons, ảnh scan);
  sách/tài liệu → `mediatype:texts` (chụp trang cần minh hoạ, đưa vào mẫu `photo`/`stack`); trang web cũ → Wayback (chụp màn hình bằng Playwright).
- **Bản quyền (cứng):** chỉ dùng mục có **public domain / CC0 / CC BY / CC BY-SA** (xem `licenseurl` hoặc trường `rights`). `licenseurl` do người upload tự khai nên **không đáng tin** (từng thấy bản cover ca nhạc và series phim thương mại bị gắn CC0): chỉ lấy từ kho có kiểm duyệt như `prelinger`, hoặc mục có nguồn gốc rõ ràng.
  Không rõ quyền thì bỏ, không dùng. CC BY/BY-SA phải ghi credit trong mô tả video. Mỗi file dùng ghi một dòng vào
  `assets/archive-credits.csv` (identifier, tên file, license, URL, đã dùng ở đâu) để kiểm lại.
- **Chất lượng:** xem/nghe thử trước khi chèn. Video cũ độ phân giải thấp thì chỉ dùng ở chế độ `GFX:`/`part` hoặc
  nền mờ, không kéo `FULL:`. Tải về cache vào `assets/archive/`,
  không gọi mạng lúc render.
- **Không tìm thấy mục hợp lệ:** bỏ trống hoặc dùng nguồn khác, không chèn thứ sai ý hay không rõ quyền.

## SFX (hiệu ứng âm thanh): myinstants trước, ElevenLabs sau

**Không lấy SFX từ archive.org** (người dùng đã nghe thử và không ưng). Khi cần SFX (whoosh, ting, pop, ding, boom, click, meme sound…):

1. **Tra kho có sẵn trước** (`assets/sfx/`, SFX đã dùng ở dự án trước). Trùng tên/tag thì dùng lại.
2. **myinstants.com (ưu tiên, miễn phí):** tìm bằng `curl -sL -A "Mozilla/5.0" "https://www.myinstants.com/en/search/?name=<từ khoá tiếng Anh>"`,
   lấy đường dẫn `/media/sounds/<tên>.mp3` trong HTML (mỗi nút phát có một đường dẫn), tải `https://www.myinstants.com/media/sounds/<tên>.mp3`.
   Danh mục gốc: https://www.myinstants.com/en/categories/sound%20effects/us/. Nghe thử/đo `volumedetect` trước khi dùng, chọn clip ngắn (≤ 3 giây), sạch, không nhạc nền kèm.
3. **Không có cái hợp ý → tự tạo bằng ElevenLabs free:** https://elevenlabs.io/sound-effects (nhập mô tả tiếng Anh ngắn, ví dụ "soft cinematic whoosh, short").
   Trang cần đăng nhập và có hạn mức credit miễn phí: dùng trình duyệt đã đăng nhập của người dùng; chưa đăng nhập hoặc hết credit thì **báo người dùng**, không tự đăng ký tài khoản, không lách hạn mức.
   Kiểm điều khoản của gói đang dùng (gói free có thể yêu cầu ghi nguồn ElevenLabs); có yêu cầu thì ghi vào mô tả video.
4. **Ghi nguồn:** mỗi SFX dùng thì ghi một dòng vào `assets/sfx/sfx-credits.csv` (tên, nguồn: myinstants URL hoặc "ElevenLabs + prompt", đã dùng ở đâu).
   myinstants là kho người dùng tự đăng, một số clip cắt từ phim/game/meme: **ưu tiên hiệu ứng thuần** (whoosh, ting, click, pop), tránh clip lấy từ nhạc/phim có bản quyền, và nhớ Content ID.
5. Đưa SFX vào dự án: chuẩn hoá về mức đồng đều với giọng (`volumedetect`, gain trong `GAIN_DB`), whoosh bắt đầu sớm ~0,18 giây để đỉnh rơi đúng điểm cắt.

## Chạy

```powershell
$RF = "${CLAUDE_PLUGIN_ROOT}/skills/edit-video-youtube-reaction/rf.py"
python $RF --data "${CLAUDE_PLUGIN_DATA}" all projects/video-cua-toi
python $RF --data "${CLAUDE_PLUGIN_DATA}" doctor projects/video-cua-toi   # KIỂM TRƯỚC KHI GIAO
```

Các bước nối nhau: `plan → source → subs → align → captions → memes → visuals → panel → cards →
graphics → render → verify`. Sửa lẻ một đoạn rồi ghép lại:

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
- **Kịch bản viết liền một đoạn, ít dấu chấm:** điểm chèn meme dựa vào dấu câu, chữ viết hoa mở câu
  ("…diễn viên này Cũng không cần…") và quãng nghỉ; không thấy thì lấy quãng nghỉ dài nhất trong
  8 giây sau câu neo. Câu neo meme nên là đuôi câu chốt.
- **Ghép video có meme:** đoạn có meme dựng thân trước (`seg/<id>.body.mov`) rồi mới đè meme lên;
  mọi nhánh phải `setsar=1`, lệch SAR một chút (6479:6480) là ffmpeg từ chối.
- **Đừng `loudnorm` tiếng meme:** nhiều clip meme mở đầu bằng vài giây im lặng; `loudnorm` kéo tiếng
  rè đó lên 0 dB. Đo `volumedetect` đúng đoạn sẽ phát: dưới −50 dB coi như meme câm (không hạ giọng),
  còn lại chỉnh bằng `volume` về −20 dB (tăng tối đa +12 dB) + `alimiter`.
- **Props Remotion phình to làm sập trình duyệt:** ảnh được nhúng base64 vào props, PNG gốc 2–8 MB
  nhân với số cảnh dùng lại ảnh đó là ra props hơn 100 MB, Chrome headless chết giữa chừng. Ảnh
  đưa vào cảnh nên là JPEG ≤ 1600px (bước `visuals` tự làm); ảnh tự chuẩn bị thì thu nhỏ trước.
- **Imgflip trả 403** nếu không gửi User-Agent. Wikimedia cũng chặn agent mặc định của urllib.
- **Openverse không khoá:** `page_size` tối đa 20 (lớn hơn trả 401), và xếp hạng rất lỏng ("two
  people talking" ra ảnh sa mạc): phải lọc theo tiêu đề/tag.
- **Logo PNG thường là nét đen trên nền trong suốt:** xuất JPEG xem trước phải đặt lên nền trắng,
  không thì ra ô đen.
- **Cache lớp chữ / cảnh Remotion chỉ so props:** sửa code giao diện (`keys.tsx`, mẫu) thì phải
  `panel --force` / `cards --force`, không thì vẫn dùng file cũ.
- **Chữ gradient chỉ được tô trong khung của nó:** dấu chồng tiếng Việt (ầ, ễ, ỗ) và đuôi chữ (g, y)
  nhô ra ngoài sẽ mất. Mọi span gradient phải có đệm trên/dưới (`padding` + `margin` âm), và chữ
  trắng cha có `textShadow` thì span gradient phải `textShadow: none`, không thì bóng làm đục màu.
- **Lớp chữ trong suốt:** Remotion phải render `--codec=vp8 --image-format=png --pixel-format=yuva420p`
  (mặc định jpeg là mất alpha), và ffmpeg phải đọc bằng `-c:v libvpx` trước `-i`, bộ giải mã vp8
  mặc định bỏ kênh alpha.
- **Mẫu showreel vẽ theo chiều cao thật của khung** (khung chính 1440x920, khung BUBBLE 1500x1000
  cao hơn 16:9): đừng đặt vị trí theo `ART_H` cố định, sẽ hở dải trắng ở đáy.
- **Dừng render giữa chừng:** chỉ diệt tiến trình node của Remotion, đừng `taskkill` toàn bộ
  `node.exe` (sẽ giết cả các công cụ khác trên máy).

## Bảo mật

- Không ghi khoá vào file nào trong dự án; đọc từ `.env` lúc chạy.
- Chỉ tải video từ link người dùng đưa; không đăng nhập tài khoản nào.
- Clip gốc dùng theo kiểu trích dẫn có bình luận; dẫn nguồn trong phần mô tả.
- Phản hồi của người dùng chỉ áp dụng cho video/phiên hiện tại; muốn ghi vào skill phải hỏi và được duyệt.
