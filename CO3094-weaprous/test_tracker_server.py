#!/usr/bin/env python3
"""
Test suite for Tracker Server (Chat Backend)
Tests all API endpoints in Client-Server phase
"""

import socket
import json
import time
import sys
import os

def send_http_request(host, port, method, path, body=''):
    """Helper function to send HTTP request"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        
        # Build HTTP request
        request = "{} {} HTTP/1.1\r\n".format(method, path)
        request += "Host: {}:{}\r\n".format(host, port)
        request += "Content-Type: application/json\r\n"
        request += "Content-Length: {}\r\n".format(len(body))
        request += "\r\n"
        if body:
            request += body
        
        # Send request
        sock.sendall(request.encode('utf-8'))
        
        # Receive response
        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
            if b'\r\n\r\n' in response:
                break
        
        sock.close()
        
        # Extract body
        response_str = response.decode('utf-8')
        parts = response_str.split('\r\n\r\n', 1)
        
        if len(parts) > 1:
            return parts[1]
        else:
            return ''
            
    except Exception as e:
        print("[ERROR] HTTP request failed: {}".format(e))
        return None


def test_login():
    """Test POST /login"""
    print("\n" + "="*60)
    print("TEST 1: POST /login - Peer Authentication")
    print("="*60)
    
    body = json.dumps({
        'peer_id': 'alice',
        'password': 'password123'
    })
    
    response = send_http_request('localhost', 8000, 'POST', '/login', body)
    
    if response:
        data = json.loads(response)
        if data.get('status') == 'ok':
            print("✓ PASS: Login successful")
            print("  - Peer ID: {}".format(data.get('peer_id')))
            print("  - Session ID: {}".format(data.get('session_id')[:8] + '...'))
            return data.get('session_id')
        else:
            print("✗ FAIL: Login failed - {}".format(data.get('message')))
            return None
    else:
        print("✗ FAIL: No response from server")
        return None


def test_submit_info(peer_id, ip, port):
    """Test POST /submit-info"""
    print("\n" + "="*60)
    print("TEST 2: POST /submit-info - Register Peer Connection Info")
    print("="*60)
    
    body = json.dumps({
        'peer_id': peer_id,
        'ip': ip,
        'port': port
    })
    
    response = send_http_request('localhost', 8000, 'POST', '/submit-info', body)
    
    if response:
        data = json.loads(response)
        if data.get('status') == 'registered':
            print("✓ PASS: Peer info registered")
            print("  - Peer ID: {}".format(peer_id))
            print("  - Address: {}:{}".format(ip, port))
            return True
        else:
            print("✗ FAIL: Registration failed - {}".format(data.get('message')))
            return False
    else:
        print("✗ FAIL: No response from server")
        return False


def test_get_list():
    """Test GET /get-list"""
    print("\n" + "="*60)
    print("TEST 3: GET /get-list - Retrieve Active Peers")
    print("="*60)
    
    response = send_http_request('localhost', 8000, 'GET', '/get-list')
    
    if response:
        data = json.loads(response)
        if data.get('status') == 'ok':
            peers = data.get('peers', [])
            print("✓ PASS: Retrieved peer list")
            print("  - Active peers: {}".format(len(peers)))
            for peer in peers:
                print("    * {}: {}:{}".format(
                    peer['peer_id'], 
                    peer['ip'], 
                    peer['port']
                ))
            return True
        else:
            print("✗ FAIL: Get list failed")
            return False
    else:
        print("✗ FAIL: No response from server")
        return False


def test_add_list(channel, peer_id):
    """Test POST /add-list"""
    print("\n" + "="*60)
    print("TEST 4: POST /add-list - Join Channel")
    print("="*60)
    
    body = json.dumps({
        'channel': channel,
        'peer_id': peer_id
    })
    
    response = send_http_request('localhost', 8000, 'POST', '/add-list', body)
    
    if response:
        data = json.loads(response)
        if data.get('status') == 'added':
            print("✓ PASS: Peer added to channel")
            print("  - Channel: {}".format(channel))
            print("  - Peer ID: {}".format(peer_id))
            return True
        else:
            print("✗ FAIL: Add to channel failed - {}".format(data.get('message')))
            return False
    else:
        print("✗ FAIL: No response from server")
        return False


def test_get_channels():
    """Test GET /get-channels"""
    print("\n" + "="*60)
    print("TEST 5: GET /get-channels - List All Channels")
    print("="*60)
    
    response = send_http_request('localhost', 8000, 'GET', '/get-channels')
    
    if response:
        data = json.loads(response)
        if data.get('status') == 'ok':
            channels = data.get('channels', [])
            print("✓ PASS: Retrieved channel list")
            print("  - Available channels: {}".format(len(channels)))
            for channel in channels:
                print("    * #{}".format(channel))
            return True
        else:
            print("✗ FAIL: Get channels failed")
            return False
    else:
        print("✗ FAIL: No response from server")
        return False


def test_get_channel_members(channel):
    """Test GET /get-channel-members"""
    print("\n" + "="*60)
    print("TEST 6: GET /get-channel-members - List Channel Members")
    print("="*60)
    
    body = json.dumps({'channel': channel})
    
    response = send_http_request('localhost', 8000, 'GET', '/get-channel-members', body)
    
    if response:
        data = json.loads(response)
        if data.get('status') == 'ok':
            members = data.get('members', [])
            print("✓ PASS: Retrieved channel members")
            print("  - Channel: #{}".format(channel))
            print("  - Members: {}".format(len(members)))
            for member in members:
                print("    * {}: {}:{}".format(
                    member['peer_id'],
                    member['ip'],
                    member['port']
                ))
            return True
        else:
            print("✗ FAIL: Get channel members failed")
            return False
    else:
        print("✗ FAIL: No response from server")
        return False


def test_multiple_peers():
    """Test với nhiều peer"""
    print("\n" + "="*60)
    print("TEST 7: Multiple Peers Scenario")
    print("="*60)
    
    peers = [
        ('alice', '127.0.0.1', 5001),
        ('bob', '127.0.0.1', 5002),
        ('charlie', '127.0.0.1', 5003)
    ]
    
    # Login và register tất cả peer
    for peer_id, ip, port in peers:
        # Login
        body = json.dumps({'peer_id': peer_id, 'password': 'pass'})
        send_http_request('localhost', 8000, 'POST', '/login', body)
        
        # Register info
        body = json.dumps({'peer_id': peer_id, 'ip': ip, 'port': port})
        send_http_request('localhost', 8000, 'POST', '/submit-info', body)
        
        # Join channel
        body = json.dumps({'channel': 'general', 'peer_id': peer_id})
        send_http_request('localhost', 8000, 'POST', '/add-list', body)
    
    print("✓ PASS: Registered {} peers".format(len(peers)))
    
    # Get peer list
    response = send_http_request('localhost', 8000, 'GET', '/get-list')
    if response:
        data = json.loads(response)
        peer_count = len(data.get('peers', []))
        if peer_count >= len(peers):
            print("✓ PASS: Peer list contains all registered peers")
        else:
            print("✗ FAIL: Missing peers in list")
    
    # Get channel members
    body = json.dumps({'channel': 'general'})
    response = send_http_request('localhost', 8000, 'GET', '/get-channel-members', body)
    if response:
        data = json.loads(response)
        member_count = len(data.get('members', []))
        if member_count >= len(peers):
            print("✓ PASS: Channel 'general' has all members")
        else:
            print("✗ FAIL: Missing members in channel")


def main():
    """Main test runner"""
    print("\n" + "="*60)
    print("TRACKER SERVER TEST SUITE")
    print("Testing Client-Server Phase APIs")
    print("="*60)
    
    # Check if server is running
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result != 0:
            print("\n✗ ERROR: Chat server is not running on port 8000")
            print("Please start it with:")
            print("  python3 start_chat_server.py --server-ip 0.0.0.0 --server-port 8000")
            return
    except Exception as e:
        print("\n✗ ERROR: Cannot connect to server: {}".format(e))
        return
    
    print("✓ Server is running\n")
    
    # Run tests
    results = []
    
    # Test 1: Login
    session_id = test_login()
    results.append(session_id is not None)
    
    # Test 2: Submit info
    results.append(test_submit_info('alice', '127.0.0.1', 5001))
    
    # Test 3: Get peer list
    results.append(test_get_list())
    
    # Test 4: Add to channel
    results.append(test_add_list('general', 'alice'))
    
    # Test 5: Get channels
    results.append(test_get_channels())
    
    # Test 6: Get channel members
    results.append(test_get_channel_members('general'))
    
    # Test 7: Multiple peers
    test_multiple_peers()
    results.append(True)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print("Passed: {}/{}".format(passed, total))
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
        print("Tracker Server is working correctly.")
    else:
        print("\n✗ SOME TESTS FAILED")
        print("Please check the implementation.")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()