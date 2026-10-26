# Tư duy dựng: cắt, nhịp và motion graphic

Học từ video mẫu "học thêm motion graphics" (kênh Joseph | Video Editing, 19:53, style dựng bằng
Claude + Remotion). Số liệu trong file này đo trên chính video đó.

File này trả lời ba câu: **khi nào** tạo motion graphic, **dạng gì**, **nhấn vào ý nào**.
Đọc trước khi viết dòng `SIDE:` / `FULL:` / `BEAT:` / chọn chế độ `FACE:` `BUBBLE:` `MOTION:`.
Âm thanh không nằm ở đây: SFX theo `sound-effects-guide.md` (L1–L23, khoá cứng).

## 1. Câu hỏi gốc cho mỗi câu thoại

Không hỏi "hiệu ứng nào đẹp". Hỏi: **người xem cần gì ở câu này?**

| Người xem cần | Cho họ | Trong skill này |
|---|---|---|
| **Tin** (quan điểm, lời khuyên, kêu gọi, chuyện cá nhân) | mặt người, chữ từ khoá | `FACE:` (+ `OVER:` `dots` / `stats` / `blurtitle`) |
| **Thấy** (thao tác thật trên màn hình) | quay màn hình trong bố cục avatar | bố cục trắng / `BUBBLE:` với `broll`, `screen`, `rec` |
| **Thấy** (giao diện dựng lại, kết quả, bằng chứng) | graphic full màn | `MOTION:` với `promptui`, `ui3d`, `search`, `typebar`, `chat`, `stack`, `doctilt`, `beforeafter`, `comments` |
| **Hiểu** (khái niệm trừu tượng, quan hệ, quy trình) | sơ đồ, ẩn dụ bằng icon, full màn | `MOTION:` với `hub`, `flow`, `steps`, `pills`, `orbit`, `compare`, `tracker` |
| **Nhớ** (con số, câu chốt, luận điểm) | một con số / một câu lớn, full màn | `MOTION:` / `FULL:` với `bignumber`, `pricecut`, `receipt`, `equation`, `title`, `horizon`, `bigtype`; `BEAT:` |
| Không cần gì thêm (câu đệm, chuyển ý ngắn) | giữ nguyên cảnh đang chạy | không khai cảnh mới |

Tác giả video mẫu tự giải thích hai lựa chọn của mình: "chọn animation UI toàn màn hình **để người
xem thấy nó thực sự trông thế nào**" và "chọn animation toàn màn hình **để hình dung khái niệm cho dễ
hiểu**". Lý do luôn đứng trước kỹ thuật.

## 2. Nhịp: tỉ lệ mặt người đi theo chức năng đoạn

Video mẫu: chỉ ~39% khung có mặt người, nhưng **không chia đều**.

- Đoạn trình diễn quy trình (phút 9–15): mặt người 0–15%, gần như toàn graphic / giao diện.
- Đoạn nêu quan điểm, thuyết phục (phút 16–18): mặt người 57–79%, graphic chỉ ở lề.
- Hook: mặt người 0,5 giây rồi cắt ngay sang **bằng chứng** (sản phẩm đẹp), sau đó quay lại mặt
  người kèm con số.

Áp vào skill:

- Hook: `FACE:` nhưng câu tuyên bố đầu tiên phải có bằng chứng thấy được trong ~5 giây đầu
  (`FULL:` ảnh / b-roll kết quả, hoặc `bignumber`). Tuyên bố khó tin mà không có hình là mất người xem.
- **Luật bố cục (khoá cứng):** motion graphic luôn full màn (`MOTION:` / `FULL:` / `BEAT:`); bố cục
  avatar (bố cục trắng, `BUBBLE:`) chỉ để chạy quay màn hình. Xoay vòng ba kiểu: người full màn ·
  motion full màn · bố cục avatar + quay màn hình.
