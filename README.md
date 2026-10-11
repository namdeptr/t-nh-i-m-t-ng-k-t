# Quản lý điểm sinh viên bằng Streamlit

## 1. Cài đặt
Cài Python 3.10 trở lên. Mở terminal trong thư mục dự án và chạy:

```bash
python -m pip install -r requirements.txt
```

## 2. Chạy ứng dụng
```bash
streamlit run app.py
```

Streamlit sẽ mở ứng dụng trong trình duyệt. Nếu không tự mở, truy cập địa chỉ local mà terminal hiển thị (thường là http://localhost:8501).

## 3. Chức năng
- Dữ liệu mẫu 10 sinh viên.
- Chỉnh sửa và thêm dòng trực tiếp trên bảng.
- Nhập CSV với các cột: `Mã sinh viên`, `Họ tên`, `Chuyên cần`, `Giữa kỳ`, `Cuối kỳ`.
- Tùy chỉnh trọng số; mặc định 10% - 30% - 60%.
- Tính điểm tổng kết, xếp loại, thống kê mô tả.
- Tìm kiếm, lọc theo xếp loại, xuất CSV.
- Biểu đồ phân bố xếp loại và điểm từng sinh viên.

## 4. Công thức
Điểm tổng kết = Chuyên cần × 10% + Giữa kỳ × 30% + Cuối kỳ × 60%.

Xếp loại minh họa:
- Xuất sắc: từ 9,0
- Giỏi: từ 8,0 đến dưới 9,0
- Khá: từ 6,5 đến dưới 8,0
- Trung bình: từ 5,0 đến dưới 6,5
- Yếu: dưới 5,0

Bạn có thể thay đổi các ngưỡng trong hàm `classify()` của `app.py`.
