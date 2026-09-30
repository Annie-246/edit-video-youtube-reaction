# TIÊU CHUẨN MOTION GRAPHIC REACTFORGE (REMOTION)

Tài liệu hướng dẫn dựng đồ hoạ động Remotion (React) với 3 hình thức hiển thị linh hoạt và khả năng tùy biến đa dạng theo nội dung kịch bản.

---

## 1. 3 Hình thức xuất hiện (Layouts)

Video reactforge hỗ trợ 3 hình thức xuất hiện đồ hoạ động để video luôn sinh động và biến hoá:

| Hình thức | Cú pháp | Kích thước | Mô tả & Khi nào dùng |
|---|---|---|---|
| **1. Góc nhỏ phía dưới trái** | `GFX: <mẫu> {json}` | 900 × 478 px | Nửa trên chạy b-roll/ảnh, người nói ở bên phải. Dùng cho thẻ ngắn, con số nổi bật, trích dẫn ngắn. |
| **2. 1/2 Màn hình bên cạnh người nói** | `SIDE: <mẫu> {json}` | 900 × 1016 px | Chiếm trọn nửa bên trái màn hình cạnh người nói. Rất thoáng, trực quan cho quy trình (bước 1-2-3), timeline, bảng so sánh 2 cột, danh sách điểm nhấn, ảnh minh họa chất lượng cao. |
| **3. Full toàn màn hình** | `FULL: @"câu" {json}` | 1920 × 1080 px | Chiếm trọn màn hình 3–5s. Dùng cho câu hỏi lớn, cú lật luận điểm, chương mới, biểu đồ trọng điểm. |

> Cú pháp neo câu nói: Thêm `@"câu neo"` trước tên mẫu (ví dụ `SIDE: @"quy trình tự động" steps {...}`) để đồ hoạ xuất hiện đúng thời khắc người nói nhắc tới từ đó!

---

## 2. Tiêu chuẩn phong cách thị giác (Style Benchmarks)

4 video mẫu chuẩn tại `motion/templates/samples/` đóng vai trò định hình ngôn ngữ thiết kế:
- **Màu sắc neon & viền phát sáng:** Tự động đồng bộ theo `style.accent` trong `project.json` (màu tím neon `#8B7CFF` hoặc xanh dương neon `#38BDF8`).
- **Nền Dark Mode Glassmorphism:** Tone nền tối `#0B0B10` phối hợp lưới 3D chuyển động (`GridFloor`) và bụi sáng trôi chậm (`Particles`).
- **Chuyển động liên tục:** Sử dụng hàm số Remotion `useCurrentFrame()`, lò xo `spring()` và đung đưa nhẹ `useDrift()`, không bao giờ để khung hình đứng im chết chóc.
- **Typography tiếng Việt:** Font chuẩn Be Vietnam Pro sắc nét, phân cấp rõ ràng (Kicker -> Headline -> Số liệu -> Diễn giải).

---

## 3. Các mẫu đồ hoạ có sẵn & Cú pháp khai báo

### Mẫu 1: Cột tăng trưởng phát sáng (`bars`)
- **Góc nhỏ:**
  ```text
  GFX: @"tăng trưởng vượt bậc" bars {"kicker":"KẾT QUẢ","headline":"Doanh thu tăng gấp 6 lần","bars":[25, 40, 65, 90, 130, 180]}
  ```
- **1/2 Màn hình:**
  ```text
  SIDE: @"tăng trưởng vượt bậc" bars {"kicker":"KẾT QUẢ","headline":"Tăng trưởng liên tục qua các quý","bars":[30, 55, 80, 110, 150, 210]}
  ```
- **Toàn màn hình:**
  ```text
  FULL: @"doanh thu bùng nổ" {"secs":3.5,"style":"bars","kicker":"TĂNG TRƯỞNG","title":"Doanh thu vượt mốc 10 tỷ"}
  ```

---

### Mẫu 2: Hai đường xu hướng đối chiếu (`trend`)
- **Góc nhỏ:**
  ```text
  GFX: @"khoảng cách ngày càng xa" trend {"kicker":"SO SÁNH","headline":"Hiệu suất vượt trội","label1":"Có ứng dụng AI","label2":"Cách làm truyền thống"}
  ```
- **1/2 Màn hình:**
  ```text
  SIDE: @"khoảng cách ngày càng xa" trend {"kicker":"ĐỐI CHIẾU XU HƯỚNG","headline":"Tốc độ bứt phá","label1":"Mô hình mới","label2":"Truyền thống"}
  ```
- **Toàn màn hình:**
  ```text
  FULL: @"bứt phá ngoạn mục" {"secs":4.0,"style":"trend","kicker":"ĐỐI CHIẾU HIỆU SUẤT","title":"Tốc độ xử lý của AI bỏ xa thủ công"}
  ```