- Đoạn demo trên màn hình thật, kể lại video gốc: bố cục avatar + `broll` / `screen`.
- Đoạn người dẫn tự giải thích, ví dụ, con số: `MOTION:`, cảnh dày 6–9 giây.
- Đoạn nhận định, "điều này nghĩa là gì với bạn", kêu gọi: `FACE:` với từ khoá; số liệu / bước 1-2-3 /
  câu luận điểm thì `OVER:` đè lên người thay vì cắt sang thẻ.
- **Không để quá ~40 giây liền không thấy mặt người.** Video mẫu đuối nhất ở chỗ này (9:06–9:54,
  14:00–15:10 thành "slideshow"). Đoạn `MOTION:` dài thì tách bằng `---` và chen một đoạn `FACE:` ngắn.
- Trung vị của video mẫu: một lần hiện mặt ~5,5 giây, một lần graphic ~9 giây.

## 3. Khi nào tạo motion graphic (danh sách kích hoạt)

Đọc kịch bản, đánh dấu từng câu theo bảng này. Câu không rơi vào dòng nào thì **không** cần cảnh mới
(luật 10 giây vẫn giữ: thiếu thì dùng b-roll hoặc ảnh, không đẻ graphic vô nghĩa).

| Câu thoại có | Dạng | Ví dụ ở video mẫu |
|---|---|---|
| Con số đo được (giờ, tiền, %, số lượng) | `bignumber` đếm lên; hai số liên quan → `equation`; đang ở `FACE:` → `OVER: stats` | 0:06 "12 hours / 4.5 billion tokens" đếm lên trên mặt người |
| Giá cũ → giá mới, chi phí giảm | `pricecut` | 5:33 giá $1,200 gạch → $299; 19:24 đếm lùi về giá mới |
| Tổng kết chi phí / thời gian nhiều mục | `receipt` | 16:06 hoá đơn "Time & cost", dòng Tổng đếm lên |
| Cũ vs mới, so sánh nhiều thứ | `compare`, `bars`, `beforeafter` | 17:00 $400–750 vs ≈ $20; 5:21 Before / After |
| Thao tác trên phần mềm, gõ prompt | `promptui` (mỗi dòng lệnh một thẻ minh hoạ), `ui3d`, `typebar`, `chat`, `search` | 2:15 cửa sổ Claude Code dựng lại, mỗi ý lệnh bật một thẻ minh hoạ |
| Tài liệu / kế hoạch thật | `doctilt`, `scriptclip` | 7:30 Figma nghiêng 3D; 7:57 dòng kịch bản cạnh clip |
| Khái niệm trừu tượng / công cụ nhận gì làm ra gì | `hub`, `flow` với icon ẩn dụ | 1:12–1:18 "Claude là bộ não", tài liệu chạy vào, việc bật ra |
| Khối lượng dữ liệu, "AI tự sắp xếp" | `folder` | 3:12 thư mục mở ra hàng trăm thư mục con |
| Cắt ậm ừ, AI đọc lời | `transcript` | 6:39 transcript từng chữ, nhãn Pause |
| Quy trình nhiều bước | `steps` (≤ 4), `pills`, `tracker` (video nhiều chương) | 15:12 bảy bước kèm thời gian từng bước |
| Mục lục / "trong video này" | `chapters` (intro) ở đầu, mỗi `BREAK:` tự quay lại danh sách và zoom vào chương mới; `recap` ở cuối | 0:23 ba thẻ chương; video mẫu 2 (0:30–0:39) danh sách 8 chương, dòng 07 khoanh cam |
| Đoạn nói có ảnh / tư liệu nhiều tấm | thỉnh thoảng `OVER: orbit` (ảnh xoay 3D quanh người, 3–6 giây) | test YouMind: slide Đám cưới chuột bay quanh người khi nói "đưa tài liệu, link, hình ảnh…" |
| "Ba điều cần nhớ" | `OVER: dots` ở `FACE:`; hoặc `steps` / `pills` ở `MOTION:` | 16:12 chấm 1-2-3 dưới mặt người |
| "Có 2 thứ…", gợi tò mò ý sau | `reveal` | 17:45 thẻ 2 úp dấu "?" rồi lật |
| Xu hướng, tăng trưởng, giữ chân | `linechart` | 17:39 đường retention |
| Hạn chót, khuyến mãi | `calendar`, `countdown`, `lock` | 5:30 đếm ngược; 5:42 lịch khoanh ngày 15; 19:18 ổ khoá rơi |
| Đang chờ xử lý / xuất xong | `progress`; ở `FACE:` → `OVER: status` | 7:27 thanh Export xanh; 9:21 "40 minutes to process" |
| Bằng chứng xã hội, kết quả học viên | `comments`, `beforeafter` | 4:48 tường bình luận + "$2,000/mo" |
| Câu luận điểm của cả video | `OVER: blurtitle` (người nói nhoè phía sau) hoặc `BEAT:` | 0:51, 3:48 chữ trên nền mặt nhoè; 18:06 câu luận điểm |
| Tên công cụ / thương hiệu lần đầu | `logo`, `tool` (full màn) | 1:30 thẻ Remotion |
| "Tôi không ngồi máy / cuộc sống thật" | ảnh / b-roll đời thường (`photo`, `stack`) | 12:42 b-roll quay thật duy nhất của video |

