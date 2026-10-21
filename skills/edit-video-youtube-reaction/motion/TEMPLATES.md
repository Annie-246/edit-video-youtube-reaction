# Mẫu đồ hoạ (bộ sáng, màu cam trơn)

Một composition duy nhất `Main` (`src/light/`). Mỗi cảnh vẽ trên artboard rộng 1180 rồi co
theo khung: khung chính 1440x920 cạnh người nói, hoặc thẻ full 1920x1080.

- **Màu:** nhấn bằng cam trơn `#D97757`, chữ `#141413`. Nền cảnh là gradient be – cam nhạt.
  Không dùng gradient nhiều màu. Ngoại lệ duy nhất: bộ showreel bên dưới (gradient cùng tông cam đất).
- **Nền đen:** chỉ dùng cho vài cảnh cần nhấn (`"dark": true`). Mặc định thẻ FULL dạng
  `title`, `quote`, `equation` và mọi `BEAT:` có nền đen; `BREAK:` dùng mẫu `chapter`.
- **Font:** Inter. Viết hoa đầu câu, không viết hoa toàn bộ. Line-height từ 1.24 trở lên.
- **Chuyển động:** chữ hiện dần từng từ (bỏ mờ, trồi lên), thẻ trồi lên lần lượt, con trỏ tay bấm,
  chữ gõ từng ký tự, số đếm lên. Hai video mẫu nằm ở `templates/samples/`.
- **Nhấn từ khoá:** bọc từ khoá trong `*…*` ở `title`, ví dụ `"Đừng gửi *email lạnh* nữa"`.
  Dấu câu ngay sau dấu sao vẫn được: `"Bán *gói định kỳ*, đừng bán lẻ"`.

## Cách gọi trong kịch bản

```text
SIDE: @"câu neo" <mẫu> {json}                  ← cảnh trong khung chính, chạy tới cảnh sau
FULL: @"câu neo" {"secs":4,"tpl":"<mẫu>", …}   ← thẻ chiếm trọn màn hình vài giây
BEAT: @"câu neo" {"title":"…"}                  ← thẻ chốt nền đen
```

## Danh mục

| Mẫu | Dùng khi | Props chính |
|---|---|---|
| `broll` | chiếu đúng khúc video gốc (bản ghi màn hình) | `at` (giây trong video gốc), `caption` |
| `photo` | ảnh minh hoạ / chuỗi ảnh, push-in chậm | `images:[…]` hoặc `src`, `caption`, `kicker` |
| `person` | nhân vật được nhắc lần đầu | `src`, `name`, `role`, `tags:[…]` |
| `title` | câu chốt, câu hỏi lớn | `kicker`, `title` (có `*nhấn*`), `sub` |
| `tool` | mở đầu một công cụ / chương | `num`, `name`, `icon`, `desc`, `tag` ("A · B") |
| `flow` | luồng A → B → C (2–4 nút) | `kicker`, `title`, `nodes:[{icon,label,sub}]` |
| `steps` | các bước 1-2-3 (trên 4 bước thì xếp dọc) | `kicker`, `title`, `steps:[{title,sub}]` |
| `compare` | cách cũ và cách mới | `kicker`, `title`, `left:{title,items}`, `right:{title,items}` |
| `checklist` | danh sách trên thẻ nghiêng 3D | `kicker`, `title`, `items:[{label,value}]`, `side` |
| `bignumber` | một con số, có đếm lên | `kicker`, `prefix`, `value`, `suffix`, `label`, `sub` |
| `equation` | phép tính a × b = kết quả | `kicker`, `a`, `op`, `b`, `result`, `note` |
| `bars` | cột so sánh (cột cuối được nhấn) | `kicker`, `title`, `bars:[{label,value,display}]` |
| `chat` | tin nhắn mẫu, hỏi đáp với AI | `kicker`, `messages:[{from:"me"/"them",text,icon}]` |
| `search` | ô tìm kiếm gõ chữ và kết quả | `kicker`, `query`, `platforms:[…]`, `results:[{src,text,icon}]` |
| `quote` | câu trích, gõ từng chữ | `kicker`, `text`, `author` |
| `filter` | N mục lọc còn M | `kicker`, `title`, `total`, `keep:[tên…]` |
| `questions` | ý tưởng bị chất vấn | `kicker`, `idea`, `questions:[…]` |
| `formats` | khung dọc / ngang / vuông | `kicker`, `title`, `items:[{ratio:"9:16",label}]` |
| `commands` | lệnh / phím tắt | `kicker`, `title`, `commands:[{cmd,desc,icon}]` |
| `form` | công cụ cho xem kết quả trước, xin thông tin sau | `kicker`, `title`, `rows:[{label,value}]`, `result`, `cta` |
| `recap` | điểm lại nhiều mục, sáng lần lượt | `kicker`, `title`, `items:[{icon,name,desc}]` |

**Bộ showreel / kiểu Greg (nền tối ấm, tự vẽ nền, dùng hạn chế):**

