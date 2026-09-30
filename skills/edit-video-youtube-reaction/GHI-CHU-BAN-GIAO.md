# reactforge — bàn giao để tối ưu

Bản ngày 28/09/2026. Công cụ dựng video react/phân tích: đầu vào là kịch bản markdown +
file quay đọc kịch bản + link video gốc, đầu ra là `out/final.mp4` 1080p đã cắt vấp,
có chữ nhảy theo từng từ, đồ hoạ động và phụ đề Việt cho clip gốc.

## Cấu trúc

```
SKILL.md              hướng dẫn dùng (đây là file Claude đọc khi chạy /reactforge)
install.sh            cài một lần
pipeline/             phần Python — toàn bộ logic dựng
  reactforge/         14 module, ~2.600 dòng
  scripts/            tiện ích chạy tay (make_screens, verify_rebuild, tg_send…)
  assets/fonts/       font Be Vietnam Pro
motion/               phần Remotion (TypeScript) — đồ hoạ động góc dưới trái
examples/             kịch bản mẫu + project.json mẫu
```

Các bước chạy nối nhau: `plan → source → subs → align → captions → panel → cards →
graphics → render → verify`. Mỗi bước là một module cùng tên trong `pipeline/reactforge/`.

## Mới so với bản 13/09

Hai file đã đổi, đều rút ra từ một lần dựng thật (video 18 phút, quay 30 phút):

- `scripts/make_screens.py` — thêm nhánh b-roll: `[MÀN HÌNH: 1:52–2:18]` giờ cho **chạy**
  đúng khúc đó của video gốc ở khung trái, thay vì chiếu ảnh tĩnh. Kèm quy tắc: đoạn nào
  đã có ảnh riêng trong `assets/<id>/` thì không trộn thêm khung từ video gốc nữa.
- `reactforge/doctor.py` — thêm cờ `source.burned_captions` cho nguồn đã cháy sẵn phụ đề.

## Những chỗ đáng tối ưu

Xếp theo mức khó chịu khi dùng thật, không theo độ khó sửa.

**1. Tư liệu gốc chỉ được hiện ở khung nhỏ.** Đây là phàn nàn đầu tiên của người dùng.
Hiện có đúng ba bố cục: đoạn nói thì chia đôi (mặt phải, tư liệu trái 900×506 và bị giảm
sáng còn 58%), clip gốc thì full khung, thẻ chữ thì full khung. Không có chế độ "tư liệu
full khung + tiếng vẫn là lời người dẫn + mặt thu nhỏ góc". Kịch bản nào cũng có vài đoạn
tư liệu mạnh xứng đáng chiếm trọn khung. Xem `render.py:render_talk` và `render_clip` —
hai hàm này đã có sẵn mọi mảnh ghép cần thiết, thiếu đường nối giữa chúng.

**2. `render --only tXX` không nối lại bản cuối.** `render.py` return sớm khi có `only`,
nên sửa một đoạn 60 giây xong vẫn phải render lại toàn bộ 35 đoạn (~8 phút) chỉ để có
file cuối. Nên tách hàm nối ra thành lệnh riêng, hoặc cho `--only` tự nối lại từ các
`work/seg/*.mov` sẵn có.

**3. `make_screens.py` encode lại mọi thứ bằng libx264.** 18 đoạn mất ~15 phút, phần lớn
là encode ảnh tĩnh thành clip rồi nối. Đây là bước phải chạy lại mỗi lần đổi tư liệu, nên
nó nằm thẳng trên đường găng. Có thể dùng `-c copy` khi nối, hoặc bỏ qua bước trung gian.

**4. Dịch phụ đề chết nếu nguồn không có sẵn file `.vtt`.** `subs.py` bắt buộc phải có
`source/captions*.vtt` do yt-dlp tải về. Với nguồn không kèm phụ đề (Facebook Reel chẳng
hạn) thì phải tự chạy whisper bên ngoài rồi ghi file `.vtt` giả vào đúng chỗ. Nên đưa
bước đó vào hẳn `source.py`.

**5. Số token báo về không thật khi chạy qua CLI.** `judge.py:77` — khi không có API key
và rơi về `claude -p`, usage được ước lượng bằng `len(text) // 4`, bỏ qua system prompt và
phần Claude Code tự thêm. Không dùng con số này để tính chi phí.

**6. `doctor` chỉ kiểm file có tồn tại, không kiểm nội dung có đúng không.** Nó bắt được
"thiếu ảnh khung trái", "lệch hình/tiếng", nhưng không bắt được "clip này cắt nhầm đoạn,
người trong clip đang nói chuyện khác". Lần dựng vừa rồi có một clip cắt trúng chỗ không
chứa câu mà kịch bản mô tả — chỉ phát hiện ra khi đọc phụ đề đã dịch. Đã có sẵn
`work/subs/*.json` chứa lời tiếng Việt của từng clip; đối chiếu nó với mô tả trong kịch
bản là một phép kiểm rẻ và bắt được đúng loại lỗi này.

**7. Bước `align` chạy 1 giờ 45 phút** cho bản quay 30 phút (whisper medium, CPU, kèm vòng
nghe lại các vùng bị nuốt chữ). Đây là bước lâu nhất. Đáng thử `faster-whisper` với
`device="auto"` để dùng GPU trên máy Apple Silicon, hoặc chia nhỏ chạy song song.

## Hai quy tắc đừng phá

- **`doctor` phải giữ quyền chặn render.** Pipeline này từng hỏng êm: thiếu dữ liệu thì
  in một dòng log rồi dựng tiếp, và ba phút đầu của một video 32 phút đã ra ngoài với
  khung trái đứng im. `render` gọi `doctor` tự động và thoát mã 1 nếu thiếu — đừng bỏ.
- **`verify` phải nghe lại chính file đã dựng, không phải file nguồn.** Vòng này bắt được
  những chỗ cắt chưa sạch ở mối nối mà vòng đầu bỏ sót. Lần dựng vừa rồi nó chạy 3 vòng,
  cắt thêm 9 chỗ rồi mới hội tụ.

## Chạy thử

```bash
./install.sh
PY=~/reactforge/.venv/bin/python
$PY -m reactforge all    projects/<dự-án>
$PY -m reactforge doctor projects/<dự-án>   # luôn chạy cái này trước khi giao
```

Cần `ffmpeg`, `yt-dlp`, `node`, `faster-whisper`, `playwright`. Khoá Claude đặt trong
`<dự-án>/.env` hoặc `~/.env`; không có khoá thì tự rơi về `claude -p`.
