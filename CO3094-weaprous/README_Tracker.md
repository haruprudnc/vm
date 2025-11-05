# Tracker Server - Chat Application Client-Server Module

**Status**: ✅ **Complete** - All 5 APIs tested and working (100% pass rate)

**Last Updated**: Latest implementation với exception handling cho GET /get-list

## Tổng quan

Tracker Server là phần **xương sống** của ứng dụng chat, triển khai **Client-Server paradigm** để quản lý và điều phối các peers trong hệ thống chat P2P. Server cung cấp các APIs RESTful để:

- **Peer registration**: Đăng ký peer với IP và port
- **Peer discovery**: Khám phá danh sách các peers đang hoạt động
- **Peer tracking**: Theo dõi trạng thái peers (active/inactive)
- **Connection setup**: Cung cấp thông tin kết nối để peers thiết lập P2P connections

## Kiến trúc

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Peer 1    │◄────►│   Tracker    │◄────►│   Peer 2    │
│ 127.0.0.1:8001│      │  Server     │      │ 127.0.0.1:8002│
└─────────────┘      │  7001        │      └─────────────┘
                     └──────────────┘
                            ▲
                            │
                     ┌──────┴──────┐
                     │             │
                ┌────┴───┐    ┌───┴────┐
                │Peer 3  │    │Peer 4  │
                └────────┘    └────────┘
```

## Các file đã implement

### 1. Core Modules

#### `peer_manager.py` - Thread-safe Peer Management
- **PeerManager class**: Quản lý peers với thread-safe operations
- **Features**:
  - Register/remove peers
  - Track active peers với timeout mechanism
  - Thread-safe operations với `threading.Lock`
  - In-memory peer storage
  - Automatic cleanup inactive peers

#### `tracker_server.py` - API Handlers
- **5 API handlers**:
  1. `login()` - Peer authentication
  2. `submit_info()` - Peer registration
  3. `get_list()` - Get active peers list
  4. `add_list()` - Add peer to active list
  5. `connect_peer()` - Get connection info for P2P setup

### 2. Entry Point

#### `start_tracker.py` - Server Startup
- Sử dụng **WeApRous** framework
- Đăng ký 5 routes cho các APIs
- Command-line arguments cho IP/port configuration
- Default port: **7001** (7000 có thể conflict với macOS ControlCenter)

### 3. Testing

#### `test_tracker.py` - Test Suite
- Test tất cả 5 APIs
- JSON request/response validation
- Error handling tests
- Integration tests

### 4. Modified Files

#### `daemon/response.py`
- Thêm method `build_json_response()` để build JSON HTTP responses

#### `daemon/request.py`
- Đã có sẵn JSON parsing (`parse_JSON()`, `isJSON()`)
- `json_data` attribute để access parsed JSON body

#### `daemon/httpadapter.py`
- Đã có sẵn JSON response handling
- Tự động convert dict response thành JSON
- **Exception cho GET /get-list**: Thêm exception để GET /get-list hoạt động với logic hiện tại (non-JSON requests thường return ngay, nhưng GET /get-list cần chạy handler để trả về JSON response)

## 5 APIs Implementation

### 1. POST /login - Peer Authentication

**Purpose**: Authenticate peer before allowing access to tracker services.

**Request Body**:
```json
{
  "peer_id": "peer1",
  "password": "optional_password"
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "Login successful",
  "peer_id": "peer1"
}
```

**Error Response** (400 Bad Request):
```json
{
  "status": "error",
  "message": "peer_id is required"
}
```

### 2. POST /submit-info - Peer Registration

**Purpose**: Register peer with IP and port to tracker server.

**Request Body**:
```json
{
  "peer_id": "peer1",
  "ip": "127.0.0.1",
  "port": 8001,
  "metadata": {
    "username": "user1",
    "version": "1.0"
  }
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "Peer registered successfully",
  "peer_id": "peer1",
  "ip": "127.0.0.1",
  "port": 8001
}
```

**Error Response** (400 Bad Request):
```json
{
  "status": "error",
  "message": "ip is required"
}
```

### 3. GET /get-list - Get Active Peers List

**Purpose**: Retrieve list of all active peers from tracker.

**Request**: No body required

**Query Parameters** (optional):
- `exclude_id`: Peer ID to exclude from list

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "Retrieved peer list successfully",
  "count": 2,
  "peers": [
    {
      "peer_id": "peer1",
      "ip": "127.0.0.1",
      "port": 8001,
      "metadata": {"username": "user1"},
      "status": "active"
    },
    {
      "peer_id": "peer2",
      "ip": "127.0.0.1",
      "port": 8002,
      "metadata": {},
      "status": "active"
    }
  ]
}
```

