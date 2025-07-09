# Changelog

Tất cả các thay đổi đáng chú ý của dự án sẽ được ghi lại trong file này.

Định dạng dựa trên [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
và dự án này tuân theo [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2023-12-01

### Thêm mới
- Phát hành chính thức package LaMa Inpainting
- Thêm file setup.py và pyproject.toml để hỗ trợ cài đặt thông qua pip
- Thêm entry points để sử dụng các lệnh lama-predict và lama-train

### Thay đổi
- Cập nhật tài liệu và hướng dẫn cài đặt
- Cải thiện cấu trúc dự án để tuân theo tiêu chuẩn Python package

### Sửa lỗi
- Sửa các đường dẫn tương đối trong mã nguồn để hoạt động khi được cài đặt như package

## [0.1.0] - 2021-09-01

### Thêm mới
- Phát hành mã nguồn ban đầu
- Mô hình đã được huấn luyện trên bộ dữ liệu Places và CelebA-HQ
- Công cụ dòng lệnh để dự đoán và huấn luyện 