| Mẫu | Dùng khi | Props chính |
|---|---|---|
| `horizon` | một câu chốt trên vành hành tinh phát sáng cam | `kicker`, `title` (có `*nhấn*`) |
| `agenda` | mục lục / danh sách hiện từng dòng (dòng mới xám rồi sáng) | `title`, `items:["…"]` |
| `chapter` | màn chuyển phần (`BREAK:` tự dùng): số lớn bay vào, xuyên qua khi thoát | `num`, `kicker`, `title` |
| `outro` | sting kết (`OUTRO:` tự dùng): chữ trồi lên có bóng lặp, kết bằng chấm cam | `title`, `sub` |

**Ảnh thật và logo** (bước `visuals` tự chèn; khai tay bằng `SIDE:` cũng được):

| Mẫu | Dùng khi | Props chính |
|---|---|---|
| `logo` | nhắc tên một thương hiệu / app: ô trắng viền cam gradient bật ra, tên hiện bên cạnh | `src`, `name`, `desc` |
| `logos` | nhiều thương hiệu nhắc liền nhau: các ô logo bật lần lượt thành hàng | `items:[{src,name}]`, `title`, `kicker` |
| `stack` | ảnh thật bay vào từ hai bên, chồng thành xấp như ảnh in | `images:[…]` (≤ 5), `caption`, `kicker` |
| `wall` | tường ảnh 3D nghiêng, các cột cuộn ngược chiều nhau (sáng / tối xen kẽ) | `images:[…]` (lặp nếu ít), `title`, `caption` |

**Bộ studio** (học từ reel agency: swipe ảnh, dải màu, thẻ nổi, chữ khổng lồ, giao diện 3D), vẽ lại bằng bộ màu cam đất. Dùng được ở `SIDE:` và `FULL:`:

- **Mỗi mẫu có 2 bản sáng (nền kem) và tối (nền than ấm).** Không khai gì thì các cảnh studio
  và `wall` **tự xen kẽ** sáng → tối → sáng theo thứ tự xuất hiện (trong `Main`), nên hai cảnh liền
  nhau không cùng nền. Muốn cố định thì thêm `"dark": true` / `"dark": false` vào cảnh đó.
- Ảnh trong `float` để **thẳng, góc vuông**, không bo, không viền sáng; chỉ có bóng đổ mềm.

| Mẫu | Dùng khi | Props chính |
|---|---|---|
| `swipe` | nhiều ảnh / màn hình app: các hàng ảnh dọc trượt ngang ngược chiều, ảnh nào lướt qua điểm nhấn thì phồng to | `images:[…]` (≥ 6), `kicker`, `rows` (2–4) |
| `strips` | một công cụ làm nhiều việc: dải màu dọc trồi lên xếp quạt, mỗi dải một nhãn + ảnh | `title`, `items:[{label,src}]` (≤ 9) |
| `float` | khoe nhiều sản phẩm / dự án: ảnh thẳng góc vuông trôi lơ lửng, câu chính gõ trong khung chọn nét đứt | `images:[…]`, `title`, `kicker` |
| `bigtype` | một câu cực ngắn cần đập vào mắt: chữ khổng lồ trên nền cam, hai dòng chữ mờ chạy ngược chiều | `text` (≤ 20 ký tự), `echo` (chữ nền) |
| `pills` | 2–6 bước / tính năng ngắn: nút viên thuốc nền than rơi vào lần lượt, nút cuối màu cam | `title`, `items:[{icon,label}]` |
| `orbit` | một nền tảng kết nối nhiều người / công cụ: tâm phát sáng, avatar quay trên 3 quỹ đạo | `center` (ảnh logo) hoặc `icon`, `items:[{src|icon}]`, `title` |
| `typebar` | prompt / câu tìm kiếm trên ảnh: thanh trắng gõ chữ trên ảnh lớn | `src`, `text`, `kicker` |
| `ui3d` | demo một phần mềm: giao diện nghiêng 3D dựng dần, bảng trợ lý trượt vào, máy quay lao vào nút, con trỏ bấm | `app`, `title`, `rows:[{label,value,pct}]`, `panel:{title,items}`, `cta` |

Hai mẫu `horizon`, `agenda` dùng được ở cả `SIDE:` (nhất là đoạn `MOTION:`) và `FULL:`.
Đây là chỗ duy nhất được dùng gradient cam đất (`#F0B49A → #D97757 → #B5532F`) và quầng sáng.

Mẫu nào cũng nhận thêm `"dark": true` để dùng nền đen.

**Icon** (dùng cho `icon`): link video play doc slides bot search chat mail gift money chart
globe mic calendar user users check x sparkle store question shield layout phone clock
sheet rocket repeat wand box calc sofa drop target flame code heart bell thumb arrow palette
translate community

## Tự code mẫu mới

Viết component vào `src/custom/<Ten>.tsx` (trong thư mục dữ liệu của plugin, không bị ghi đè
khi cập nhật), dùng `../light/kit` (`Stage`, `Card`, `Words`, `GradText`, `Pill`, `Kicker`,
`Typed`, `Cursor`, `useIn`, `L`) và `../light/icons` (`Icon`, `IconTile`). Đăng ký tên trong
`src/custom/index.ts`. Mẫu tự code trùng tên sẽ đè lên mẫu có sẵn.

Xem thử một khung trước khi dựng cả bài:

```bash
cd <data>/motion && npx remotion still Main out.png --props=props.json --frame=60
```