**Không tạo** khi: câu chuyển ý ngắn, câu cảm thán, câu đang giữ cảm xúc cá nhân (để mặt người làm việc),
hoặc cảnh trước còn đang minh hoạ đúng ý này.

## 4. Nhấn vào ý nào

- **Mỗi câu một cụm nhấn**, bọc `*…*`, 1–3 từ. Hai cụm nhấn là không cụm nào nổi.
- Chọn từ mang **cảm xúc hoặc kết quả**, không chọn từ chức năng. Video mẫu nhấn: "100% *using AI*",
  "really smart *brain*", "It needs *limbs*", "*beginner's guide*", "*struggling*", "Looked *perfect*",
  "anything *extra*", "*perform*", "*forever*".
- Con số luôn là thứ được nhấn (cỡ lớn, đếm lên); chữ dẫn để nhỏ.
- Ý trùng lặp với cảnh trước thì không nhấn lại; nhấn phần **mới** của câu.
- Nhấn **chữ** (`title`, từ khoá, `BEAT:`) bằng đổi màu/đổi font cho đúng một cụm là đủ: không thêm mũi tên,
  gạch chân, khung đỏ lên chữ.
- **Ngoại lệ: khoanh / gạch chân / bút dạ quang vẽ tay** (Highlight Marks, xem mục 9) được dùng trên **hình**
  (quay màn hình, b-roll, `doctilt`, `photo`) để trỏ đúng chi tiết người dẫn đang nói tới: con số trong bảng giá,
  một nút bấm, một dòng tài liệu. Chỉ màu cam `#D97757`, nét vẽ tay tự chạy ra trong ~0,4 giây, mỗi lúc một dấu.

## 5. Đồng bộ với lời (cách đặt câu neo)

Hai loại graphic, hai luật khác nhau (đo trên video mẫu bằng mốc từ của Whisper):

- **Con số = cú đấm: đáp đúng lúc nói con số.** "12" được nói 0:07.16, bộ đếm chạm 12 ở 0:07.0;
  "six" 3:58.11, chạm 6 ở 3:58.0; "$299" 19:31.9, đếm lùi về đích đúng lúc đó.
  `bignumber` đếm từ khung 8 tới khung 40 (xong sau ~1,3 giây kể từ đầu cảnh), nên **câu neo là 3–5 từ
  đứng ngay trước con số**, không phải chính con số.
- **Câu chữ = kênh đọc: hiện trước lời 1–3 giây.** "brain" nói ở 1:14.6, câu "Claude is a really smart
  *brain*" hiện xong từ 1:12.5. Người xem đọc trước, tai nghe xác nhận lại. Chữ hiện sau lời thì video
  có cảm giác chậm hơn người xem. Câu neo của `title` / `BEAT:` là đầu câu (hoặc cuối câu trước).
