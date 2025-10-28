# Task 1 - HTTP Server with Cookie Session

## Tổng quan
Task 1 yêu cầu implement HTTP server với cookie session để xử lý authentication và access control. Server sẽ:
- Validate credentials khi login (username=admin, password=password)
- Set cookie khi login thành công
- Kiểm tra cookie khi truy cập protected resources
- Trả về 401 Unauthorized khi không có cookie hợp lệ

## Các file đã được implement

### 1. Backend Server (`daemon/backend.py`)
- Fixed threading implementation để handle multiple client connections
- Sử dụng HttpAdapter để xử lý HTTP requests

### 2. HTTP Adapter (`daemon/httpadapter.py`)
- **Task 1A**: Implement authentication handling cho POST /login
- **Task 1B**: Implement cookie-based access control cho GET /
- Thêm method `_parse_form_data()` để parse form data từ POST requests

### 3. Dictionary (`daemon/dictionary.py`)
- Fixed import error cho Python 3.13 (MutableMapping từ collections.abc)

### 4. Proxy (`daemon/proxy.py`)
- Fixed print statements để compatible với Python 3

## Cách chạy

### 1. Start Backend Server
```bash
cd /Users/nguyenducgiabao/CO3094-weaprous/CO3094-weaprous
python3 start_backend.py --server-ip 0.0.0.0 --server-port 9000
```

### 2. Test với script test
```bash
python3 test_task1.py
```

### 3. Demo với browser
1. Mở browser và truy cập `http://localhost:9000/login.html`
2. Nhập username: `admin`, password: `password`
3. Submit form
4. Sau khi login thành công, truy cập `http://localhost:9000/` để xem protected content

## Test Cases

### ✅ Test 1: Successful Login
- POST /login với username=admin, password=password
- Expected: 200 OK + Set-Cookie: auth=true

### ✅ Test 2: Failed Login  
- POST /login với username/password sai
- Expected: 401 Unauthorized

### ✅ Test 3: Protected Access Without Cookie
- GET / không có cookie
- Expected: 401 Unauthorized

### ✅ Test 4: Protected Access With Cookie
- GET / với Cookie: auth=true
- Expected: 200 OK + index page content

## Kết quả
Tất cả test cases đều PASS! Task 1 đã được hoàn thành thành công với:
- ✓ Authentication system working correctly
- ✓ Cookie-based access control implemented  
- ✓ Protected resources properly secured
- ✓ Login form validation working

## Files được tạo/sửa đổi
- `daemon/backend.py` - Fixed threading
- `daemon/httpadapter.py` - Main authentication logic
- `daemon/dictionary.py` - Fixed import
- `daemon/proxy.py` - Fixed print statements
- `test_task1.py` - Test suite
- `demo_task1.py` - Demo script
