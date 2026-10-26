# Intro kiểu match cut (hình ảnh ↔ mặt người full khung, nhạc dồn, chữ nhấn)

Học từ video mẫu "học cách match cut và nhịp, sound effect" (intro phim tài liệu *The Dark World of
Megachurches*, 132 giây, 79 cảnh) và áp thử thành công trên intro video Jensen Huang GTC Berlin
(26/10/2026, người dùng duyệt). Đây là **công thức mặc định cho đoạn intro** của mọi video react: từ
câu đầu tiên tới hết đoạn hook, **trước** câu "trong video này có N ý" (phần mục lục để nguyên).

## 1. Đo được gì ở video mẫu

| Hồi | Thời gian | Cảnh | Trung vị độ dài cảnh | Nội dung |
|---|---|---|---|---|
| Mồi câu chuyện | 0–21 s | 14 | 1,3 s | lời dẫn cá nhân, mỗi danh từ một hình |
| Vụ việc chính | 21–71 s | 22 | 1,5 s | để nguyên câu trích gốc (dài nhất 9,5 s), rồi dồn bằng chứng |
| Dồn dập | 71–122 s | 27 | 1,6 s | toàn câu trích nhân vật, ghép hỏi–đáp |
| Cao trào | 122–129 s | 15 | **0,37 s** | cắt cực nhanh, chớp sáng, impact vào thẻ tên phim |

