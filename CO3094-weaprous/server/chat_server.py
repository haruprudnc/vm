#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
#

"""
Chat Server - Central tracker for peer-to-peer chat application
"""

import json
import threading
import time
from daemon.weaprous import WeApRous

class ChatServer:
    """
    Central server for chat application using client-server paradigm.
    Maintains peer registry and channel information.
    """
    
    def __init__(self):
        self.app = WeApRous()
        
        # Data structures
        self.peers = {}  # {peer_id: {'ip': str, 'port': int, 'last_seen': timestamp}}
        self.channels = {}  # {channel_name: [peer_id1, peer_id2, ...]}
        self.sessions = {}  # {session_id: peer_id}
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Setup routes
        self.setup_routes()
        
        # Start cleanup thread
        self.start_cleanup_thread()
    
    def setup_routes(self):
        """Register all API endpoints"""
        
        @self.app.route('/login', methods=['POST'])
        def login(headers, body):
            """Handle user login/registration"""
            print("hello")
            return self.handle_login(body)
        
        @self.app.route('/submit-info', methods=['POST'])
        def submit_info(headers, body):
            """Register peer connection information"""
            return self.handle_submit_info(body)
        
        @self.app.route('/get-list', methods=['GET'])
        def get_list(headers, body):
            """Get list of active peers"""
            return self.handle_get_list()
        
        @self.app.route('/add-list', methods=['POST'])
        def add_list(headers, body):
            """Add peer to a channel"""
            return self.handle_add_list(body)
        
        @self.app.route('/get-channels', methods=['GET'])
        def get_channels(headers, body):
            """Get list of available channels"""
            return self.handle_get_channels()
        
        @self.app.route('/get-channel-members', methods=['GET'])
        def get_channel_members(headers, body):
            """Get members of a specific channel"""
            # Extract query parameters from headers if needed
            return self.handle_get_channel_members(body)
    
    def handle_login(self, body):
        """
        Process login request.
        
        :param body: JSON string with peer_id and password
        :return: JSON response with status and session_id
        """
        try:
            data = json.loads(body) if body else {}
            peer_id = data.get('peer_id', '')
            password = data.get('password', '')

            print("[ChatServer]", peer_id, ", " ,password)
            
            if not peer_id:
                return json.dumps({'status': 'error', 'message': 'peer_id required'})
            
            # Simple authentication (in production, use proper auth)
            # For this assignment, accept any password
            with self.lock:
                session_id = self.generate_session_id(peer_id)
                self.sessions[session_id] = peer_id
            
            print("[ChatServer] Login successful for peer: {}".format(peer_id))
            
            return json.dumps({
                'status': 'ok',
                'peer_id': peer_id,
                'session_id': session_id
            })
            
        except Exception as e:
            print("[ChatServer] Login error: {}".format(e))
            return json.dumps({'status': 'error', 'message': str(e)})
    
    def handle_submit_info(self, body):
        """
        Register peer connection information.
        
        :param body: JSON with peer_id, ip, port
        :return: JSON response
        """
        try:
            data = json.loads(body) if body else {}
            peer_id = data.get('peer_id')
            ip = data.get('ip')
            port = data.get('port')
            
            if not all([peer_id, ip, port]):
                return json.dumps({
                    'status': 'error',
                    'message': 'peer_id, ip, and port required'
                })
            
            with self.lock:
                self.peers[peer_id] = {
                    'ip': ip,
                    'port': int(port),
                    'last_seen': time.time()
                }
            
            print("[ChatServer] Registered peer {} at {}:{}".format(
                peer_id, ip, port))
            
            return json.dumps({
                'status': 'registered',
                'peer_id': peer_id
            })
            
        except Exception as e:
            print("[ChatServer] Submit info error: {}".format(e))
            return json.dumps({'status': 'error', 'message': str(e)})
    
    def handle_get_list(self):
        """
        Get list of all active peers.
        
        :return: JSON with peer list
        """
        try:
            with self.lock:
                peer_list = []
                for peer_id, info in self.peers.items():
                    peer_list.append({
                        'peer_id': peer_id,
                        'ip': info['ip'],
                        'port': info['port']
                    })
            
            print("[ChatServer] Returning {} active peers".format(len(peer_list)))
            
            return json.dumps({
                'status': 'ok',
                'peers': peer_list
            })
            
        except Exception as e:
            print("[ChatServer] Get list error: {}".format(e))
            return json.dumps({'status': 'error', 'message': str(e)})
    
    def handle_add_list(self, body):
        """
        Add peer to a channel.
        
        :param body: JSON with channel and peer_id
        :return: JSON response
        """
        try:
            data = json.loads(body) if body else {}
            channel = data.get('channel')
            peer_id = data.get('peer_id')
            
            if not all([channel, peer_id]):
                return json.dumps({
                    'status': 'error',
                    'message': 'channel and peer_id required'
                })
            
            with self.lock:
                if channel not in self.channels:
                    self.channels[channel] = []
                
                if peer_id not in self.channels[channel]:
                    self.channels[channel].append(peer_id)
            
            print("[ChatServer] Added {} to channel {}".format(peer_id, channel))
            
            return json.dumps({
                'status': 'added',
                'channel': channel,
                'peer_id': peer_id
            })
            
        except Exception as e:
            print("[ChatServer] Add list error: {}".format(e))
            return json.dumps({'status': 'error', 'message': str(e)})
    
    def handle_get_channels(self):
        """
        Get list of available channels.
        
        :return: JSON with channel list
        """
        try:
            with self.lock:
                channel_list = list(self.channels.keys())
            
            print("[ChatServer] Returning {} channels".format(len(channel_list)))
            
            return json.dumps({
                'status': 'ok',
                'channels': channel_list
            })
            
        except Exception as e:
            print("[ChatServer] Get channels error: {}".format(e))
            return json.dumps({'status': 'error', 'message': str(e)})
    
    def handle_get_channel_members(self, body):
        """
        Get members of a specific channel.
        
        :param body: JSON with channel name
        :return: JSON with member list
        """
        try:
            data = json.loads(body) if body else {}
            channel = data.get('channel')
            
            if not channel:
                return json.dumps({
                    'status': 'error',
                    'message': 'channel required'
                })
            
            with self.lock:
                members = self.channels.get(channel, [])
                member_details = []
                
                for peer_id in members:
                    if peer_id in self.peers:
                        member_details.append({
                            'peer_id': peer_id,
                            'ip': self.peers[peer_id]['ip'],
                            'port': self.peers[peer_id]['port']
                        })
            
            print("[ChatServer] Returning {} members for channel {}".format(
                len(member_details), channel))
            
            return json.dumps({
                'status': 'ok',
                'channel': channel,
                'members': member_details
            })
            
        except Exception as e:
            print("[ChatServer] Get channel members error: {}".format(e))
            return json.dumps({'status': 'error', 'message': str(e)})
    
    def generate_session_id(self, peer_id):
        """Generate a simple session ID"""
        import hashlib
        timestamp = str(time.time())
        session_str = "{}:{}".format(peer_id, timestamp)
        return hashlib.md5(session_str.encode()).hexdigest()
    
    def start_cleanup_thread(self):
        """Start background thread to remove inactive peers"""
        def cleanup():
            while True:
                time.sleep(60)  # Check every minute
                current_time = time.time()
                timeout = 300  # 5 minutes
                
                with self.lock:
                    inactive_peers = []
                    for peer_id, info in self.peers.items():
                        if current_time - info['last_seen'] > timeout:
                            inactive_peers.append(peer_id)
                    
                    # Remove inactive peers
                    for peer_id in inactive_peers:
                        del self.peers[peer_id]
                        print("[ChatServer] Removed inactive peer: {}".format(peer_id))
                        
                        # Remove from channels
                        for channel in self.channels:
                            if peer_id in self.channels[channel]:
                                self.channels[channel].remove(peer_id)
        
        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()
    
    def run(self, ip, port):
        """Start the chat server"""
        print("[ChatServer] Starting on {}:{}".format(ip, port))
        self.app.prepare_address(ip, port)
        self.app.run()


# Entry point
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Chat Server')
    parser.add_argument('--server-ip', default='127.0.0.1', help='Server IP')
    parser.add_argument('--server-port', type=int, default=8000, help='Server port')
    args = parser.parse_args()
    
    server = ChatServer()
    server.run(args.server_ip, args.server_port)