---

### Mẫu 3: Dashboard & Luồng quyết định AI (`system_flow`)
- **Góc nhỏ:**
  ```text
  GFX: @"hệ thống tự động" system_flow {"kicker":"QUY TRÌNH","headline":"Tự động thẩm định dữ liệu"}
  ```
- **1/2 Màn hình:**
  ```text
  SIDE: @"luồng xử lý" system_flow {"kicker":"KIẾN TRÚC HỆ THỐNG","headline":"Quy trình pipeline tự động"}
  ```
- **Toàn màn hình:**
  ```text
  FULL: @"kiểm duyệt tự động" {"secs":4.0,"style":"system_flow","kicker":"HỆ THỐNG AI","title":"Quy trình kiểm duyệt tự động không cần người"}
  ```

---

### Mẫu 4: Chu kỳ 24/7 & Tác vụ xoay quanh (`clock_cycle`)
- **Góc nhỏ:**
  ```text
  GFX: @"chạy xuyên đêm" clock_cycle {"kicker":"TỰ ĐỘNG HÓA","headline":"Vận hành liên tục 24/7"}
  ```
- **1/2 Màn hình:**
  ```text
  SIDE: @"vận hành 24/7" clock_cycle {"kicker":"VẬN HÀNH XUYÊN SUỐT","headline":"Tự động giải phóng 100% sức người"}
  ```
- **Toàn màn hình:**
  ```text
  FULL: @"tiết kiệm toàn bộ thời gian" {"secs":3.8,"style":"clock_cycle","kicker":"TỐI ƯU THỜI GIAN","title":"Hệ thống tự chạy 24/7 không cần can thiệp"}
  ```

---

### Mẫu 5: Quy trình bước dọc (`steps`) — Tối ưu cho 1/2 Màn hình
Dành riêng cho nửa màn hình bên cạnh người nói, diễn giải tiến trình rõ ràng:
```text
SIDE: @"bốn bước cốt lõi" steps {"kicker":"QUY TRÌNH","headline":"4 Bước Thực Hiện","steps":[{"title":"Bước 1: Bóc băng tự động","desc":"Whisper AI chuyển âm thanh thành lời","tag":"AI"},{"title":"Bước 2: Cắt gọt ý cuối","desc":"Loại bỏ triệt để đoạn vấp lặp","tag":"Claude"},{"title":"Bước 3: Motion Graphic","desc":"Cứ mỗi 10s có 1 visual mới","tag":"React"},{"title":"Bước 4: Xuất bản 4K","desc":"Chuẩn âm thanh -16 LUFS mượt mà","tag":"FFmpeg"}]}
```

---

### Mẫu 6: Bảng so sánh 2 chiều (`compare`)
```text
SIDE: @"so sánh trực quan" compare {"kicker":"ĐỐI ĐẦU","leftTitle":"Thủ công","leftItems":["Mất 4-6 giờ dựng","Dễ sót lỗi nhại lời","Tốn nhiều chi phí"],"rightTitle":"Antigravity AI","rightItems":["Xử lý tự động trong tích tắc","Giữ ý cuối hoàn chỉnh nhất","Motion graphic render bằng code"]}
```

---

### Mẫu 7: Hình ảnh minh hoạ Gemini / B-roll (`image`)
Dùng khi người dùng note yêu cầu sinh ảnh minh hoạ bằng Gemini API hoặc chèn ảnh visual đặc biệt:
```text
SIDE: @"hình ảnh trực quan" image {"kicker":"MINH HOẠ","headline":"Mô Phỏng Trực Quan","src":"https://...","caption":"Giao diện điều khiển tự động hoá thời gian thực","tags":["Gemini AI","Trực quan 4K"]}
```

---

### Mẫu 8: Con số lớn & Điểm nhấn (`bignumber`, `list`, `card`)
- `bignumber`: Con số đếm tăng dần (`useCountUp`) kèm danh sách insight phụ.
- `list`: Danh sách các ý chính có tick xanh neon.
- `card`: Khối thông tin mở màn hoặc trích dẫn tiêu đề lớn.

---

## 4. Tự do Sáng tạo Mẫu Mới (Dynamic Code Generation)

**Quy tắc:** 4 mẫu trên chỉ là phong cách mẫu. AI được toàn quyền và chủ động viết thêm bất kỳ component React/Remotion mới nào phù hợp với câu chuyện của kịch bản:
- Biểu đồ phễu (funnel), biểu đồ tròn (donut), biểu đồ nhị phân.
- Sơ đồ tư duy (mindmap), mạng lưới nơ-ron kết nối các điểm.
- Giao diện dòng lệnh Terminal với chữ gõ từng ký tự.
- Giao diện giả lập điện thoại di động (mobile app preview).
- Thẻ thông tin khách hàng, thẻ hồ sơ (profile card).

