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
| `intro` | sting mở đầu (`INTRO:` tự dùng): chấm → vạch → chữ rơi từng ký tự | `title`, `sub` |
| `outro` | sting kết (`OUTRO:` tự dùng): chữ trồi lên có bóng lặp, kết bằng chấm cam | `title`, `sub` |

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