### 4. POST /add-list - Add Peer to List

**Purpose**: Mark a peer as active in the tracker list.

**Request Body**:
```json
{
  "peer_id": "peer1"
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "Peer added to list successfully",
  "peer_id": "peer1"
}
```

**Error Response** (404 Not Found):
```json
{
  "status": "error",
  "message": "Peer not found. Register peer first using /submit-info"
}
```

### 5. POST /connect-peer - Initiate P2P Connection

**Purpose**: Get target peer information to initiate direct P2P connection.

**Request Body**:
```json
{
  "from_peer_id": "peer1",
  "to_peer_id": "peer2"
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "Connection information retrieved",
  "target_peer": {
    "peer_id": "peer2",
    "ip": "127.0.0.1",
    "port": 8002,
    "metadata": {}
  }
}
```

**Error Response** (404 Not Found):
```json
{
  "status": "error",
  "message": "Target peer not found"
}
```

## Cách chạy

### 1. Start Tracker Server

```bash
cd /Users/nguyenducgiabao/CO3094-weaprous/CO3094-weaprous
python3 start_tracker.py --server-ip 0.0.0.0 --server-port 7001
```

**Note**: Port 7001 được dùng thay vì 7000 để tránh conflict với macOS ControlCenter (port 7000).

**Expected Output**:
```
============================================================
Tracker Server - Chat Application Client-Server Module
============================================================
Starting tracker server on 0.0.0.0:7001
APIs available:
  POST   /login        - Peer authentication
  POST   /submit-info  - Peer registration
  GET    /get-list     - Get active peers list
  POST   /add-list     - Add peer to list
  POST   /connect-peer - Initiate P2P connection
============================================================
[Backend] Listening on port 7001
```

### 2. Test với script test

```bash
python3 test_tracker.py
```

### 3. Test thủ công với curl

```bash
# Test login
curl -X POST http://localhost:7001/login \
  -H "Content-Type: application/json" \
  -d '{"peer_id": "peer1", "password": "test123"}'

# Test submit-info
curl -X POST http://localhost:7001/submit-info \
  -H "Content-Type: application/json" \
  -d '{"peer_id": "peer1", "ip": "127.0.0.1", "port": 8001}'

# Test get-list
curl -X GET http://localhost:7001/get-list

# Test add-list
curl -X POST http://localhost:7001/add-list \
  -H "Content-Type: application/json" \
  -d '{"peer_id": "peer1"}'

# Test connect-peer
curl -X POST http://localhost:7001/connect-peer \
  -H "Content-Type: application/json" \
  -d '{"from_peer_id": "peer1", "to_peer_id": "peer2"}'
```

## Technical Requirements

### ✅ Concurrency
- **Thread-safe operations**: Sử dụng `threading.Lock` trong `PeerManager`
- **Multi-threaded server**: WeApRous/Backend sử dụng threading để handle multiple connections

### ✅ Error Handling
- **Input validation**: Validate required fields trong tất cả APIs
- **Exception handling**: Try-except blocks trong tất cả handlers
- **Error responses**: Trả về proper HTTP status codes và error messages

### ✅ JSON Request/Response
- **Request parsing**: Tự động parse JSON body từ request
- **Response building**: Tự động serialize dict thành JSON response
- **Content-Type**: Proper `application/json` headers

### ✅ Thread-safe Operations
- **PeerManager lock**: Tất cả peer operations được bảo vệ bằng lock
- **Atomic operations**: Register, remove, update operations là atomic

### ✅ In-memory Peer Tracking
- **Peer storage**: Dictionary-based in-memory storage
- **Timeout mechanism**: Automatic cleanup inactive peers (default: 300s)
- **Status tracking**: Track peer status (active/inactive)

### ✅ GET Request Handling
- **Exception implementation**: GET /get-list có exception trong `httpadapter.py` để bypass logic non-JSON return early
- **Logic preservation**: Giữ nguyên logic ban đầu cho các request khác (non-JSON requests return ngay với `resp.build_response(req)`)
- **Handler execution**: GET /get-list vẫn chạy handler và trả về JSON response đúng cách

## Files Structure

