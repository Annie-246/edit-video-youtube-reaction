# Bản Chỉ Dẫn Sound Effect (SFX) — Khi Nào Chèn Tiếng Gì, Vì Sao, Và Chèn Theo Nhịp Nào

> **Tài liệu này dùng cho 2 việc:**
> 1. **Làm "luật" để train Claude (AI)** — để AI tự biết khi nào chèn SFX loại gì, đặt ở đâu, to nhỏ thế nào khi dựng video (Phần 2 là phần copy thẳng vào skill/prompt được).
> 2. **Dạy học viên** — người nền CapCut, làm talking head + video bán hàng + YouTube, hiểu lý do đằng sau từng tiếng chứ không chèn theo cảm tính.
>
> **Cách đọc:** Phần 0 = lý thuyết nền (đọc 1 lần cho hiểu). Phần 1 = từ điển tra cứu từng loại SFX. Phần 2 = bảng luật cho AI. Phần 3 = lỗi & chống lạm dụng.
>
> **Nguồn lý thuyết chính:** Zella — *Sound Design at Cuts: Whoosh, Impact, Riser* (quy tắc đặt tiếng tại điểm cắt); SozAI/Tim Runia — *The ONLY 3 Sound Effects You Need to Tell Any Story* (whoosh–riser–impact là bộ 3 kể chuyện); MyTasker — *Sound Design for Video: Levels, Mixing and Techniques* (mức âm lượng dB cụ thể); PitchDrift — *Best Practices in Sound Design for Motion Graphics* (tối giản, timing); thư viện phân loại của Epidemic Sound, sfx-kit (CC0), Uppbeat, Hoopr. Chỗ nào là **đề xuất của Muse** (không phải số liệu nguồn) đều ghi rõ.

---

## Phần 0 — Nguyên tắc nền: SFX để làm gì và 3 quy tắc nhịp

### 0.1. SFX trong video có 6 chức năng — mỗi tiếng chèn vào phải thuộc ít nhất 1 chức năng

| # | Chức năng | Giải thích | Ví dụ điển hình |
|---|---|---|---|
| 1 | **Đóng dấu chuyển động** (motion) | Hình đang chuyển động mà không có tiếng sẽ "trôi" và rẻ tiền. Tiếng đi kèm làm chuyển động có trọng lượng và tốc độ. | Whoosh khi chữ bay vào, camera lia nhanh (whip pan), vật trượt qua khung |
| 2 | **Dấu câu cho câu chuyện** (punctuation) | Giống dấu chấm/dấu chấm than trong văn: SFX ngắt nhịp, báo "ý này xong", "điểm này quan trọng". Đây là cách gọi trong nghề: *sound punctuation*. | Impact nhẹ khi kết thúc một ý lớn; ding khi một gạch đầu dòng hiện ra |
| 3 | **Dẫn dắt chờ đợi → thỏa mãn** (tension & release) | Tiếng leo lên tạo căng thẳng/chờ đợi, tiếng "rơi" xuống giải tỏa. Cặp bài trùng kinh điển: riser → impact, hoặc riser → im lặng. | Riser trước lúc công bố giá/kết quả, impact đúng khoảnh khắc công bố |
| 4 | **Phản hồi hành động** (feedback) | Người xem cần "nghe thấy" thao tác trên màn hình để tin nó đã xảy ra — như bấm nút ngoài đời có tiếng tách. | Click khi bấm nút, pop khi bong bóng chat hiện, shutter khi "chụp" lại khung hình |
| 5 | **Xây không khí & tính thật** (atmosphere / realism) | Lớp tiếng nền rất nhỏ làm cảnh có "nơi chốn"; tiếng đồ vật thật (foley) làm hành động đáng tin. Nhóm này phải *gần như không ai nhận ra*. | Room tone quán cà phê dưới B-roll, tiếng giấy khi lật tài liệu, gõ phím khi đang gõ thật |
| 6 | **Tín hiệu cảm xúc / phần thưởng** (reward & emotion) | Tiếng tích cực báo "đúng rồi / được rồi / hay quá" — não người xem ghi nhận như một phần thưởng nhỏ, giữ họ xem tiếp. | Sparkle khi hiện kết quả đẹp, cha-ching khi nhắc doanh số, chime "hoàn thành" khi việc xong |

**Hệ quả thực hành:** một SFX không trả lời được câu *"tiếng này làm nhiệm vụ gì?"* thì bỏ. Đây là nguyên tắc lọc số 1 — cho cả người và AI.

### 0.2. Ba quy tắc nhịp (timing) quan trọng nhất

Mọi SFX chỉ rơi vào 1 trong 3 vị trí tương đối so với hình. Chọn sai vị trí = sai chức năng.

| Vị trí | Tên gọi | Dùng cho | Vì sao hiệu quả |
|---|---|---|---|
| **TRƯỚC điểm hình** | Anticipation (tiếng "dọn đường") | Riser, reverse whoosh — bắt đầu *trước* khoảnh khắc chính khoảng 0,5–2 giây | Tai nghe thấy trước → não chuẩn bị chú ý → khoảnh khắc chính "đã tai" hơn. Riser phải **dừng chết ngay tại** khoảnh khắc chính; cái dừng đột ngột mới là hiệu ứng (theo Zella). |
| **TRÙNG điểm hình** | Hit on the frame (đánh trúng khung) | Impact, pop, ding, click — đỉnh tiếng (transient) rơi **đúng khung hình** sự kiện xảy ra | Não gộp tiếng + hình thành một sự kiện duy nhất → cảm giác "khớp, xịn". Impact lệch sớm chỉ ~50 ms (khoảng 1–2 frame) đã bị cảm nhận là cẩu thả (theo Zella). |
| **Vắt qua điểm cắt** | Straddle (tiếng "ôm" điểm cắt) | Whoosh cho chuyển cảnh có chuyển động — bắt đầu *ngay trước* điểm cắt, đạt đỉnh khi khung hình đổi, đuôi tiếng kéo sang *sau* điểm cắt một chút | Vì whoosh *chính là* âm thanh của chuyển động đó; nó làm hai cảnh dính vào nhau thay vì bị "cắt cụt". |

