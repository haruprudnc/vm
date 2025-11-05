#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
#

"""
Chat Client - Client-side implementation for chat application
"""

import socket
import json
import threading
import time

class ChatClient:
    """
    Chat client for peer discovery and registration.
    Handles client-server communication phase.
    """
    
    def __init__(self, peer_id, server_ip, server_port):
        """
        Initialize chat client.
        
        :param peer_id: Unique identifier for this peer
        :param server_ip: IP address of central server
        :param server_port: Port of central server
        """
        self.peer_id = peer_id
        self.server_ip = server_ip
        self.server_port = server_port
        
        # Client state
        self.session_id = None
        self.my_ip = None
        self.my_port = None
        
        # Peer connections (for P2P phase)
        self.peer_connections = {}  # {peer_id: socket}
        self.channels = []
        
        print("[ChatClient] Initialized client for peer: {}".format(peer_id))
    
    def login(self, password="default"):
        """
        Login to the chat server.
        
        :param password: Password for authentication
        :return: True if successful, False otherwise
        """
        try:
            body = json.dumps({
                'peer_id': self.peer_id,
                'password': password
            })
            
            response = self.send_http_request('/login', 'POST', body)
            data = json.loads(response)
            
            if data.get('status') == 'ok':
                self.session_id = data.get('session_id')
                print("[ChatClient] Login successful. Session: {}".format(
                    self.session_id[:8]))
                return True
            else:
                print("[ChatClient] Login failed: {}".format(
                    data.get('message')))
                return False
                
        except Exception as e:
            print("[ChatClient] Login error: {}".format(e))
            return False
    
    def register_peer_info(self, my_ip, my_port):
        """
        Register this peer's connection info with the server.
        
        :param my_ip: This peer's IP address
        :param my_port: This peer's listening port
        :return: True if successful
        """
        try:
            self.my_ip = my_ip
            self.my_port = my_port
            
            body = json.dumps({
                'peer_id': self.peer_id,
                'ip': my_ip,
                'port': my_port
            })
            
            response = self.send_http_request('/submit-info', 'POST', body)
            data = json.loads(response)
            
            if data.get('status') == 'registered':
                print("[ChatClient] Peer info registered: {}:{}".format(
                    my_ip, my_port))
                return True
            else:
                print("[ChatClient] Registration failed: {}".format(
                    data.get('message')))
                return False
                
        except Exception as e:
            print("[ChatClient] Register error: {}".format(e))
            return False
    
    def get_peer_list(self):
        """
        Retrieve list of active peers from server.
        
        :return: List of peer dictionaries
        """
        try:
            response = self.send_http_request('/get-list', 'GET')
            data = json.loads(response)
            
            if data.get('status') == 'ok':
                peers = data.get('peers', [])
                print("[ChatClient] Retrieved {} peers".format(len(peers)))
                return peers
            else:
                print("[ChatClient] Get peer list failed")
                return []
                
        except Exception as e:
            print("[ChatClient] Get peer list error: {}".format(e))
            return []
    
    def join_channel(self, channel_name):
        """
        Join a chat channel.
        
        :param channel_name: Name of channel to join
        :return: True if successful
        """
        try:
            body = json.dumps({
                'channel': channel_name,
                'peer_id': self.peer_id
            })
            
            response = self.send_http_request('/add-list', 'POST', body)
            data = json.loads(response)
            
            if data.get('status') == 'added':
                if channel_name not in self.channels:
                    self.channels.append(channel_name)
                print("[ChatClient] Joined channel: {}".format(channel_name))
                return True
            else:
                print("[ChatClient] Join channel failed")
                return False
                
        except Exception as e:
            print("[ChatClient] Join channel error: {}".format(e))
            return False
    
    def get_channel_list(self):
        """
        Get list of available channels.
        
        :return: List of channel names
        """
        try:
            response = self.send_http_request('/get-channels', 'GET')
            data = json.loads(response)
            
            if data.get('status') == 'ok':
                channels = data.get('channels', [])
                print("[ChatClient] Retrieved {} channels".format(len(channels)))
                return channels
            else:
                return []
                
        except Exception as e:
            print("[ChatClient] Get channel list error: {}".format(e))
            return []
    
    def get_channel_members(self, channel_name):
        """
        Get members of a specific channel.
        
        :param channel_name: Name of channel
        :return: List of member dictionaries
        """
        try:
            body = json.dumps({'channel': channel_name})
            response = self.send_http_request('/get-channel-members', 'GET', body)
            data = json.loads(response)
            
            if data.get('status') == 'ok':
                members = data.get('members', [])
                print("[ChatClient] Channel {} has {} members".format(
                    channel_name, len(members)))
                return members
            else:
                return []
                
        except Exception as e:
            print("[ChatClient] Get channel members error: {}".format(e))
            return []
    
    def send_http_request(self, path, method, body=''):
        """
        Send HTTP request to server.
        
        :param path: API endpoint path
        :param method: HTTP method (GET, POST, etc.)
        :param body: Request body
        :return: Response body as string
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.server_ip, self.server_port))
            
            # Build HTTP request
            request = "{} {} HTTP/1.1\r\n".format(method, path)
            request += "Host: {}:{}\r\n".format(self.server_ip, self.server_port)
            request += "Content-Type: application/json\r\n"
            request += "Content-Length: {}\r\n".format(len(body))
            
            if self.session_id:
                request += "Cookie: session_id={}\r\n".format(self.session_id)
            
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
                    # Check if we have complete response
                    break
            
            sock.close()
            
            # Extract body from response
            response_str = response.decode('utf-8')
            parts = response_str.split('\r\n\r\n', 1)
            
            if len(parts) > 1:
                return parts[1]
            else:
                return ''
                
        except Exception as e:
            print("[ChatClient] HTTP request error: {}".format(e))
            return ''


# Test client
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Chat Client')
    parser.add_argument('--peer-id', required=True, help='Peer ID')
    parser.add_argument('--server-ip', default='127.0.0.1', help='Server IP')
    parser.add_argument('--server-port', type=int, default=8000, help='Server port')
    parser.add_argument('--my-ip', default='127.0.0.1', help='My IP')
    parser.add_argument('--my-port', type=int, default=5001, help='My port')
    args = parser.parse_args()
    
    # Create client
    client = ChatClient(args.peer_id, args.server_ip, args.server_port)
    
    # Test client-server operations
    print("\n=== Testing Client-Server Operations ===\n")
    
    # 1. Login
    if client.login():
        print("✓ Login successful")
    
    # 2. Register peer info
    if client.register_peer_info(args.my_ip, args.my_port):
        print("✓ Peer info registered")
    
    # 3. Get peer list
    peers = client.get_peer_list()
    print("✓ Peer list retrieved: {}".format(peers))
    
    # 4. Join a channel
    if client.join_channel('general'):
        print("✓ Joined channel 'general'")
    
    # 5. Get channel list
    channels = client.get_channel_list()
    print("✓ Channels: {}".format(channels))
    
    # 6. Get channel members
    members = client.get_channel_members('general')
    print("✓ Channel members: {}".format(members))
    
    print("\n=== Client-Server Test Complete ===\n")