```
CO3094-weaprous/
├── peer_manager.py          # Thread-safe peer management
├── tracker_server.py        # 5 API handlers
├── start_tracker.py         # Entry point
├── test_tracker.py          # Test suite
├── README_Tracker.md        # Documentation
└── daemon/
    ├── response.py          # Modified: added build_json_response()
    ├── request.py           # Already has JSON parsing
    └── httpadapter.py       # Already has JSON response handling
```

## Test Cases

### ✅ Test 1: POST /login
- **Input**: Valid peer_id
- **Expected**: 200 OK + success message
- **Result**: ✓ PASS
- **Test Output**: `{"status": "success", "message": "Login successful", "peer_id": "peer1"}`

### ✅ Test 2: POST /submit-info
- **Input**: peer_id, ip, port
- **Expected**: 200 OK + registered peer info
- **Result**: ✓ PASS
- **Test Output**: `{"status": "success", "message": "Peer registered successfully", "peer_id": "peer1", "ip": "127.0.0.1", "port": 8001}`

### ✅ Test 3: GET /get-list
- **Input**: None
- **Expected**: 200 OK + list of active peers
- **Result**: ✓ PASS
- **Note**: Cần exception trong `httpadapter.py` để GET request chạy handler (logic ban đầu chỉ chạy handler cho JSON requests)
- **Test Output**: `{"status": "success", "message": "Retrieved peer list successfully", "count": 1, "peers": [...]}`

### ✅ Test 4: POST /add-list
- **Input**: peer_id (registered)
- **Expected**: 200 OK + success message
- **Result**: ✓ PASS
- **Test Output**: `{"status": "success", "message": "Peer added to list successfully", "peer_id": "peer1"}`

### ✅ Test 5: POST /connect-peer
- **Input**: from_peer_id, to_peer_id
- **Expected**: 200 OK + target peer connection info
- **Result**: ✓ PASS
- **Test Output**: `{"status": "success", "message": "Connection information retrieved", "target_peer": {...}}`

### Test Summary
- **Total Tests**: 5
- **Passed**: 5 ✓
- **Failed**: 0 ✗
- **Success Rate**: 100%

## Error Handling Examples

### Missing Required Fields
```json
POST /submit-info
{
  "peer_id": "peer1"
  // Missing: ip, port
}

Response (400 Bad Request):
{
  "status": "error",
  "message": "ip is required"
}
```

### Peer Not Found
```json
POST /connect-peer
{
  "from_peer_id": "peer1",
  "to_peer_id": "nonexistent"
}

Response (404 Not Found):
{
  "status": "error",
  "message": "Target peer not found"
}
```

## Integration với Task 1 và Chat Application

### Integration với Task 1 (HTTP Server with Cookies)
- Tracker Server sử dụng **WeApRous framework** từ Task 1
- Chia sẻ infrastructure: `daemon/backend.py`, `daemon/httpadapter.py`, `daemon/request.py`, `daemon/response.py`
- Logic phân biệt: Task 1 xử lý form-based POST /login (Cookie auth), Tracker Server xử lý JSON POST /login (Peer auth)
- Có thể chạy cùng instance nhờ Content-Type routing trong `httpadapter.py`

Tracker Server là **bước đầu tiên** trong hybrid chat application:

1. **Initialization Phase** (Client-Server):
   - Peer đăng ký với Tracker Server (`/submit-info`)
   - Peer lấy danh sách peers (`/get-list`)
   - Peer lấy connection info (`/connect-peer`)

2. **Chatting Phase** (P2P):
   - Sau khi có connection info, peers thiết lập direct P2P connections
   - Communication không qua Tracker Server nữa

## Notes

- **Port**: Default port là **7001** (đổi từ 7000 để tránh conflict với macOS ControlCenter), có thể thay đổi bằng `--server-port`
- **Peer Timeout**: Default 300 seconds (5 minutes) before peer considered inactive
- **Thread Safety**: Tất cả peer operations đều thread-safe
- **In-memory Storage**: Peer data lưu trong memory, sẽ mất khi server restart
- **GET /get-list Exception**: Để GET /get-list hoạt động, đã thêm exception trong `httpadapter.py` vì logic ban đầu chỉ chạy handler cho JSON requests, nhưng GET /get-list cần trả về JSON response

## Next Steps

Sau khi Tracker Server hoàn thành, bước tiếp theo là:
- Implement Peer-to-Peer communication phase
- Implement broadcast-peer API
- Implement send-peer API
- Channel management system