**Hai ghi chú nhịp nâng cao (từ thực hành mix chuyên nghiệp):**
- **Tránh để đỉnh tiếng đè đúng âm tiết quan trọng của lời nói.** Nếu một SFX buộc phải nằm gần câu nói, xê dịch nó một chút (vài chục ms) để đỉnh tiếng không "nuốt" mất âm tiết chính — người xem vẫn cảm nhận là đồng bộ nhưng nghe rõ cả hai (theo Sound Ideas, kỹ thuật micro-shift trong dialogue mixing).
- **Khoảng lặng là một "SFX".** Riser rồi cắt vào im lặng hoàn toàn tạo tương phản mạnh hơn cả impact. Im lặng đặt ngay sau hook hoặc ngay trước câu chốt (punchline) buộc người xem phải chú ý (theo MyTasker).

### 0.3. Quy tắc âm lượng: giọng nói là vua

Thứ tự ưu tiên khi mix: **giọng nói → SFX → nhạc nền.** Số tham chiếu (theo MyTasker, cho video nói chuyện):

| Lớp âm thanh | Mức tham chiếu | Ghi chú |
|---|---|---|
| Giọng nói (dialogue) | −6 đến −12 dB, tổng thể video chuẩn hóa ≈ −14 LUFS (chuẩn YouTube) | Luôn rõ nhất; mọi lớp khác phải "nhường" |
| SFX | −10 đến −20 dB; thực hành gọn: **nhỏ hơn giọng khoảng 6 dB trở lên** (theo Zella: "khoảng nửa âm lượng của giọng, hoặc nhỏ hơn") | SFX tốt là SFX người xem *cảm* được nhiều hơn *nghe thấy*. Nếu khán giả ý thức rõ "vừa có tiếng whoosh" → tiếng đó đang quá to |
| Nhạc nền khi có người nói | −20 đến −30 dB (tức ducking — nhạc tự hạ xuống dưới lời) | Nhạc có lời hát sẽ luôn "đánh nhau" với lời nói — tránh dùng nhạc có vocal dưới đoạn nói |

**Ducking cho SFX:** khi SFX dài (riser, ambience) chạy qua đoạn có giọng nói, hạ nó xuống (hoặc dùng sidechain compression để nó tự né giọng). SFX ngắn (pop, click < 0,3 giây) ít khi cần duck vì nó không kịp che lời — nhưng vẫn phải nằm dưới mức giọng.

### 0.4. Quy tắc "ít mà đúng"

- Bộ 3 **whoosh – riser – impact** gánh phần lớn nhu cầu kể chuyện của mọi video (theo Tim Runia/SozAI). Học viên và AI nên thành thạo 3 loại này trước, các loại khác là gia vị.
- **Không phải điểm cắt nào cũng có tiếng.** Video cắt mỗi 4–5 giây mà điểm cắt nào cũng kêu thì bản mix biến thành… một bản nhạc gõ (theo Zella). Chỉ "đóng tiếng" cho các điểm cắt *quan trọng*: đổi phần, punch-in (zoom vào mặt), reveal (lộ diện thông tin).
- Năng lượng tiếng phải **khớp năng lượng hình**: chuyển cảnh dissolve nhẹ → whoosh mềm, nhẹ; whip pan → whoosh sắc, nhanh; cắt cứng vào câu khẳng định lớn → impact. **Tiếng lệch tông còn tệ hơn là im lặng** (theo Zella).
- Tiếng "lớn" (impact nặng, boom) là tài nguyên khan hiếm: để dành cho reveal/tít lớn/sự kiện thật sự quan trọng (theo SFXVault). Dùng liên tục thì lúc cần nhấn thật sẽ không còn gì để nhấn.

---

## Phần 1 — Bảng phân loại SFX

> Cột **Nghe thử** trỏ tới kho công khai (Pixabay / Mixkit / Freesound / Epidemic Sound / freesfx) — bấm vào, gõ đúng tên loại vào ô tìm kiếm của kho để nghe các biến thể. Link lấy từ nguồn thật, không tự chế.


