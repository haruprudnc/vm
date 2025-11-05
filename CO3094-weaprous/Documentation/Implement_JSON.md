# JSON Support Documentation - WeApRous Framework

## Tổng quan các thay đổi

Ba module chính đã được cập nhật để hỗ trợ đầy đủ JSON cho RESTful API:

1. **request.py** - Parse JSON request body

---

## 1. REQUEST.PY - JSON Request Parsing

### Các thay đổi chính

#### 1.1. Thêm thuộc tính `json_data`

```python
class Request():
    def __init__(self):
        # ... existing attributes ...
        self.json_data = None  # NEW: Store parsed JSON
```

#### 1.2. Method `extract_body()` - Tách body từ HTTP request

```python
def extract_body(self, request):
    """
    Extract body from HTTP request.
    Body is everything after \r\n\r\n separator.
    """
    separator = '\r\n\r\n'
    if separator in request:
        parts = request.split(separator, 1)
        if len(parts) == 2:
            body = parts[1].strip()
            print("[request.py-extract_body] {}".format(body))
            return body
    return None
```

**Cách hoạt động:**
- HTTP request có format: `Headers\r\n\r\nBody`
- Split tại `\r\n\r\n` để tách headers và body
- Return body string hoặc None

#### 1.3. Method `parse_json_body()` - Parse JSON

```python
def parse_JSON(self, body):
    """
    Parse JSON from body string
    """
    if not body:
        return None
    try:
        print("[request.py-parse_JSON] {}".format(json.loads(body)))
        return json.loads(body)
    except Exception as e:
        print("[request.py-parse_JSON] Failed to parse {}!!!".format(e))
        return None
```

**Error handling:**
- Catch JSON parse errors
- Log error và return None
- Không crash server nếu JSON invalid

#### 1.4. Enhanced `prepare()` method

```python
def prepare(self, request, routes=None):
    """Prepares the entire request with the given parameters."""

    #^^ View RAW request^^#
    print("[Request] RAW request content: \n{}".format(request))

    # ... existing code ...
    
    # Extract body
    self.body = self.extract_body(request)
    
    # Check Content-Type and parse JSON
    if self.isJSON():
        self.json_data = self.parse_JSON(self.body)
```

**Flow:**
1. Extract raw body từ request
2. Check Content-Type header
3. Nếu là `application/json` → parse body thành dict/list
4. Store trong `self.json_data`

#### 1.5. Helper methods

```python
def is_json(self):
    """Check if request has JSON content type."""
    content_type = self.headers.get('content-type', '')
    if (self.body is not None) and ('application/json' in content_type):
        return True
    return False
```

