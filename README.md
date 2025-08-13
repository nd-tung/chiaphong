# Hotel Room Classification System 🏨

**Hệ thống phân loại phòng khách sạn** - Ứng dụng web Flask để xử lý file PDF khách sạn và tạo báo cáo Excel housekeeping dựa trên template có sẵn.

## Tính năng chính

### 📄 Xử lý 3 loại file PDF:
- **ARR (Arrivals)**: Danh sách phòng check-in → đánh dấu "X" vào cột ARR trong template
- **DEP (Departures)**: Danh sách phòng check-out → đánh dấu "X" vào cột DO trong template  
- **GIH (Guests in House)**: Danh sách phòng có khách ở → đánh dấu "X" vào cột OD trong template

### 🤖 Tự động hóa:
- **Trích xuất số phòng** từ file PDF bằng regex pattern recognition
- **Cập nhật template Excel** (`template.xlsx`) với các dấu X tự động
- **Chức năng nhập tay**: Cho phép thêm/xóa/chỉnh sửa danh sách phòng theo từng loại
- **Giao diện web đa ngôn ngữ** (Tiếng Việt và English)

### 📊 Xuất file kết quả:
- **File Excel (.xlsx)**: Dựa trên template có sẵn, đã đánh dấu X
- **File ảnh (.png)**: Convert từ Excel để dễ dàng chia sẻ và in
- **Thống kê tổng quan**: Số lượng phòng theo từng loại ARR/DEP/OD

## Cài đặt

### 1. Cài đặt Python packages

```bash
pip3 install -r requirements.txt
```

### 2. Cấu trúc thư mục

Đảm bảo có các file sau trong thư mục:
- `template.xlsx` - File Excel template
- Các file PDF mẫu (không bắt buộc, chỉ để test)

## Sử dụng

### 1. Chạy web application

```bash
python3 web_server.py
```

### 2. Mở trình duyệt

Truy cập: **http://localhost:8000** (đã thay đổi từ port 5000 → 8000)

### 3. Upload 3 file PDF

- **File ARR**: Chọn file PDF chứa danh sách arrivals
- **File DEP**: Chọn file PDF chứa danh sách departures  
- **File GIH**: Chọn file PDF chứa danh sách guests in house

### 4. Chọn định dạng xuất

- **Excel (.xlsx)**: File Excel chuẩn có thể chỉnh sửa tiếp
- **Hình ảnh (.png)**: File ảnh để in hoặc chia sẻ dễ dàng

### 5. Tạo báo cáo

Nhấn nút "Tạo Báo Cáo" và tải file kết quả theo định dạng đã chọn.

## Test

Để test với file mẫu:

```bash
python3 test_simple.py
```

## Cấu trúc file hiện tại

```
chialich/
├── web_server.py          # Flask web server chính (port 8000)
├── template.xlsx          # Excel template (133 phòng có sẵn)
├── templates/
│   └── upload.html       # Giao diện web upload file
├── uploads/               # Thư mục chứa file upload (tự động tạo)
├── downloads/             # Thư mục chứa file kết quả (tự động tạo)
├── requirements.txt       # Python dependencies
├── README.md             # Hướng dẫn này
└── Các file PDF mẫu       # File test (tuỳ chọn)

📋 Các file được tạo tự động:
• room_classification_DDMMYY.xlsx  # File Excel kết quả
• room_classification_DDMMYY.png   # File ảnh kết quả
```

## Yêu cầu hệ thống

- Python 3.7+
- Flask 2.3.3
- pdfplumber 0.9.0
- openpyxl 3.1.2
- PyPDF2 3.0.1
- Pillow 10.0.1 (cho xuất ảnh)

## ⚠️ QUAN TRỌNG - Sử dụng Template

**Hệ thống sử dụng template Excel có sẵn (`template.xlsx`) để đánh dấu X:**

- Template có cấu trúc: `HOUSEKEEPING DEPARTMENT` với 133 phòng đã được định sẵn
- Header gồm: `Room | OD | DO | ARR | NOTE` (lặp lại nhiều cột)
- **ARR rooms** → Đánh dấu "X" vào cột **ARR**
- **DEP rooms** → Đánh dấu "X" vào cột **DO** (Departures)
- **GIH rooms** → Đánh dấu "X" vào cột **OD** (Occupied Dirty)
- Ngày sẽ được cập nhật tự động dựa trên "Schedule Date" được nhập

## Cách hoạt động

1. **Trích xuất số phòng**: Sử dụng `pdftotext` + regex pattern để tìm số phòng từ PDF
2. **Lọc dữ liệu**: Loại bỏ các số không hợp lệ (ngày tháng, mã booking, etc.)
3. **Load template Excel**: Mở file `template.xlsx` có sẵn thay vì tạo mới
4. **Mapping phòng**: Tìm vị trí của từng số phòng trong template
5. **Đánh dấu X**: Thêm "X" vào các cột tương ứng (ARR/DO/OD) đúng vị trí phòng
6. **Cập nhật ngày**: Thay đổi ngày trong template theo "Schedule Date" được nhập
7. **Export**: Lưu file Excel đã cập nhật và convert thành PNG

## Lưu ý

- File PDF phải có format chuẩn từ hệ thống PMS khách sạn
- Template Excel không được thay đổi cấu trúc headers
- Số phòng hợp lệ: 3-4 chữ số (100-9999), loại trừ vùng ngày tháng (2500-2600)
- Web app chạy ở chế độ debug, không nên dùng trong production

## Liên hệ

Nếu có vấn đề hoặc cần hỗ trợ, vui lòng tạo issue trong repository.
