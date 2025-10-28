#!/usr/bin/env python3
"""
Test script for Task 1 - HTTP server with cookie session
Tests authentication handling and cookie-based access control
"""

import socket
import time
import threading
import subprocess
import sys
import os

def test_http_request(host, port, request):
    """Send HTTP request and return response"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.send(request.encode())
        
        response = b""
        while True:
            data = sock.recv(1024)
            if not data:
                break
            response += data
        
        sock.close()
        return response.decode()
    except Exception as e:
        print(f"Error sending request: {e}")
        return None

def test_login_success():
    """Test successful login with correct credentials"""
    print("\n=== Testing successful login ===")
    
    request = """POST /login HTTP/1.1\r
Host: localhost:9000\r
Content-Type: application/x-www-form-urlencoded\r
Content-Length: 27\r
\r
username=admin&password=password"""
    
    response = test_http_request('localhost', 9000, request)
    if response:
        print("Response received:")
        print(response[:500] + "..." if len(response) > 500 else response)
        
        if "Set-Cookie: auth=true" in response:
            print("✓ SUCCESS: Set-Cookie header found")
        else:
            print("✗ FAIL: Set-Cookie header not found")
            
        if "200 OK" in response:
            print("✓ SUCCESS: 200 OK status")
        else:
            print("✗ FAIL: Expected 200 OK status")
    else:
        print("✗ FAIL: No response received")

def test_login_failure():
    """Test login failure with incorrect credentials"""
    print("\n=== Testing login failure ===")
    
    request = """POST /login HTTP/1.1\r
Host: localhost:9000\r
Content-Type: application/x-www-form-urlencoded\r
Content-Length: 30\r
\r
username=wrong&password=wrong"""
    
    response = test_http_request('localhost', 9000, request)
    if response:
        print("Response received:")
        print(response[:500] + "..." if len(response) > 500 else response)
        
        if "401 Unauthorized" in response:
            print("✓ SUCCESS: 401 Unauthorized status")
        else:
            print("✗ FAIL: Expected 401 Unauthorized status")
            
        if "Invalid credentials" in response:
            print("✓ SUCCESS: Error message found")
        else:
            print("✗ FAIL: Error message not found")
    else:
        print("✗ FAIL: No response received")

def test_protected_access_without_cookie():
    """Test accessing protected resource without cookie"""
    print("\n=== Testing protected access without cookie ===")
    
    request = """GET / HTTP/1.1\r
Host: localhost:9000\r
\r
"""
    
    response = test_http_request('localhost', 9000, request)
    if response:
        print("Response received:")
        print(response[:500] + "..." if len(response) > 500 else response)
        
        if "401 Unauthorized" in response:
            print("✓ SUCCESS: 401 Unauthorized status")
        else:
            print("✗ FAIL: Expected 401 Unauthorized status")
            
        if "Please login first" in response:
            print("✓ SUCCESS: Access denied message found")
        else:
            print("✗ FAIL: Access denied message not found")
    else:
        print("✗ FAIL: No response received")

def test_protected_access_with_cookie():
    """Test accessing protected resource with valid cookie"""
    print("\n=== Testing protected access with cookie ===")
    
    request = """GET / HTTP/1.1\r
Host: localhost:9000\r
Cookie: auth=true\r
\r
"""
    
    response = test_http_request('localhost', 9000, request)
    if response:
        print("Response received:")
        print(response[:500] + "..." if len(response) > 500 else response)
        
        if "200 OK" in response:
            print("✓ SUCCESS: 200 OK status")
        else:
            print("✗ FAIL: Expected 200 OK status")
            
        if "bksysnet@hcmut" in response:
            print("✓ SUCCESS: Index page content found")
        else:
            print("✗ FAIL: Index page content not found")
    else:
        print("✗ FAIL: No response received")

def start_backend_server():
    """Start the backend server in a separate process"""
    print("Starting backend server...")
    try:
        # Change to the correct directory
        os.chdir('/CO3094-weaprous')
        
        # Start backend server
        process = subprocess.Popen([
            sys.executable, 'start_backend.py', 
            '--server-ip', '0.0.0.0', 
            '--server-port', '9000'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for server to start
        time.sleep(2)
        return process
    except Exception as e:
        print(f"Error starting backend server: {e}")
        return None

def main():
    """Main test function"""
    print("Task 1 Test Suite - HTTP Server with Cookie Session")
    print("=" * 50)
    
    # Start backend server
    server_process = start_backend_server()
    if not server_process:
        print("Failed to start backend server. Exiting.")
        return
    
    try:
        # Wait for server to be ready
        time.sleep(3)
        
        # Run tests
        test_login_success()
        test_login_failure()
        test_protected_access_without_cookie()
        test_protected_access_with_cookie()
        
        print("\n" + "=" * 50)
        print("Test suite completed!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        # Clean up
        if server_process:
            print("Stopping backend server...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    main()