- Thẻ minh hoạ theo lời liệt kê (mỗi ý một thẻ) bật ra **khi người nói bắt đầu ý đó**, không đợi
  nói xong (2:30–2:45 ở video mẫu).

## 5b. Hiện theo lời, không hiện cả loạt

Phần tử trong một cảnh không được bật ra hết ngay đầu cảnh. Mỗi mục danh sách hiện đúng lúc người dẫn nói tới nó
(pipeline tự dò lời, xem SKILL.md). Khi đặt tên mục, dùng đúng chữ người dẫn nói để pipeline dò được.

## 6. Nhất quán: một hệ thống nhìn, không phải bộ sưu tập hiệu ứng

- **Một ngôn ngữ chuyển cảnh, lặp lại.** Video mẫu dùng gần như duy nhất kiểu nhoè → nét 0,2–0,5 giây
  (0:00.67, 0:23, 7:28, 15:10, 17:17, 19:18). Không đổi kiểu chuyển cảnh mỗi lần để "cho đỡ chán".
- **Một khái niệm = một icon suốt video.** Biểu tượng não ở 1:12 quay lại ở 3:48, 10:00, 17:45:
  người xem không phải giải mã lại. Khi khai `flow` / `pills` / `logo`, giữ cùng `icon` cho cùng
  một thứ từ đầu tới cuối.
- **Bản đồ chương.** Video dài nhiều bước cần chỗ cho người xem biết "đang ở đâu": `agenda` sau hook,
  `BREAK:` có `num` ở mỗi phần, `recap` ở cuối liệt kê lại đúng các mục đã hứa ở `agenda`
  (cùng tên, cùng thứ tự).
- **Quảng cáo / kêu gọi dùng cùng bộ màu và mẫu** với phần nội dung, không đổi sang phong cách khác.

## 7. Khi nào hiệu ứng chỉ là trang trí (bỏ)

- Cảnh mới không thêm thông tin so với lời và cảnh trước.
- Chuyển động không có hướng nghĩa (trượt ngang giữa hai ví dụ cùng loại, xoay cho vui).
- Nhiều lớp giao diện nối nhau > 30 giây chỉ để tạo cảm giác "nhiều việc".
- Đã có hai cảnh liền nhau cùng dạng (luật cũ: hai cảnh liền nhau không cùng dạng).

## 8. Kiểm trước khi khai cảnh

1. Câu này người xem cần **tin / thấy / hiểu / nhớ**, hay không cần gì?
2. Dạng chọn khớp mục 3 chưa? Có cảnh trước đang minh hoạ đúng ý này không?
3. Cụm `*nhấn*` có đúng một cụm, là từ cảm xúc / kết quả / con số?
4. Câu neo: con số → neo vào 3–5 từ trước số; câu chữ → neo vào đầu câu.
5. Icon / tên mục có trùng với lần xuất hiện trước của cùng khái niệm?
6. Đoạn này đã bao lâu không thấy mặt người? Quá ~40 giây thì tách đoạn và chen `FACE:`.
7. Graphic có đang nằm trong bố cục avatar không? Có thì chuyển sang `MOTION:` / `FULL:` (bố cục avatar
   chỉ cho quay màn hình). Ngoại lệ duy nhất: lớp nhỏ ở mục 9b (đè lên `FACE:`) và dấu khoanh trên hình.
8. Loại motion đã gọi đúng tên ở mục 9 chưa? Có mẫu sẵn thì dùng; chưa có thì tự code theo 9c, không ép
   một mẫu sai dạng cho có.

## 9. Chọn loại motion theo tình huống (bản đồ 32 loại)

Tên loại theo `motion-graphics-taxonomy.md` (cùng thư mục, có link mẫu xem được và mẫu gốc làm tay).
Mục 3 trả lời "câu này cần cảnh gì"; mục này trả lời "cảnh đó gọi là gì, làm bằng gì". Linh hoạt: một
tình huống có nhiều lựa chọn, chọn theo nhịp đoạn (mục 2) và luật hai cảnh liền nhau không cùng dạng.

