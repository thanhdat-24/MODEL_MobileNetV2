# Ứng dụng nhận diện hoa quả thông minh

Ứng dụng web sử dụng MobileNetV2 để nhận diện các loại hoa quả và tạo công thức món ăn.

## Tính năng chính

1. **Nhận diện hoa quả đơn lẻ**: Tải lên và nhận diện một hình ảnh hoa quả.
2. **Nhận diện nhiều hoa quả**: Tải lên nhiều hình ảnh và phân loại thành các nhóm hoa quả.
3. **Lưu lịch sử nhận diện**: Xem lại các kết quả nhận diện trước đây.
4. **Đánh giá kết quả**: Đánh giá mức độ chính xác của kết quả bằng hệ thống sao.
5. **Công thức món ăn**: Xem các công thức món ăn dựa trên loại hoa quả đã nhận diện.
6. **Công thức do AI tạo**: Tạo công thức món ăn độc đáo với OpenAI API.

## Cài đặt

### Yêu cầu

- Python 3.7+
- TensorFlow 2.x
- Flask
- OpenAI API key (cho tính năng tạo công thức bằng AI)

### Các bước cài đặt

1. Clone repository
```
git clone <repository-url>
cd <repository-folder>
```

2. Cài đặt các thư viện cần thiết
```
pip install -r requirements.txt
```

3. Cấu hình API keys

Mở file `src/config.py` và cập nhật API key OpenAI của bạn:
```python
# Cấu hình OpenAI API
OPENAI_API_KEY = "your_openai_api_key"  # Thay thế bằng API key của bạn
OPENAI_MODEL = "gpt-3.5-turbo"  # hoặc "gpt-4" nếu có quyền truy cập
```

4. Chạy ứng dụng
```
python src/app.py
```

Ứng dụng sẽ chạy trên địa chỉ http://localhost:5000

## Hướng dẫn sử dụng tính năng tạo công thức với OpenAI

1. Đăng nhập vào hệ thống.
2. Chọn tính năng nhận diện hoa quả (đơn lẻ hoặc nhiều ảnh).
3. Sau khi nhận diện, vào trang "Lịch sử" để xem kết quả nhận diện.
4. Với mỗi kết quả nhận diện, nhấn nút "Xem công thức" để hiển thị các công thức món ăn.
5. Bật chế độ "Công thức do AI tạo" để tạo công thức độc đáo sử dụng OpenAI GPT.
6. Xem chi tiết công thức bằng cách nhấn nút "Xem chi tiết".

## Cấu trúc dữ liệu công thức

Mỗi công thức được tạo bởi OpenAI có cấu trúc như sau:

```json
{
  "id": 1,
  "ten_mon": "Tên món ăn bằng tiếng Việt",
  "nguyen_lieu": ["Nguyên liệu 1", "Nguyên liệu 2", "..."],
  "cach_lam": "1. Bước thứ nhất\n2. Bước thứ hai\n...",
  "loai_hoa_qua": "Tên loại hoa quả",
  "thoi_gian_nau": 30,
  "do_kho": "Dễ/Trung bình/Khó",
  "luot_thich": 0
}
```

## Lưu ý

- Tính năng tạo công thức bằng AI yêu cầu OpenAI API key hợp lệ trong file config.
- Nếu OpenAI API không khả dụng, hệ thống sẽ trở về chế độ tạo công thức mẫu.
- Các công thức do AI tạo ra sẽ được lưu vào cơ sở dữ liệu để sử dụng lại sau này. 