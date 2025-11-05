#!/usr/bin/env python3
"""
Test script for Tracker Server APIs
Tests all 7 APIs: login, submit-info, get-list, add-list, connect-peer, broadcast-peer, send-peer
"""

import socket
import json
import time
import sys

# Default port for Tracker Server (can be overridden)
TRACKER_PORT = 7001  # Changed from 7000 to avoid conflict with macOS ControlCenter


def send_http_request(host, port, method, path, body=None, headers=None):
    """Send HTTP request and return response"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        
        # Build request
        request_line = "{} {} HTTP/1.1\r\n".format(method, path)
        request_headers = "Host: {}:{}\r\n".format(host, port)
        
        if headers:
            for key, value in headers.items():
                request_headers += "{}: {}\r\n".format(key, value)
        
        if body:
            if isinstance(body, dict):
                body_str = json.dumps(body)
            else:
                body_str = body
            
            request_headers += "Content-Type: application/json\r\n"
            request_headers += "Content-Length: {}\r\n".format(len(body_str))
            request = request_line + request_headers + "\r\n" + body_str
        else:
            request = request_line + request_headers + "\r\n"
        
        sock.sendall(request.encode())
        
        # Receive response
        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
        
        sock.close()
        return response.decode()
    except Exception as e:
        print("Error sending request: {}".format(e))
        return None


def parse_json_response(response):
    """Parse JSON from HTTP response"""
    if not response:
        return None
    
    try:
        # Find JSON body (after \r\n\r\n)
        parts = response.split('\r\n\r\n', 1)
        if len(parts) == 2:
            body = parts[1]
            return json.loads(body)
    except Exception as e:
        print("Error parsing JSON: {}".format(e))
    
    return None


def test_login():
    """Test POST /login - Peer authentication"""
    print("\n=== Testing POST /login ===")
    
    body = {
        "peer_id": "peer1",
        "password": "test123"
    }
    
    response = send_http_request('localhost', TRACKER_PORT, 'POST', '/login', body)
    if response:
        status_line = response.split('\r\n')[0]
        print("Status: {}".format(status_line))
        
        json_data = parse_json_response(response)
        if json_data:
            print("Response: {}".format(json.dumps(json_data, indent=2)))
            
            if json_data.get('status') == 'success':
                print("✓ Login successful")
                return True
            else:
                print("✗ Login failed")
                return False
        else:
            print("✗ Failed to parse JSON response")
            return False
    else:
        print("✗ No response received")
        return False


def test_submit_info():
    """Test POST /submit-info - Peer registration"""
    print("\n=== Testing POST /submit-info ===")
    
    body = {
        "peer_id": "peer1",
        "ip": "127.0.0.1",
        "port": 8001,
        "metadata": {
            "username": "user1",
            "version": "1.0"
        }
    }
    
    response = send_http_request('localhost', TRACKER_PORT, 'POST', '/submit-info', body)
    if response:
        status_line = response.split('\r\n')[0]
        print("Status: {}".format(status_line))
        
        json_data = parse_json_response(response)
        if json_data:
            print("Response: {}".format(json.dumps(json_data, indent=2)))
            
            if json_data.get('status') == 'success':
                print("✓ Peer registered successfully")
                return True
            else:
                print("✗ Peer registration failed")
                return False
        else:
            print("✗ Failed to parse JSON response")
            return False
    else:
        print("✗ No response received")
        return False


def test_get_list():
    """Test POST /get-list - Get active peers list"""
    print("\n=== Testing POST /get-list ===")
    
    body = {
        "peer_id": "peer1"
    }
    
    response = send_http_request('localhost', TRACKER_PORT, 'POST', '/get-list', body)
    if response:
        status_line = response.split('\r\n')[0]
        print("Status: {}".format(status_line))
        
        json_data = parse_json_response(response)
        if json_data:
            print("Response: {}".format(json.dumps(json_data, indent=2)))
            
            if json_data.get('status') == 'success':
                peers = json_data.get('peers', [])
                print("✓ Retrieved {} peers".format(len(peers)))
                return True
            else:
                print("✗ Failed to get peer list")
                return False
        else:
            print("✗ Failed to parse JSON response")
            return False
    else:
        print("✗ No response received")
        return False


def test_add_list():
    """Test POST /add-list - Add peer to list"""
    print("\n=== Testing POST /add-list ===")
    
    body = {
        "peer_id": "peer1"
    }
    
    response = send_http_request('localhost', TRACKER_PORT, 'POST', '/add-list', body)
    if response:
        status_line = response.split('\r\n')[0]
        print("Status: {}".format(status_line))
        
        json_data = parse_json_response(response)
        if json_data:
            print("Response: {}".format(json.dumps(json_data, indent=2)))
            
            if json_data.get('status') == 'success':
                print("✓ Peer added to list successfully")
                return True
            else:
                print("✗ Failed to add peer to list")
                return False
        else:
            print("✗ Failed to parse JSON response")
            return False
    else:
        print("✗ No response received")
        return False


def test_connect_peer():
    """Test POST /connect-peer - Initiate P2P connection"""
    print("\n=== Testing POST /connect-peer ===")
    
    # First register another peer
    body_reg = {
        "peer_id": "peer2",
        "ip": "127.0.0.1",
        "port": 8002
    }
    send_http_request('localhost', TRACKER_PORT, 'POST', '/submit-info', body_reg)
    time.sleep(0.5)  # Wait a bit
    
    # Now test connect-peer
    body = {
        "from_peer_id": "peer1",
        "to_peer_id": "peer2"
    }
    
    response = send_http_request('localhost', TRACKER_PORT, 'POST', '/connect-peer', body)
    if response:
        status_line = response.split('\r\n')[0]
        print("Status: {}".format(status_line))
        
        json_data = parse_json_response(response)
        if json_data:
            print("Response: {}".format(json.dumps(json_data, indent=2)))
            
            if json_data.get('status') == 'success':
                target_peer = json_data.get('target_peer', {})
                print("✓ Connection info retrieved: {}:{}".format(
                    target_peer.get('ip'), target_peer.get('port')
                ))
                return True
            else:
                print("✗ Failed to get connection info")
                return False
        else:
            print("✗ Failed to parse JSON response")
            return False
    else:
        print("✗ No response received")
        return False


def test_broadcast_peer():
    """Test POST /broadcast-peer - Broadcast message to peers"""
    print("\n=== Testing POST /broadcast-peer ===")
    
    # Register peer3 for testing
    body_reg = {
        "peer_id": "peer3",
        "ip": "127.0.0.1",
        "port": 8003
    }
    send_http_request('localhost', TRACKER_PORT, 'POST', '/submit-info', body_reg)
    time.sleep(0.5)
    
    # Test broadcast to all peers
    body = {
        "sender_peer_id": "peer1",
        "message": {
            "command": "public",
            "payload": "Hello everyone!",
            "time": "2025-01-01T00:00:00"
        }
    }
    
    response = send_http_request('localhost', TRACKER_PORT, 'POST', '/broadcast-peer', body)
    if response:
        status_line = response.split('\r\n')[0]
        print("Status: {}".format(status_line))
        
        json_data = parse_json_response(response)
        if json_data:
            print("Response: {}".format(json.dumps(json_data, indent=2)))
            
            if json_data.get('status') == 'success':
                target_peers = json_data.get('target_peers', [])
                count = json_data.get('count', 0)
                print("✓ Broadcast targets retrieved: {} peers".format(count))
                if count > 0:
                    print("  Target peers: {}".format([p.get('peer_id') for p in target_peers]))
                return True
            else:
                print("✗ Failed to get broadcast targets")
                return False
        else:
            print("✗ Failed to parse JSON response")
            return False
    else:
        print("✗ No response received")
        return False


def test_broadcast_peer_channel():
    """Test POST /broadcast-peer with channel"""
    print("\n=== Testing POST /broadcast-peer (with channel) ===")
    
    # Join peer1 and peer3 to a channel
    body_join1 = {
        "peer_id": "peer1",
        "channel": "test_channel"
    }
    send_http_request('localhost', TRACKER_PORT, 'POST', '/add-list', body_join1)
    
    body_join3 = {
        "peer_id": "peer3",
        "channel": "test_channel"
    }
    send_http_request('localhost', TRACKER_PORT, 'POST', '/add-list', body_join3)
    time.sleep(0.5)
    
    # Test broadcast to channel
    body = {
        "sender_peer_id": "peer1",
        "channel": "test_channel",
        "message": {
            "command": "channel",
            "channel": "test_channel",
            "payload": "Hello channel!",
            "time": "2025-01-01T00:00:00"
        }
    }
    
    response = send_http_request('localhost', TRACKER_PORT, 'POST', '/broadcast-peer', body)
    if response:
        status_line = response.split('\r\n')[0]
        print("Status: {}".format(status_line))
        
        json_data = parse_json_response(response)
        if json_data:
            print("Response: {}".format(json.dumps(json_data, indent=2)))
            
            if json_data.get('status') == 'success':
                target_peers = json_data.get('target_peers', [])
                count = json_data.get('count', 0)
                channel = json_data.get('channel')
                print("✓ Broadcast to channel '{}' retrieved: {} peers".format(channel, count))
                if count > 0:
                    print("  Target peers: {}".format([p.get('peer_id') for p in target_peers]))
                return True
            else:
                print("✗ Failed to get broadcast targets for channel")
                return False
        else:
            print("✗ Failed to parse JSON response")
            return False
    else:
        print("✗ No response received")
        return False


def test_send_peer():
    """Test POST /send-peer - Send message to specific peer"""
    print("\n=== Testing POST /send-peer ===")
    
    body = {
        "from_peer_id": "peer1",
        "to_peer_id": "peer2",
        "message": {
            "command": "dm",
            "payload": "Hello peer2!",
            "time": "2025-01-01T00:00:00"
        }
    }
    
    response = send_http_request('localhost', TRACKER_PORT, 'POST', '/send-peer', body)
    if response:
        status_line = response.split('\r\n')[0]
        print("Status: {}".format(status_line))
        
        json_data = parse_json_response(response)
        if json_data:
            print("Response: {}".format(json.dumps(json_data, indent=2)))
            
            if json_data.get('status') == 'success':
                target_peer = json_data.get('target_peer', {})
                print("✓ Target peer info retrieved: {}:{}".format(
                    target_peer.get('ip'), target_peer.get('port')
                ))
                return True
            else:
                print("✗ Failed to get target peer info")
                return False
        else:
            print("✗ Failed to parse JSON response")
            return False
    else:
        print("✗ No response received")
        return False


def main():
    """Main test function"""
    print("=" * 60)
    print("Tracker Server Test Suite")
    print("=" * 60)
    print("Make sure tracker server is running on port {}".format(TRACKER_PORT))
    print("Start with: python3 start_tracker.py --server-ip 0.0.0.0 --server-port {}".format(TRACKER_PORT))
    print("=" * 60)
    
    # Wait a bit for server to be ready
    time.sleep(1)
    
    results = []
    
    # Test 1: Login
    results.append(("Login", test_login()))
    
    # Test 2: Submit Info
    results.append(("Submit Info", test_submit_info()))
    
    # Test 3: Get List
    results.append(("Get List", test_get_list()))
    
    # Test 4: Add List
    results.append(("Add List", test_add_list()))
    
    # Test 5: Connect Peer
    results.append(("Connect Peer", test_connect_peer()))
    
    # Test 6: Broadcast Peer
    results.append(("Broadcast Peer", test_broadcast_peer()))
    
    # Test 7: Broadcast Peer (Channel)
    results.append(("Broadcast Peer (Channel)", test_broadcast_peer_channel()))
    
    # Test 8: Send Peer
    results.append(("Send Peer", test_send_peer()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print("{}: {}".format(test_name, status))
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print("Total: {} passed, {} failed".format(passed, failed))
    
    if failed == 0:
        print("All tests PASSED! ✓")
    else:
        print("Some tests FAILED ✗")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