### 9a. Bảng tra

| # | Loại (tên chuẩn) | Tình huống trong kịch bản | Làm bằng trong skill |
|---|---|---|---|
| 1 | Karaoke Highlight | lời dài trên quay màn hình | thanh chữ nhảy của bố cục avatar (tự động) |
| 2 | Pop / Word-by-word Captions | hook, câu nhanh ở người full màn | chữ từ khoá `FACE:` (tự động) |
| 3 | Kinetic Typography | câu chốt, slogan, câu "đắt" | `title`, `bigtype`, `horizon`, `BEAT:`; ở `FACE:` → `OVER: blurtitle` |
| 4 | Kinetic Callout / Text Emphasis | một con số / cụm khoá đập vào mắt | `bignumber`, `bigtype`; FACE kiểu chồng (`"big": true`) |
| 5 | Typewriter | gõ câu hỏi, prompt, câu tìm kiếm | `quote`, `typebar`, `search`, `promptui` |
| 6 | 3D Text | — | **không dùng** (bộ màu cấm khối 3D cho chữ) |
| 7 | Lower Thirds | nhân vật / người dẫn xuất hiện lần đầu, cần tên + vai trò | full màn: `person`; ở `FACE:` → **`OVER: lowerthird`** (9b) |
| 8 | Title Card | mở một chủ đề lớn | `title`, `tool`, `horizon` (thẻ `FULL:`) |
| 9 | Chapter / Section Cards | sang phần mới | `BREAK:` → `chapters` / `chapter` (tự động) |
| 10 | Logo Sting / Intro–Outro | kết video | `OUTRO:` (không có intro, luật cũ giữ nguyên) |
| 11 | Animated Charts | xu hướng, trước/sau theo số | `linechart`, `bars` |
| 12 | Stat Callout / Number Counter | một con số đo được | `bignumber`, `pricecut`, `receipt`; ở `FACE:` → `OVER: stats` |
| 13 | Progress Bar / Ring | đang xử lý, mới đi được X% | `progress`; ở `FACE:` → `OVER: status` |
| 14 | Timeline / Steps / Checklist | quy trình, danh sách, video nhiều bước | `steps`, `pills`, `flow`, `checklist`, `tracker`, `agenda`, `recap`; ở `FACE:` → `OVER: dots` |
| 15 | Comparison / Before–After | cũ vs mới, trước vs sau | `compare`, `beforeafter`, `bars` |
| 16 | Quote Card | trích lời nhân vật / khách hàng | `quote` |
| 17 | Callout / Annotation | chỉ vào một thành phần trên hình đang chiếu | dấu chỉ điểm trên quay màn hình / `doctilt` / `photo` (9b) |
| 18 | Highlight Marks | khoanh đúng con số / nút / dòng trên hình | dấu khoanh cam vẽ tay trên hình (9b, mục 4) |
| 19 | Zoom / Punch-in | câu chốt ở người full màn | `FACE:` punch 1.15 (tự động); b-roll tự zoom trượt |
| 20 | Subscribe / Like / Bell | lời kêu gọi đăng ký giữa / cuối video | ở `FACE:` → **`OVER: subscribe`** (9b) |
| 21 | End Screen / End Card | 10–20 giây cuối | `OUTRO:` + lời kêu gọi; cần ô gợi ý video tiếp → mẫu `endscreen` (9c) |
| 22 | Social Post / Comment Mockup | bình luận, bằng chứng xã hội, đoạn chat | `comments`, `chat` |
| 23 | Notification Pop | "đơn mới", "tin nhắn mới", cảnh báo bật lên | ở `FACE:` → **`OVER: notify`** (9b); full màn → `chat` |
| 24 | Price Tag / Product Card | nói giá, giới thiệu sản phẩm | `pricecut`, `logo`; có ảnh sản phẩm → mẫu `product` (9c) |
| 25 | Discount Badge / Promo Sticker | ưu đãi, freeship, % giảm | ở `FACE:` → **`OVER: badge`** (9b); hạn chót → `countdown`, `lock` |
| 26 | Picture-in-Picture | quay màn hình + mặt người | `BUBBLE:`, bubble tròn của `MOTION:` (tự động) |
| 27 | Split Screen | đặt hai thứ cạnh nhau cùng lúc | `compare`, `beforeafter`; hai video chạy song song → mẫu `split` (9c) |
| 28 | Motion Backgrounds | nền của thẻ | nền than + quầng cam có sẵn; không thêm nền khác |
| 29 | Sticker / Emoji | phản ứng vui, ngắn | không chèn meme; cần sticker nhỏ ở `FACE:` → `OVER: sticker` (9b), rất hạn chế |
| 30 | Transitions | nối hai cảnh | chỉ ngôn ngữ chuyển cảnh có sẵn: co/giãn, morph, nhoè → nét. **Không** thêm wipe / glitch / slide |
| 31 | Light Leaks / Flares | — | **không dùng** |
| 32 | Map / Route | chỉ khi kịch bản nói về địa điểm, hành trình | mẫu `map` (9c), hiếm |

