#!/usr/bin/env python3
"""
Test script for Task 1: HTTP server with cookie session
"""

import socket
import time

def send_http_request(host, port, request):
    """Send HTTP request and return response"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.sendall(request.encode())
        
        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
        
        sock.close()
        return response.decode()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_login_page():
    """Test GET /login.html"""
    print("=== Testing GET /login.html ===")
    request = "GET /login.html HTTP/1.1\r\nHost: localhost\r\n\r\n"
    response = send_http_request("localhost", 9000, request)
    if response:
        print("Status:", response.split('\r\n')[0])
        if "200 OK" in response:
            print("✓ Login page accessible")
        else:
            print("✗ Login page not accessible")
    else:
        print("✗ Connection failed")

def test_login_success():
    """Test POST /login with correct credentials"""
    print("\n=== Testing POST /login (correct credentials) ===")
    body = "username=admin&password=password"
    request = f"POST /login HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {len(body)}\r\n\r\n{body}"
    response = send_http_request("localhost", 9000, request)
    if response:
        print("Status:", response.split('\r\n')[0])
        if "200 OK" in response and "Set-Cookie: auth=true" in response:
            print("✓ Login successful with cookie set")
        else:
            print("✗ Login failed or cookie not set")
    else:
        print("✗ Connection failed")

def test_login_failure():
    """Test POST /login with wrong credentials"""
    print("\n=== Testing POST /login (wrong credentials) ===")
    body = "username=wrong&password=wrong"
    request = f"POST /login HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {len(body)}\r\n\r\n{body}"
    response = send_http_request("localhost", 9000, request)
    if response:
        print("Status:", response.split('\r\n')[0])
        if "401 Unauthorized" in response:
            print("✓ Login correctly rejected")
        else:
            print("✗ Login should have been rejected")
    else:
        print("✗ Connection failed")

def test_index_without_cookie():
    """Test GET / without cookie"""
    print("\n=== Testing GET / (without cookie) ===")
    request = "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
    response = send_http_request("localhost", 9000, request)
    if response:
        print("Status:", response.split('\r\n')[0])
        if "401 Unauthorized" in response:
            print("✓ Index page correctly protected")
        else:
            print("✗ Index page should be protected")
    else:
        print("✗ Connection failed")

def test_index_with_cookie():
    """Test GET / with auth cookie"""
    print("\n=== Testing GET / (with auth cookie) ===")
    request = "GET / HTTP/1.1\r\nHost: localhost\r\nCookie: auth=true\r\n\r\n"
    response = send_http_request("localhost", 9000, request)
    if response:
        print("Status:", response.split('\r\n')[0])
        if "200 OK" in response:
            print("✓ Index page accessible with cookie")
        else:
            print("✗ Index page should be accessible with cookie")
    else:
        print("✗ Connection failed")

if __name__ == "__main__":
    print("Starting Task 1 Authentication Tests...")
    print("Make sure backend server is running on port 9000")
    
    # Wait a bit for server to start
    time.sleep(2)
    
    test_login_page()
    test_login_failure()
    test_login_success()
    test_index_without_cookie()
    test_index_with_cookie()
    
    print("\n=== Test Summary ===")
    print("Task 1A: Authentication handling - POST /login")
    print("Task 1B: Cookie-based access control - GET /")
    print("All tests completed!")
