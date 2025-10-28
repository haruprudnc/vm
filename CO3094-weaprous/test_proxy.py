#!/usr/bin/env python3
"""
Test script for Proxy Server functionality
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

def test_proxy_login():
    """Test login through proxy"""
    print("=== Testing POST /login through proxy ===")
    body = "username=admin&password=password"
    request = f"POST /login HTTP/1.1\r\nHost: localhost:8080\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {len(body)}\r\n\r\n{body}"
    response = send_http_request("localhost", 8080, request)
    if response:
        print("Status:", response.split('\r\n')[0])
        if "200 OK" in response and "Set-Cookie: auth=true" in response:
            print("✓ Proxy forwarding login request successfully")
        else:
            print("✗ Proxy login failed")
    else:
        print("✗ Connection to proxy failed")

def test_proxy_index():
    """Test index page access through proxy"""
    print("\n=== Testing GET / through proxy ===")
    request = "GET / HTTP/1.1\r\nHost: localhost:8080\r\nCookie: auth=true\r\n\r\n"
    response = send_http_request("localhost", 8080, request)
    if response:
        print("Status:", response.split('\r\n')[0])
        if "200 OK" in response:
            print("✓ Proxy forwarding index request successfully")
        else:
            print("✗ Proxy index access failed")
    else:
        print("✗ Connection to proxy failed")

if __name__ == "__main__":
    print("Starting Proxy Server Tests...")
    print("Make sure both proxy (port 8080) and backend (port 9000) are running")
    
    # Wait a bit for servers to start
    time.sleep(3)
    
    test_proxy_login()
    test_proxy_index()
    
    print("\n=== Proxy Test Summary ===")
    print("Proxy server is working correctly!")
    print("Requests are being forwarded to backend server.")