### 9b. Lớp nhỏ đè lên người nói (ngoại lệ của luật "motion full màn")

Lower Thirds (`lowerthird`), Subscribe/Bell (`subscribe`), Notification Pop (`notify`), Discount Badge
(`badge`), Sticker (`sticker`) **được** đè lên người nói ở đoạn `FACE:` qua dòng `OVER:`, vì chúng là
nhãn phụ, không phải nội dung chính:

- Chiếm ≤ 1/4 khung, nằm ở 1/3 dưới hoặc góc trên; không che miệng, không trùng giờ với cụm từ khoá
  (trùng thì cụm từ khoá nhường như các lớp `OVER:` khác).
- Mỗi lúc một lớp nhỏ, 2–4 giây, hiện theo câu neo rồi tự tan. Dùng bộ màu chung: nền than, chữ kem, nhấn cam.
- `lowerthird` chỉ ở lần đầu nhân vật xuất hiện; `subscribe` tối đa 2 lần một video (giữa và cuối),
  đúng lúc người dẫn kêu gọi.
- Sơ đồ, số liệu, quy trình, logo, ảnh **vẫn phải full màn**: lớp nhỏ không phải đường tắt để nhét graphic
  cạnh mặt người.

Callout / Highlight Marks (17, 18) nằm **trên hình đang chiếu** (quay màn hình trong bố cục avatar, `doctilt`,
`photo`), trỏ đúng chi tiết đang được nói, không dùng trên chữ.

### 9c. Loại chưa có mẫu: tự code khi kịch bản thật cần

Chưa có mẫu sẵn: `lowerthird`, `subscribe`, `notify`, `badge`, `sticker`, dấu khoanh / chỉ điểm trên hình,
`endscreen`, `product`, `split`, `map`. **Không code trước cho đủ bộ**; video nào cần thì code đúng lúc đó:

1. Mở link mẫu của loại đó trong `motion-graphics-taxonomy.md` (ưu tiên 🎨 mẫu gốc làm tay) để lấy nhịp và bố cục.
2. Code bằng bộ màu và `kit` có sẵn (xem `motion/TEMPLATES.md` → "Tự code mẫu mới"). Mẫu full màn vào
   `src/custom/`; lớp nhỏ đè người phải đăng ký thêm vào bảng `OVERS` trong `src/light/keys.tsx`; dấu khoanh trên
   quay màn hình phải thêm props vào cảnh `broll` / `screen` (bước `doctor` hiện chỉ cho ba mẫu này trong bố cục avatar).
3. `npx remotion still` một khung để soi trước khi dựng cả bài; ổn thì ghi mẫu vào `TEMPLATES.md` để video sau
   dùng lại.

Không có loại nào khớp tình huống thì cũng tự code dạng mới theo đúng quy trình trên, miễn qua được mục 1 và 7
(người xem cần gì, có phải trang trí không).