| # | Loại SFX (EN + gọi VN) | Nghe như thế nào · Nghe thử | KHI NÀO DÙNG (điểm kích hoạt cụ thể) | Mục đích | Cách chèn & nhịp | Ví dụ: talking head / bán hàng |
|---|---|---|---|---|---|---|
| 1 | **Whoosh** — tiếng "vút", gió quét | Tiếng không khí bị quét nhanh qua tai, dài 0,3–1,5 giây; có biến thể nhẹ (mềm, thoáng — cho dissolve) và nặng (trầm, điện ảnh — cho chuyển động lớn). Nghe thử: [freesfx – Whoosh](https://freesfx.co.uk/sfx/whoosh) | Có **chuyển động thật trên hình**: chuyển cảnh dạng slide/wipe/zoom, chữ hoặc vật bay vào–ra, camera lia nhanh | Đóng dấu chuyển động; nối hai cảnh thành một dòng chảy | **Vắt qua điểm cắt:** bắt đầu ngay trước điểm cắt, đỉnh tiếng trùng lúc khung hình đổi, đuôi kéo sang sau cắt một chút. Độ dài whoosh ≈ độ dài chuyển động. Âm lượng dưới giọng ~6 dB trở lên | Chuyển phần trong video: chữ tiêu đề phần bay vào kèm whoosh nhẹ; lia từ mặt người nói sang B-roll sản phẩm |
| 2 | **Swipe / Swish / Zip** — tiếng "xoẹt" nhanh, sắc | Ngắn và sắc hơn whoosh (0,1–0,4 giây), cảm giác vật nhỏ vụt qua hoặc ngón tay vuốt màn hình. Nghe thử: [Pixabay Sound Effects](https://pixabay.com/sound-effects/) (gõ "swipe" / "zip") | Chuyển cảnh **rất nhanh**, cắt liên tiếp nhiều ảnh/clip ngắn, vuốt qua danh sách, thẻ/card trượt vào nhanh | Tạo cảm giác tốc độ, gọn, hiện đại | Trùng hoặc vắt nhẹ qua điểm cắt như whoosh nhưng ngắn hơn; chuỗi cắt nhanh thì dùng cùng 1 mẫu swipe lặp lại để tạo nhịp đều. Đừng dùng cho chuyển cảnh chậm/trang trọng | Montage lướt 4–5 ảnh sản phẩm trong 2 giây; vuốt qua các comment/tin nhắn trên màn hình |
| 3 | **Reverse Whoosh** — whoosh ngược, tiếng "hút vào" | Như bị hút ngược vào một điểm rồi **dừng đột ngột**; cảm giác "sắp có gì đó xảy ra". Nghe thử: [Pixabay Sound Effects](https://pixabay.com/sound-effects/) (gõ "reverse whoosh") | Ngay **trước** một điểm cắt quan trọng hoặc trước khi một phần tử "sụp" vào một điểm (logo thu nhỏ, chữ biến mất vào điểm) | Anticipation: kéo sự chú ý dồn về một điểm, báo trước biến cố | Đặt **trước** sự kiện, điểm dừng của tiếng = đúng khung hình sự kiện bắt đầu. Thường dài 0,5–1 giây. Hay đi cặp: reverse whoosh → impact nhỏ | Trước khi hiện bảng giá: tiếng hút vào → bảng giá "đập" ra kèm impact |
| 4 | **Riser** — tiếng leo thang | Âm thanh cao dần/dồn dần về cao độ và độ to trong 0,5–3 giây (có loại trầm rumble, loại sáng kiểu cymbal). Nghe thử: [RISER Sound FX – YouTube](https://www.youtube.com/watch?v=Q8mYX1scq6I) | Đoạn **trước** khoảnh khắc chính: sắp công bố kết quả, giá, con số lớn, sắp mở hộp/reveal, trước câu khẳng định quan trọng nhất của video | Xây căng thẳng & chờ đợi (tension) để khoảnh khắc chính "nổ" hơn | Bắt đầu nhỏ **trước** khoảnh khắc 0,5–2 giây, leo dần và **dừng chết đúng khoảnh khắc chính** — không kéo qua. Sau riser hoặc là impact, hoặc là im lặng (tương phản mạnh nhất). Nếu có lời nói chồng lên, hạ riser xuống dưới giọng | "Và mức giá hôm nay là…" (riser leo) → im lặng nửa nhịp → đọc giá + impact |
| 5 | **Faller / Downer** — tiếng đi xuống | Ngược riser: cao độ và năng lượng tụt dần, 0,5–2 giây; cảm giác kết thúc, hạ màn, hoặc "hụt" (thất vọng nhẹ). Nghe thử: [Pixabay Sound Effects](https://pixabay.com/sound-effects/) (gõ "faller" / "downer") | Kết thúc một phần/ý, vật rơi xuống, giá **giảm**, chuyển từ cao trào về bình thường, khoảnh khắc hài "thất bại" nhẹ | Giải tỏa (release), đóng ý, đổi tông cảm xúc xuống | Đặt bắt đầu **tại** điểm cao trào và tụt dần theo hình; tránh chồng lên câu nói quan trọng ngay sau đó. Bản hài thì chọn faller hơi "tẽn" (cartoon) | Công bố "giá cũ 2 triệu" gạch bỏ → faller nhẹ → chuyển sang giá mới với pop/ding |
| 6 | **Impact / Hit** — tiếng "đập", điểm rơi | Một cú đập ngắn, gọn, có lực (0,1–0,5 giây): thud/đập khô. Nghe thử: [SFXVault – Impacts & Motion (có preview nghe ngay)](https://sfxvault.com/free_sfx/impacts-motion-free-pack/) | **Đúng khoảnh khắc** vật/chữ "rơi" xuống: tiêu đề lớn xuất hiện, punch-in (zoom đột ngột vào mặt), kết thúc một riser, cắt cứng vào câu khẳng định lớn | Dấu chấm than: khẳng định khoảnh khắc này quan trọng; neo sự chú ý | **Trúng khung hình tuyệt đối** — đỉnh tiếng = đúng frame sự kiện; lệch 1–2 frame đã thấy "lệch". Không đặt trước. Để dành cho khoảnh khắc lớn, không rải khắp video | Tiêu đề video đập vào đầu video; punch-in vào mặt đúng câu "Nghe kỹ chỗ này này!" |
| 7 | **Boom / Bass Drop / Sub** — tiếng trầm sâu, rung | Trầm, sâu, rung lồng ngực, đuôi dài 1–3 giây; "nặng" hơn impact nhiều lần. Nghe thử mẫu: [SFXVault sample (WAV)](https://cdn.sfxvault.com/2026/02/IMsample.wav) | Reveal **rất lớn**: mở đầu video hoành tráng, đổi chương lớn, công bố kết quả cuối cùng, logo lớn xuất hiện | Tạo trọng lượng và cảm giác "sự kiện lớn" | Trúng khung như impact nhưng đuôi để ngân tự nhiên; kiểm tra kỹ trên loa điện thoại (trầm sâu thường *biến mất* trên loa nhỏ — đừng để ý nghĩa của video phụ thuộc vào nó). Mỗi video ngắn chỉ nên có 0–1 lần | Mở đầu video case study doanh thu; màn hình đen → logo kênh xuất hiện kèm boom nhẹ |
| 8 | **Pop** — tiếng "bốp/bụp" nhỏ | Tiếng bong bóng bật rất ngắn (0,05–0,2 giây), vui, nhẹ, "nảy". Nghe thử & xem cách dùng: [SSW – Audio cues (có ví dụ pop khi bong bóng chat hiện)](https://www.ssw.com.au/rules/use-audio-cues-to-get-audience-attention) | Một **phần tử nhỏ xuất hiện** trên hình: chữ bật lên, icon, bong bóng chat, sticker, gạch đầu dòng, nút bấm hiện ra | Phản hồi + hút mắt về phần tử mới; giữ nhịp vui, nhanh cho video | **Trùng khung hình phần tử xuất hiện** (nếu phần tử có animation nảy, đặt đỉnh pop ở frame nó "nảy" to nhất). Rất nhỏ, dưới giọng nhiều; phần tử hiện liên tiếp thì pop theo từng cái nhưng giảm dần độ to để khỏi chói | Chữ khóa (keyword) bật lên giữa màn hình khi người nói nhắc tới; từng dòng trong danh sách "3 sai lầm" hiện kèm pop |
| 9 | **Ding / Chime / Tone** — tiếng "ting", chuông nhỏ | Tiếng chuông kim loại trong, ngân ngắn 0,3–1 giây; có họ hàng: ding đơn (một điểm sáng) và dãy nốt đi lên (danh sách hiện dần). Nghe thử: [Epidemic Sound – User Interface](https://www.epidemicsound.com/sound-effects/categories/user-interface/) | Hiện **thông tin "sáng"**: ý tưởng hay, con số kết quả, một mục trong danh sách, thông báo tốt, khoảnh khắc "à há" | Đánh dấu điểm sáng, thưởng nhẹ cho người xem, tách các mục trong liệt kê | Trùng khung hình thông tin xuất hiện; nếu là dãy mục hiện liên tiếp, dùng dãy nốt **đi lên dần** theo từng mục để tạo cảm giác tiến triển. Tránh ding khi nội dung đang nghiêm trọng/buồn (lệch tông) | Con số "−5 kg sau 2 tuần" hiện kèm ding; từng gạch đầu dòng checklist hiện kèm nốt đi lên |
| 10 | **Sparkle / Shimmer** — tiếng lấp lánh | Tiếng "tinh tinh" nhẹ, sáng, hơi ma thuật, 0,5–1,5 giây. Nghe thử: [Mixkit Free Sound Effects](https://mixkit.co/free-sound-effects/) (gõ "sparkle" / "shimmer") | Reveal **đẹp/tích cực**: ảnh after (sau khi dùng sản phẩm), giao diện đẹp hiện ra, khoảnh khắc "biến hình", quà tặng | Gắn cảm xúc "đẹp, đáng mơ ước" vào hình ảnh; phần thưởng cảm xúc | Trùng lúc hình đẹp xuất hiện, để đuôi ngân hết tự nhiên; âm lượng nhỏ — nó là lớp "phấn" chứ không phải điểm nhấn chính. Không dùng cho nội dung khô/kỹ thuật nặng | Ảnh after của khách hàng hiện ra; màn hình khoe thành quả học viên |
| 11 | **Click / Tap** — tiếng tách, bấm nút | Tiếng tách cơ học/điện tử rất ngắn (< 0,1 giây). Nghe thử: [Epidemic Sound – User Interface](https://www.epidemicsound.com/sound-effects/categories/user-interface/) | Thao tác **bấm/chọn** xuất hiện trên hình: bấm nút, tick chọn, chuyển tab, con trỏ chuột click, bật/tắt công tắc | Phản hồi hành động — làm thao tác trên màn hình "có thật" | Trùng đúng frame thao tác xảy ra. Rất nhỏ, gần như cảm nhận hơn là nghe. Chuỗi thao tác liên tiếp → click theo nhịp thao tác thật, đừng thêm/bớt | Quay màn hình hướng dẫn: click vào nút "Đăng ký" trên CapCut/app; tick từng ô trong form |
| 12 | **Notification — Success / Error** — tiếng báo đúng/sai | Hai họ đối lập: *success chime* = nốt đi lên, dễ chịu ("xong rồi!"); *error buzz* = trầm, gắt, ngắn ("sai rồi"). Nghe thử: [Epidemic Sound – User Interface](https://www.epidemicsound.com/sound-effects/categories/user-interface/) | Phần tử **thông báo** hiện trên hình: tích xanh/hoàn thành, cảnh báo, lỗi, tin nhắn đến, kết quả đúng–sai trong quiz | Báo hiệu trạng thái ngay lập tức, không cần đọc chữ người xem cũng hiểu đúng/sai | Trùng frame thông báo hiện. Cặp hình–tiếng phải nhất quán tuyệt đối (tích xanh không bao giờ đi với error buzz). Error dùng tiết chế — nghe nhiều gây khó chịu | Đoạn "đúng hay sai?" trong video dạy học; thông báo "đã lưu đơn" trong video bán hàng |
| 13 | **Typing / Keyboard** — tiếng gõ phím | Tiếng lách cách phím cơ/phím máy tính, chạy theo nhịp gõ thật. Nghe thử: [Freesound – Typewriter.wav](https://freesound.org/people/ddohler/sounds/9098/) | **Chữ đang được gõ ra** trên hình: hiệu ứng typewriter, quay màn hình gõ prompt/văn bản, chat đang soạn tin | Làm chữ "đang sống" và khớp hành động gõ; giữ mắt người xem trong lúc chữ hiện | Chạy **đồng bộ với tốc độ chữ xuất hiện** — chữ hiện nhanh thì gõ nhanh, chữ dừng thì tiếng dừng. Kết thúc câu có thể thêm ding nhỏ kiểu máy chữ cổ (khi hợp phong cách). Hạ nhỏ dưới giọng nếu có lời nói chồng lên | Gõ prompt vào Claude/ChatGPT trên màn hình quay; tiêu đề mở đầu kiểu gõ máy chữ cho video kể chuyện |
| 14 | **Camera Shutter** — tiếng màn trập "tách" | Tiếng màn trập máy ảnh: tách + cơ học, ~0,2 giây. Nghe thử: [Pixabay Sound Effects](https://pixabay.com/sound-effects/) (gõ "camera shutter") | Khoảnh khắc **"chụp lại"**: ảnh xuất hiện, đóng băng khung hình (freeze frame), chụp before/after, hiện ảnh polaroid | Báo "khoảnh khắc này được ghi lại" — hút chú ý vào tấm ảnh | Trùng frame ảnh xuất hiện/đóng băng. Thường đi kèm flash trắng 1–2 frame trên hình cho khớp. Không dùng khi không có yếu tố "ảnh" (sẽ vô nghĩa) | Đóng băng khung mặt khách hàng để chèn chú thích; hiện ảnh before/after trong video bán mỹ phẩm |
| 15 | **Cash Register / Cha-ching** — tiếng máy tính tiền "kaching" | Tiếng chuông máy tính tiền + ngăn kéo bật: "ka-ching!", vui và rất "tiền". Nghe thử: [Legis Music – Cash Register SFX](https://legismusic.com/royalty-free-music/sfx/cash-register-electric-cash-register-close-drawer-1737) | Nhắc tới **tiền vào**: doanh số, chốt đơn, giá bán, lợi nhuận, "bán được X đơn" | Gắn cảm xúc "ra tiền" vào con số; tín hiệu phần thưởng mạnh cho video bán hàng/kinh doanh | Trùng khoảnh khắc con số tiền/doanh số xuất hiện hoặc đúng từ khóa tiền trong lời nói. **Dùng rất tiết chế** (1–2 lần/video): lạm dụng sẽ thành phản cảm, khoe khoang. Tránh trong nội dung tài chính nghiêm túc/tư vấn đáng tin | "Ngày đầu tiên bán được 47 đơn" — con số hiện kèm cha-ching nhỏ; mở đầu video khoe kết quả kinh doanh |
| 16 | **Heartbeat** — tiếng tim đập | "Thình thịch" trầm, đều, tăng tốc được; 2–10 giây. Nghe thử: [Pixabay Sound Effects](https://pixabay.com/sound-effects/) (gõ "heartbeat") | Đoạn **hồi hộp chờ kết quả**: trước công bố, đếm ngược cảm xúc, tình huống nguy hiểm/lo lắng trong câu chuyện | Tăng căng thẳng sinh lý — nhịp tim người xem bị "kéo" theo | Chạy **dưới** hình/lời trong vài giây, tăng tốc dần về phía khoảnh khắc chính rồi **cắt hẳn** tại khoảnh khắc đó (cắt vào im lặng hoặc impact). Tuyệt đối không để chạy dài lê thê, không chồng lên đoạn cần nghe rõ từng chữ | Kể case "khách sắp hủy đơn thì…" với tim đập nhẹ dưới giọng; chờ kết quả xét nghiệm/giảm cân trong vlog |
| 17 | **Tick / Clock** — tiếng tích tắc đồng hồ | Tích tắc đều đặn, khô, gọn; thường đi theo nhịp 1 giây hoặc nhanh hơn. Nghe thử: [Pixabay Sound Effects](https://pixabay.com/sound-effects/) (gõ "clock tick" / "countdown") | **Đếm ngược / số đang chạy**: bộ đếm 5-4-3-2-1, số liệu đang tăng (counter), thời gian trôi, hạn chót (deadline) đang tới | Tạo nhịp và áp lực thời gian; neo mắt vào con số đang chạy | **Khóa chặt theo nhịp số đổi** — mỗi tick = một lần số nhảy. Số chạy nhanh dần thì tick nhanh dần theo. Dừng tick đúng lúc số chạm đích (thường nối bằng ding/pop) | Số follower/doanh số chạy từ 0 lên con số thật; đếm ngược 5 giây cuối khuyến mãi |
| 18 | **Glitch** — tiếng nhiễu điện tử | Tiếng nhiễu xé, méo, "vỡ sóng" rất ngắn (0,1–0,5 giây). Nghe thử: [Epidemic Sound – User Interface](https://www.epidemicsound.com/sound-effects/categories/user-interface/) (mục Glitch) | Chuyển cảnh/hình ảnh **kiểu công nghệ**: hình bị glitch, chuyển chủ đề tech, báo "lỗi/sai", sửa một thông tin vừa nói | Tín hiệu "kỹ thuật số, hiện đại" hoặc "có gì đó sai" | Trùng đúng đoạn hình bị nhiễu (hình glitch bao lâu, tiếng dài bấy nhiêu). Chỉ hợp video tông hiện đại/tech; **tuyệt đối tránh** trong video tông ấm áp, thủ công, cao cấp trầm | Chuyển cảnh trong video review AI/tool; gạch sửa một con số vừa nói sai (kèm hình nhiễu nhẹ) |
| 19 | **Paper & Foley đời thường** — tiếng giấy, đồ vật thật | Tiếng thật của đồ vật: lật giấy, xé, kéo khóa, đặt cốc, gõ bàn, tiếng bút viết… Nghe thử: [Mixkit Free Sound Effects](https://mixkit.co/free-sound-effects/) (gõ "paper" / "foley") | **Hành động thật đang diễn ra trên hình** với đồ vật thật: mở hộp, lật tài liệu, cầm sản phẩm lên, ký giấy | Tính thật (realism) — hành động có tiếng mới "sờ được"; nhóm này phải gần như vô hình | Trùng khớp hành động thật từng nhịp (lật trang nào kêu trang đó). Âm lượng rất nhỏ, ngang tiếng thật ngoài đời. Sai nhịp hoặc quá to là lộ "giả" ngay | Mở hộp sản phẩm (unboxing) trong video bán hàng; lật từng trang tài liệu khi tư vấn trực tiếp |
| 20 | **Ambience / Room Tone** — tiếng nền không gian | Lớp tiếng môi trường chạy dài, rất nhỏ: quán cà phê, văn phòng, đường phố xa, phòng yên tĩnh có "hơi thở". Nghe thử: [Pixabay Sound Effects](https://pixabay.com/sound-effects/) (gõ "ambience" / "room tone") | Dưới **B-roll hoặc đoạn chuyển bối cảnh**: cảnh quán, cảnh làm việc, mở đầu thiết lập nơi chốn; lót liền mạch dưới cả video nói trong phòng (room tone) | Xây không khí, xóa cảm giác "âm thanh bị cụt" giữa các đoạn, làm cảnh có nơi chốn | Chạy **liên tục** dưới đoạn, không ngắt quãng; fade in/out ở hai đầu. Rất nhỏ (−25 dB hoặc thấp hơn dưới giọng). Đổi bối cảnh thì đổi ambience theo và cho nghe rõ hơn 1–2 giây đầu cảnh mới để "đặt" nơi chốn | B-roll học viên làm việc tại quán cà phê; lót room tone phòng yên tĩnh dưới toàn bộ talking head để các đoạn cắt nối nhau mượt |
| 21 | **Silence (khoảng lặng có chủ đích)** — "SFX âm" | Không có tiếng gì cả — nhưng được *đặt* như một hiệu ứng. (Không có link nghe thử — vì không có gì để nghe.) | **Ngay sau hook** hoặc **ngay trước câu chốt/kết luận/punchline**; sau riser thay vì impact; khoảnh khắc cảm xúc cần ngấm | Tương phản: sau khi tai đã quen có tiếng, im lặng bắt tai phải "dỏng lên". Cho câu chốt có đất để rơi | Dài khoảng 0,3–1 giây (ngắn hơn thì không kịp nhận ra, dài hơn thì tưởng video lỗi). Đảm bảo là im lặng *sạch* cả nhạc lẫn SFX; câu chốt đi ngay sau phải thật sự xứng đáng | "…và đó là lý do tôi mất trắng 200 triệu." → lặng 0,5 giây → nói tiếp. Riser leo → cắt im lặng → hiện kết quả |
| 22 | **Logo Sting / Ident** — nhạc hiệu nhận diện ngắn | Đoạn âm thanh ký tên 1–3 giây (thường gồm whoosh nhỏ + nốt nhạc/tiếng riêng của kênh), dùng nguyên vẹn lặp lại mọi video. Nghe thử: [Mixkit Free Sound Effects](https://mixkit.co/free-sound-effects/) (gõ "logo" / "ident") | **Mở đầu và/hoặc kết thúc** video, ngay tại logo/tên kênh xuất hiện | Nhận diện thương hiệu bằng tai — người xem nghe là biết kênh nào trước cả khi nhìn | Trùng với animation của logo (tiếng đi theo chuyển động logo). Dùng **y hệt** mọi video, không đổi mẫu liên tục. Âm lượng có thể nhỉnh hơn SFX thường một chút vì nó là "chữ ký" | Logo kênh hiện cuối video kèm sting riêng; mở đầu series cố định của kênh |

**Đọc nhanh bảng trên theo "họ" tiếng** (để nhớ và để ra lệnh cho AI):
- **Họ chuyển động:** Whoosh (1), Swipe (2), Reverse Whoosh (3) — đi với hình đang chuyển động/chuyển cảnh.
- **Họ căng–thả:** Riser (4), Faller (5), Impact (6), Boom (7), Heartbeat (16), Silence (21) — điều khiển cảm xúc chờ đợi và điểm rơi.
- **Họ điểm sáng nhỏ:** Pop (8), Ding (9), Sparkle (10), Tick (17) — đi với phần tử/số liệu xuất hiện.
- **Họ phản hồi & thật:** Click (11), Notification (12), Typing (13), Shutter (14), Paper/Foley (19), Ambience (20) — khớp hành động trên hình.
- **Họ tín hiệu riêng:** Cha-ching (15) cho tiền, Glitch (18) cho tech/lỗi, Logo Sting (22) cho thương hiệu.


---

## Phần 2 — Bảng luật cho AI (copy vào skill / prompt train Claude)

> Viết dạng **SỰ KIỆN → SFX → CÁCH ĐẶT** để AI áp dụng máy móc được. Khi ra lệnh cho Claude dựng video, đính kèm bảng này và yêu cầu: *"Chèn SFX theo đúng bảng luật; sự kiện nào không có trong bảng thì không tự thêm tiếng; sau khi dựng, liệt kê lại các SFX đã chèn kèm mốc thời gian để kiểm tra."*

| # | SỰ KIỆN trong video | → SFX | → Cách đặt (vị trí · độ dài · âm lượng · lưu ý) |
|---|---|---|---|
| L1 | Chuyển cảnh có chuyển động (slide/wipe/zoom, chữ bay vào) | Whoosh nhẹ | Vắt qua điểm cắt: bắt đầu trước cắt ~2–3 frame, đỉnh trùng lúc khung đổi, đuôi kéo sang sau. Dài ≈ thời gian chuyển động. Nhỏ hơn giọng ≥ 6 dB |
| L2 | Chuỗi cắt nhanh liên tiếp (montage ảnh/clip < 1 giây/cảnh) | Swipe — cùng 1 mẫu lặp lại | Trùng từng điểm cắt để tạo nhịp đều. Không đổi mẫu giữa chuỗi |
| L3 | Sắp tới điểm công bố quan trọng (giá, kết quả, con số lớn) | Riser ngắn (0,5–2 giây) | Bắt đầu trước khoảnh khắc, leo dần, **dừng đúng khoảnh khắc**. Sau đó hoặc Impact (L4) hoặc im lặng (L15) — chọn 1, không cả hai |
| L4 | Tiêu đề lớn / câu khẳng định chính xuất hiện; punch-in vào mặt | Impact vừa | Đỉnh tiếng **đúng frame** xuất hiện. Tối đa vài lần/video — chỉ cho khoảnh khắc thật sự lớn |
| L5 | Reveal rất lớn (kết quả cuối, logo lớn, đổi chương) | Boom nhẹ (thay Impact khi cần "nặng" hơn) | Đúng frame, để đuôi ngân tự nhiên. Tối đa 1 lần/video ngắn |
| L6 | Chữ khóa / icon / bong bóng chat / gạch đầu dòng xuất hiện | Pop | Trùng frame phần tử xuất hiện. Rất nhỏ. Nhiều phần tử hiện liên tiếp → pop từng cái, giảm dần âm lượng |
| L7 | Con số kết quả / ý tưởng hay / một mục danh sách xuất hiện | Ding đơn; nếu là dãy mục → dãy nốt đi lên | Trùng frame xuất hiện. Không dùng ding khi nội dung nghiêm trọng |
| L8 | Ảnh "after" / thành quả đẹp xuất hiện | Sparkle | Trùng lúc ảnh hiện, để ngân tự nhiên, âm lượng nhỏ |
| L9 | Thao tác bấm nút / tick chọn / click chuột trên màn hình quay | Click | Đúng frame thao tác. Gần như chỉ để "cảm" thấy, không để nghe rõ |
| L10 | Thông báo hoàn thành (tích xanh) xuất hiện | Success chime | Trùng frame. Cặp hình–tiếng phải nhất quán |
| L11 | Thông báo lỗi / đáp án sai xuất hiện | Error buzz ngắn | Trùng frame. Dùng tiết chế, tối đa vài lần/video |
| L12 | Chữ đang gõ ra (typewriter / quay màn hình gõ prompt) | Typing | Đồng bộ tốc độ gõ với tốc độ chữ hiện; chữ dừng → tiếng dừng |
| L13 | Ảnh xuất hiện / đóng băng khung hình (freeze frame) | Camera shutter | Đúng frame ảnh hiện; phối hợp flash trắng 1–2 frame nếu có |
| L14 | Con số tiền / doanh số / chốt đơn xuất hiện | Cha-ching | Trùng khoảnh khắc con số hiện. **Tối đa 1–2 lần/video** |
| L15 | Ngay trước câu chốt quan trọng nhất / ngay sau hook | Silence 0,3–1 giây | Cắt sạch cả nhạc lẫn SFX trong khoảng lặng. Không dùng quá 2 lần/video |
| L16 | Đoạn chờ kết quả gây hồi hộp | Heartbeat nhẹ | Chạy dưới hình 2–6 giây, tăng tốc dần, **cắt hẳn** tại khoảnh khắc công bố |
| L17 | Số đang chạy (counter) / đếm ngược | Tick | Mỗi tick = một lần số nhảy; dừng đúng lúc số chạm đích, nối bằng Ding hoặc Pop |
| L18 | Chữ/số "sụp" vào một điểm hoặc biến mất; dẫn vào điểm cắt lớn | Reverse whoosh | Đặt trước sự kiện, điểm dừng của tiếng = frame sự kiện bắt đầu |
| L19 | Kết thúc một phần / giá cũ bị gạch bỏ / hạ tông cảm xúc | Faller nhẹ | Bắt đầu tại điểm cao, tụt dần theo hình; không chồng lên câu nói ngay sau |
| L20 | Hành động với đồ vật thật trên hình (mở hộp, lật giấy, đặt sản phẩm) | Foley tương ứng (paper/object) | Khớp từng nhịp hành động thật; âm lượng như tiếng thật ngoài đời |
| L21 | B-roll đổi bối cảnh / đoạn không có lời | Ambience của đúng bối cảnh đó | Chạy liên tục, fade hai đầu, rất nhỏ dưới giọng (≤ −25 dB tham chiếu); cho rõ hơn 1–2 giây đầu cảnh mới |
| L22 | Logo kênh xuất hiện (đầu/cuối video) | Logo sting cố định của kênh | Trùng animation logo; **dùng y hệt một mẫu cho mọi video** |
| L23 | Điểm cắt thường (cắt lời nói liên tiếp, jump cut bình thường) | **KHÔNG SFX** | Mặc định im lặng. Chỉ các sự kiện L1–L22 mới có tiếng; jump cut dọn câu nói không phải sự kiện cần tiếng |

**Luật tổng quát kèm theo (dán cùng bảng):**
1. Mỗi SFX phải trỏ được về một sự kiện L1–L22. Không sự kiện → không tiếng.
2. Âm lượng mặc định của mọi SFX: nhỏ hơn giọng nói; Impact/Boom là ngoại lệ duy nhất được nhỉnh hơn nhưng vẫn không át lời.
3. Một khoảnh khắc chỉ có **một** SFX chính (được phép lớp phụ rất nhỏ như ambience/room tone chạy nền). Không chồng pop + ding + sparkle vào cùng một phần tử.
4. Cùng một loại sự kiện lặp lại trong video → dùng **cùng một mẫu tiếng** (nhất quán = chuyên nghiệp; mỗi lần một mẫu khác nhau = rối).
5. Khi lời nói chứa thông tin bắt buộc nghe rõ từng chữ (giá, số điện thoại, hướng dẫn quan trọng): không đặt SFX có đỉnh tiếng chồng lên các âm tiết đó — xê dịch SFX ra trước/sau vài frame.

---

## Phần 3 — Lỗi thường gặp & chống lạm dụng

| # | Lỗi | Vì sao hỏng | Cách tránh |
|---|---|---|---|
| E1 | **Đóng tiếng cho mọi điểm cắt** | Bản mix thành "nhạc gõ"; người xem mệt tai và hết cảm giác điểm nhấn (theo Zella: video cắt mỗi 4–5 giây mà cắt nào cũng kêu là quá tải) | Chỉ sự kiện quan trọng mới có tiếng (bảng luật L23: mặc định không SFX) |
| E2 | **SFX quá to, át giọng** | Người xem phải căng tai nghe lời → bỏ video. Đây là lỗi bị phàn nàn nhiều nhất ở video nói chuyện | SFX nằm dưới giọng (tham chiếu −10 đến −20 dB; khoảng nửa âm lượng giọng trở xuống); nghe thử bản cuối bằng **loa điện thoại** |
| E3 | **Tiếng lệch tông/lệch năng lượng với hình** (whoosh điện ảnh nặng cho chuyển cảnh nhẹ nhàng; ding vui trong đoạn nghiêm túc) | Cảm giác "sai sai" khó gọi tên; theo Zella, lệch tông còn tệ hơn im lặng | Chọn biến thể theo năng lượng hình: nhẹ↔nhẹ, nhanh↔sắc, lớn↔nặng. Lưỡng lự thì bỏ tiếng |
| E4 | **Đỉnh SFX đè đúng âm tiết quan trọng** | Nuốt mất một chữ trong câu — người xem nghe hụt thông tin mà không hiểu sao | Xê dịch SFX vài chục ms khỏi âm tiết chính (kỹ thuật micro-shift trong dialogue mixing) |
| E5 | **Riser không dừng / kéo qua khoảnh khắc chính** | Mất toàn bộ tác dụng "chờ đợi → rơi"; nghe như tiếng nền vô nghĩa | Riser luôn kết thúc **đúng** khoảnh khắc chính, nhường chỗ cho impact hoặc im lặng |
| E6 | **Impact đặt lệch frame** (sớm/muộn 1–2 frame) | Cảm giác cẩu thả, "không khớp" dù người xem không chỉ ra được | Canh transient của impact đúng frame sự kiện; zoom timeline tới mức frame để đặt |
| E7 | **Dùng impact/boom lớn liên tục** | "Sói đến" hiệu ứng: đến khoảnh khắc quan trọng thật thì không còn gì để nhấn; người xem chai cảm xúc | Để dành tiếng lớn cho 1–3 khoảnh khắc/video; khoảnh khắc thường dùng pop/ding nhỏ |
| E8 | **Chồng nhiều SFX vào một điểm** (pop + ding + whoosh cùng lúc) | Rối, rẻ tiền, như video hiệu ứng mẫu trên app | Một khoảnh khắc = một SFX chính (luật tổng quát 3 ở Phần 2) |
| E9 | **Mỗi lần một mẫu tiếng khác nhau cho cùng sự kiện** | Mất tính hệ thống; video nghe "chắp vá" | Cố định 1 mẫu cho mỗi loại sự kiện trong cả kênh (đây cũng là cách tạo nhận diện âm thanh riêng) |
| E10 | **Ambience/nhạc nền có lời chồng dưới lời nói** | Hai luồng chữ đánh nhau trong đầu người nghe | Nhạc dưới đoạn nói phải là nhạc không lời; ambience giữ rất nhỏ và không có yếu tố "giai điệu gây chú ý" |
| E11 | **Tin vào boom/trầm sâu trên loa điện thoại** | Loa điện thoại gần như không phát được trầm sâu → hiệu ứng biến mất, chỉ còn cảm giác thiếu tiếng | Kiểm tra bản mix trên loa điện thoại; đừng để điểm nhấn chỉ dựa vào tần trầm |
| E12 | **Cha-ching và tiếng "khoe tiền" lặp lại** | Nhanh chóng thành phản cảm, giảm uy tín người bán | Tối đa 1–2 lần/video, chỉ tại con số thật sự đáng kể |

### Mật độ SFX tham khảo theo thể loại

> ⚠️ **Nói rõ:** các nguồn chuyên môn thống nhất nguyên tắc "không đóng tiếng mọi điểm cắt, để dành tiếng lớn cho khoảnh khắc lớn", nhưng **không nguồn nào công bố một con số chuẩn** kiểu "X tiếng/phút". Bảng dưới đây là **đề xuất thực hành của Muse** [đề xuất], suy từ các nguyên tắc trên + nhịp cắt thường gặp — dùng làm điểm khởi đầu để Annie hiệu chỉnh theo gu kênh của mình, không phải chuẩn ngành.

| Thể loại video | Mật độ gợi ý [đề xuất của Muse] | Ghi chú |
|---|---|---|
| Talking head chia sẻ / dạy học (YouTube, cắt mỗi 3–6 giây) | Khoảng **3–6 điểm SFX có chủ đích mỗi phút** ở đoạn có nhiều phần tử hiện (đầu video, liệt kê); đoạn nói liền mạch gần như **0** | Phần lớn là pop/ding/click nhỏ; impact lớn chỉ 1–3 lần **cả video** |
| Video ngắn bán hàng (30–60 giây) | Khoảng **5–10 điểm SFX mỗi video**: hook (impact/whoosh) + mỗi luận điểm chính 1 tiếng nhỏ + giá (riser→ding/cha-ching) + CTA (pop/click) | Nhịp nhanh hơn talking head nhưng vẫn theo sự kiện, không theo điểm cắt |
| Vlog / kể chuyện | **1–3 điểm mỗi phút**, thiên về ambience + foley + whoosh chuyển cảnh | Ưu tiên tính thật; SFX "điểm sáng" rất ít |
| Video cảm xúc / câu chuyện nặng | **0–2 điểm mỗi phút**, dùng nhiều silence và heartbeat tiết chế | Khoảng lặng là công cụ chính; ding/sparkle gần như cấm (lệch tông) |

**Bài kiểm tra cuối cùng trước khi xuất bản (cho cả người và AI):** nghe lại video một lượt với mắt nhắm. Nếu có tiếng nào làm bạn tự hỏi *"tiếng gì vậy, sao lại có?"* → tiếng đó hoặc quá to, hoặc không có sự kiện đỡ lưng → xóa hoặc giảm. SFX đạt chuẩn là SFX không ai nhận ra — cho tới khi tắt nó đi thì thấy video "thiếu thiếu".

---

## Phụ lục — Nguồn tham khảo chính

- Zella — *How to Add Whoosh and Impact Sounds to Video Cuts*: https://zellahq.com/blog/sound-design-at-cuts-whoosh-impact-riser/ (quy tắc whoosh vắt qua cắt, impact trúng frame, riser dừng chết tại điểm rơi, SFX ≈ nửa âm lượng giọng, không đóng tiếng mọi điểm cắt)
- SozAI — *The ONLY 3 Sound Effects You Need to Tell Any Story* (Tim Runia): https://sozai.app/transcript/three-sound-effects-tell-any-story/ (bộ 3 whoosh–riser–impact; tension & release; ít mà có chủ đích)
- MyTasker — *Sound Design for Video: Levels, Mixing and Techniques That Actually Matter*: https://mytasker.com/blog/the-complete-guide-to-sound-design-for-video-creators (dải dB: giọng −6…−12, SFX −10…−20, nhạc dưới lời −20…−30; −14 LUFS; silence là công cụ; literal vs emotional effects)
- PitchDrift — *15 Best Practices in Sound Design for Motion Graphics*: https://pitchdrift-productions.com/best-practices-in-sound-design-for-motion-graphics/ (tối giản, timing, dùng SFX có chủ đích)
- Sound Ideas — *Enhancing Intelligibility in Sound Mixing*: https://sound-ideas.com/blogs/sound-ideas/enhancing-intelligibility-in-sound-mixing (micro-shift tránh đỉnh tiếng nuốt âm tiết)
- FlexClip — *Cinematic Transition Sound Effects*: https://www.flexclip.com/learn/transition-sound-effects.html (đặt tiếng chuyển cảnh quanh điểm bắt đầu chuyển động 1–2 frame)
- Phân loại thư viện: Epidemic Sound (hạng mục User Interface, 250.000+ SFX) https://www.epidemicsound.com/sound-effects/categories/user-interface/ · sfx-kit CC0 (phân loại whoosh/swipe/reverse/riser/impact/boom/pop/interface/notification/tones/shimmer/logo sting) https://github.com/wyzowl/sfx-kit · Uppbeat sound kits (Pops & Dings, Logo & Idents, Creator kit) https://uppbeat.io/blog/sound-effects/best-sound-effect-packs · Hoopr — *What Sound Effects Do YouTubers Use?* https://blog.hoopr.ai/what-sound-effects-do-youtubers-use · SSW — *Use audio cues to get audience attention* https://www.ssw.com.au/rules/use-audio-cues-to-get-audience-attention (pop khi bong bóng chat hiện, chime khi hoàn thành, typing bám theo phím gõ)
- Kho nghe thử miễn phí: Pixabay https://pixabay.com/sound-effects/ · Mixkit https://mixkit.co/free-sound-effects/ · Freesound https://freesound.org/people/ddohler/sounds/9098/ (mẫu typewriter)
