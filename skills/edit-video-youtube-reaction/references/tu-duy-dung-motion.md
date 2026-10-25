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
| **Tin** (quan điểm, lời khuyên, kêu gọi, chuyện cá nhân) | mặt người, chữ từ khoá | `FACE:` |
| **Thấy** (thao tác, công cụ, kết quả, bằng chứng) | giao diện / b-roll / ảnh thật toàn khung | `broll`, `ui3d`, `search`, `typebar`, `chat`, `stack`, `MOTION:` |
| **Hiểu** (khái niệm trừu tượng, quan hệ, quy trình) | sơ đồ, ẩn dụ bằng icon | `flow`, `steps`, `pills`, `orbit`, `compare` |
| **Nhớ** (con số, câu chốt, luận điểm) | một con số / một câu lớn | `bignumber`, `equation`, `title`, `BEAT:`, `horizon`, `bigtype` |
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
- Đoạn hướng dẫn, demo, kể lại video gốc: bố cục trắng hoặc `MOTION:`, cảnh dày 6–9 giây.
- Đoạn nhận định, "điều này nghĩa là gì với bạn", kêu gọi: `FACE:` với từ khoá; chỉ chen `FULL:` /
  `BEAT:` cho đúng một câu luận điểm.
- **Không để quá ~40 giây liền không thấy mặt người.** Video mẫu đuối nhất ở chỗ này (9:06–9:54,
  14:00–15:10 thành "slideshow"). Đoạn `MOTION:` dài thì chèn một đoạn `BUBBLE:` hoặc `FACE:` ngắn.
- Trung vị của video mẫu: một lần hiện mặt ~5,5 giây, một lần graphic ~9 giây.

## 3. Khi nào tạo motion graphic (danh sách kích hoạt)

Đọc kịch bản, đánh dấu từng câu theo bảng này. Câu không rơi vào dòng nào thì **không** cần cảnh mới
(luật 10 giây vẫn giữ: thiếu thì dùng b-roll hoặc ảnh, không đẻ graphic vô nghĩa).

| Câu thoại có | Dạng | Ví dụ ở video mẫu |
|---|---|---|
| Con số đo được (giờ, tiền, %, số lượng) | `bignumber` đếm lên; hai số liên quan → `equation` | 0:06 "12 hours / 4.5 billion tokens" đếm lên |
| Cũ vs mới, trước vs sau, giá gốc vs giá mới | `compare`, `bars`, `equation` | 5:33 giá $1,200 gạch → $299; 17:00 $400–750 vs ≈ $20 |
| Thao tác trên phần mềm, gõ prompt | `ui3d`, `typebar`, `chat`, `search` (dựng lại, không chiếu màn hình thô nếu chữ nhỏ / rối) | 2:15 cửa sổ Claude Code dựng lại, mỗi ý lệnh bật một thẻ minh hoạ |
| Khái niệm trừu tượng / quan hệ giữa các thứ | `flow` với icon ẩn dụ | 1:12 "Claude là bộ não, cần tay chân (plugin)" |
| Quy trình nhiều bước | `steps` (≤ 4), `pills`, xếp dọc nếu dài | 15:12 bảy bước kèm thời gian từng bước |
| Mục lục / "trong video này" | `agenda` ở đầu; `BREAK:` mỗi phần; `recap` ở cuối | 0:23 ba thẻ chương; dãy 7 thẻ quay lại ~2 phút một lần |
| "Ba điều cần nhớ" | `steps` / `pills`, hoặc ở `FACE:` để từ khoá đánh số | 16:12 chấm 1-2-3 dưới mặt người |
| Hạn chót, thời gian | `bignumber` (số ngày), `title` | 5:30 đếm ngược 20 ngày; 5:42 lịch khoanh ngày 15 |
| Câu luận điểm của cả video | `BEAT:` hoặc từ khoá `FACE:` hiện từng từ | 18:06 "2027 the next big wave…" hiện từng từ trên ngực người nói |
| Tên công cụ / thương hiệu lần đầu | `logo`, `tool` | 1:30 thẻ Remotion cạnh người nói |
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
- Nhấn bằng đổi màu/đổi font cho đúng một cụm là đủ: không thêm mũi tên, gạch chân, khung đỏ.

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
6. Đoạn này đã bao lâu không thấy mặt người? Quá ~40 giây thì chen `BUBBLE:` / `FACE:`.