- Mặt người dẫn chỉ ~15 % thời lượng hook, mỗi lần 1,5–3,5 s, **chỉ ở câu ngôi thứ nhất** ("tôi chưa
  từng nghe…", "đây đúng là hang thỏ").
- Nhạc nền chạy suốt; **nhạc tắt ~1 s trước câu chốt rồi nổ lại** đúng lúc sang hồi mới; cuối intro
  impact lớn rồi nhạc tắt hẳn, chỉ còn đuôi vang.
- Chỉ ~10 SFX trong 132 s, đều ở ranh giới ý (film burn + sub drop, chớp trắng + hit, nháy đen + tách,
  vệt sáng + whoosh, thẻ tên + impact). **Cắt thường: im lặng.**

## 2. Công thức (khoá cứng cho intro)

1. **Mỗi danh từ một hình, hình đến trước lời 0,1–0,3 s.** "Ngày 21/10" → sân khấu; "Jensen Huang" →
   Jensen; "CEO của Nvidia" → logo; "87 phút" → thẻ số; "tại Berlin" → địa điểm; "chip AI" → con chip;
   "ChatGPT hay Claude" → hai logo. Câu liệt kê: mỗi mục một cảnh.
2. **Mặt người full khung ~20–30 %**, mỗi lần 1,4–2,5 s, ở câu nhận định / ngôi thứ nhất. Punch-in
   (phóng 1,15 lần vào mặt) đúng chữ nhấn ("quan trọng", "rất đáng").
3. **Cảnh 0,8–2 s.** Đoạn liệt kê / cao trào: 0,33–0,4 s một cảnh, **cắt đúng phách nhạc**.
4. **Match cut thật sự** — chọn và cắt khung để hai cảnh liền nhau trùng:
   - **mặt ↔ mặt:** cảnh nhân vật (Jensen) phóng/cắt khung để mặt nằm cùng độ cao, cùng cỡ với mặt
     người dẫn ở cảnh sau (đo bằng nhận diện mặt, đừng đoán); người dẫn vào ở khung chặt 1,15;
   - **cùng bố cục:** hai thẻ số liệu cùng layout, chỉ đổi số ("15.000 người" → "100+ điểm chiếu");
   - **cùng tâm:** logo này sang logo kia đặt cùng tâm khung;
   - **cùng hình khối / hướng chuyển động:** máy bay → máy bay, tay giơ → tay giơ.
5. **Chuyển động liền mạch:** mọi cảnh tư liệu cùng một tốc độ đẩy vào (push-in ~0,09 %/khung), nên
   chuyển động "chảy" qua điểm cắt. Không zoom ngẫu nhiên từng cảnh.
6. **Chữ highlight vẫn bắt buộc** trên mặt người **và** trên cảnh tư liệu (composition `Keys`, cụm
   2–6 từ, `*từ khoá*` cam, chữ số/câu chốt dùng kiểu `stack`). **Không** đặt chữ đè lên thẻ số liệu,
   thẻ logo, thẻ sơ đồ (đã có chữ riêng); một lúc chỉ một cụm trên màn hình.
7. **Nhạc nền kịch tính** (bắt buộc cho intro này):
   - chọn bài có đoạn lắng → đoạn dồn (có riser) → drop; đo mốc drop bằng phổ;
   - đặt offset sao cho **drop rơi đúng câu chuyển ý lớn** của intro (ví dụ "thông điệp xuyên suốt");
   - cân theo đoạn: nhạc luôn nằm **dưới giọng 12–16 dB** khi có lời (đoạn lắng gain ~0 dB, sau drop
     hạ ~15 dB), cộng sidechain ducking nhẹ (ratio ~2,5) — **đo**, đừng đặt một mức volume cố định
     (lần đầu đặt −12 dB cố định: đoạn lắng tụt còn −58 dB, gần như không nghe thấy);
   - nhạc **tắt sạch** ngay sau từ cuối của intro (L15, 0,3 s) → thẻ tiêu đề + boom (L5).
8. **SFX rất ít, theo luật L1–L23:** nhạc gánh nhịp. Intro ~45 s chỉ cần 2–3 tiếng: một whoosh mềm ở
   chuyển ý có chuyển động (L1), im lặng trước câu kết (L15), boom ở thẻ tiêu đề (L5).
   **Không** đặt swipe ở từng điểm cắt montage (đã thử: 11 tiếng swipe nghe "lỏ" — phạm E1), **không**
   dùng tiếng điện tử / sci-fi cho phim tư liệu (phạm E3). Nguồn: myinstants trước, ElevenLabs sau;
   không nghe được thì vẽ phổ chọn mẫu sạch (một cú đập gọn + đuôi tắt dần, không lẫn nhạc / giọng).
9. **Kết intro:** im lặng 0,3 s → thẻ tiêu đề 1,8 s (flash trắng 2 khung, chữ đập từ to về đúng cỡ,
   ảnh nền mờ là một cảnh đẹp của video gốc) + boom → vào câu "trong video này có N ý".

## 3. Cách dựng (đã chạy được)

Intro dựng **ngoài** pipeline chính bằng một script EDL rồi ghép vào đầu `final.mp4`:

1. Lấy mốc từng từ của đoạn intro (`timed_words_for` của talk đầu tiên).
2. Viết EDL `(bắt đầu, kết thúc, loại, tham số)` theo đúng mốc từ: `src` (khung video gốc, `at` giây,
   tuỳ chọn `crop` để khớp mặt), `face` (bản quay, danh sách `(mốc, (zoom, top))` cho punch-in), `card`
   (thẻ Remotion tự code: số liệu, logo, tiêu đề), `slice` (cắt một đoạn thẻ đã render), `black`.
3. Mỗi cảnh render riêng **đúng số khung** (`round(b*30) - round(a*30)`) rồi `concat -c copy`.
4. Lớp chữ: composition `Keys` (`--codec=vp8 --image-format=png --pixel-format=yuva420p`), đè bằng
   `overlay` (đọc bằng `-c:v libvpx` để giữ alpha).
5. Tiếng: giọng lấy từ chính `final.mp4` (cùng timeline, đã chuẩn hoá), nhạc + SFX `adelay` + `amix
   normalize=0` + `alimiter`; kiểm tổng ~ −15 LUFS.
6. Ghép (cách duy nhất đã chạy đúng, lệch 0 khung / 0 s ở mọi mốc):
   - **sao lưu `final.mp4`**;
   - cắt đuôi `final.mp4` **đúng biên khung** (vd. `-ss 44.8333333` sau `-i`, encode lại, `-r 30`);
   - đổi cả intro và đuôi sang file trung gian `.mkv` **tiếng PCM** (`-c:v copy -c:a pcm_s16le`, intro thêm
     `atrim=end=<độ dài>,apad=whole_dur=<độ dài>`) để hình và tiếng dài bằng nhau tuyệt đối;
   - `-f concat` (demuxer) hai file `.mkv` → encode H.264 + AAC một lần.
   Chạy lại `render --concat` sẽ ghi đè bản đã ghép → phải ghép lại.

Script mẫu đầy đủ: `references/intro-match-cut-build-example.py` (dự án Jensen; đổi đường dẫn, EDL,
cụm chữ, mốc nhạc cho video mới).

## 4. Bẫy đã gặp

- **`zoompan` ở 1080p làm hình rung** (làm tròn toạ độ theo từng điểm ảnh): upscale 4K → `zoompan` →
  thu về 1080p. Đo được độ giật giảm từ 1,79 xuống 0,69.
- **Video gốc 59,94 fps:** phải `fps=30` **trước** `zoompan`, không thì cảnh bị quay chậm gấp đôi.
- **Chọn khung tư liệu:** kiểm `scdet` trong từng đoạn cắt, tránh đoạn có điểm chuyển camera bên trong
  (một cảnh 0,4 s mà đổi góc máy giữa chừng là giật).
- **`-t` đặt sau `-i`** cắt luôn phần `apad` → mất thẻ tiêu đề cuối; đặt `-t` trước `-i`.
- **Ghép intro vào `final.mp4` — 4 lần hỏng trước khi đúng:**
  bộ lọc `concat` với input có `-ss` mất ~48 s hình, tiếng trôi 0,2 s; bộ lọc `concat` + `trim` cũng hỏng
  (hình dừng ở 223 s); `-f concat` với file trung gian tiếng **AAC** lệch 2 khung cả phần sau, vì demuxer nối
  file sau vào sau luồng dài nhất của file trước, mà AAC có đệm nên tiếng dài hơn hình ~0,06 s. Đúng: file
  trung gian tiếng PCM, cắt đúng độ dài (mục 3 bước 6).
- **Mọi clip của intro phải cùng một định dạng màu** (BT.709, tv range): thẻ Remotion ra `yuvj420p` full
  range, clip video ra `yuv420p` tv range; đổi định dạng giữa luồng làm ffmpeg dựng lại bộ lọc, bộ đếm khung
  về 0 → rớt khung ở mỗi điểm nối (đã mất 3 khung, cả phần sau hình sớm hơn tiếng 0,1 s). Chuẩn hoá từng clip
  (`scale=out_range=tv:out_color_matrix=bt709,format=yuv420p` + gắn tag màu), và `setpts=N/30/TB` trước
  overlay. Đừng chữa bằng `tpad` (đã thử: làm hình dài hơn tiếng).
- **Kiểm trước khi giao:** intro `nb_frames == round(độ dài × 30)`; cắt đuôi `final.mp4` **đúng biên khung**
  (vd. 44,8333 chứ không 44,85, rơi giữa hai khung lệch 1 khung); ghép xong so hình + tiếng ở vài mốc cuối
  video với bản cũ: lệch khung = 0, tiếng không trôi.
- **Đo nhạc trong bản mix bằng cách trừ giọng là sai** (limiter làm lệch); xuất riêng nhánh nhạc sau
  ducking rồi đo.
- **Nhạc từ archive.org:** giấy phép do người upload tự khai, cùng tác giả mà chỗ ghi CC BY chỗ ghi
  BY-ND → lấy thẳng từ trang chính chủ (vd. incompetech.com cho Kevin MacLeod, CC BY 4.0) và ghi
  credit vào `assets/music/music-credits.txt` để đưa vào mô tả video.
