#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Student Implementation
# Tracker Server for Hybrid Chat Application
#

"""
start_tracker.py
~~~~~~~~~~~~~~~~~

This module implements a Tracker Server for the hybrid chat application.
The tracker maintains a registry of active peers and provides APIs for
peer registration, discovery, and channel management.

Architecture:
- Uses WeApRous framework for RESTful API endpoints
- Stores peer information in memory (can be extended to database)
- Supports peer registration, deregistration, and discovery
- Manages chat channels and channel membership
"""

import argparse
import socket
import json
import time
from datetime import datetime
from daemon.weaprous import WeApRous

# Default port for tracker server
TRACKER_PORT = 7000

# In-memory storage for peers and channels
# Structure: {peer_id: {ip, port, username, last_seen, channels}}
active_peers = {}

# Structure: {channel_name: {creator, created_at, members[], description}}
channels = {}

# Lock for thread-safe operations (if using threading)
import threading
data_lock = threading.Lock()


def get_current_timestamp():
    """Returns current timestamp in ISO format"""
    return datetime.utcnow().isoformat() + 'Z'


def cleanup_inactive_peers(timeout=300):
    """
    Remove peers that haven't sent heartbeat in timeout seconds
    
    :param timeout: Timeout in seconds (default 5 minutes)
    """
    current_time = time.time()
    with data_lock:
        inactive_peers = []
        for peer_id, peer_info in active_peers.items():
            if current_time - peer_info.get('last_seen_ts', 0) > timeout:
                inactive_peers.append(peer_id)
        
        for peer_id in inactive_peers:
            print("[Tracker] Removing inactive peer: {}".format(peer_id))
            del active_peers[peer_id]


# Initialize WeApRous application
app = WeApRous()


@app.route('/register', methods=['POST'])
def register_peer(headers="guest", body="anonymous"):
    """
    Register a new peer with the tracker.
    
    Expected JSON body:
    {
        "peer_id": "unique_peer_identifier",
        "ip": "192.168.1.100",
        "port": 9001,
        "username": "user123"
    }
    
    Response:
    {
        "status": "success",
        "message": "Peer registered successfully",
        "peer_id": "unique_peer_identifier",
        "timestamp": "2025-10-29T10:30:00Z"
    }
    """
    print("[Tracker] Handling peer registration")
    print("[Tracker] Headers: {}".format(headers))
    print("[Tracker] Body: {}".format(body))
    
    try:
        # Parse request body
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
        
        peer_id = data.get('peer_id')
        ip = data.get('ip')
        port = data.get('port')
        username = data.get('username')
        
        # Validate required fields
        if not all([peer_id, ip, port, username]):
            return json.dumps({
                "status": "error",
                "message": "Missing required fields: peer_id, ip, port, username"
            })
        
        # Register peer
        with data_lock:
            active_peers[peer_id] = {
                'ip': ip,
                'port': port,
                'username': username,
                'registered_at': get_current_timestamp(),
                'last_seen': get_current_timestamp(),
                'last_seen_ts': time.time(),
                'channels': []
            }
        
        print("[Tracker] Peer registered: {} ({}:{})".format(username, ip, port))
        
        return json.dumps({
            "status": "success",
            "message": "Peer registered successfully",
            "peer_id": peer_id,
            "timestamp": get_current_timestamp()
        })
        
    except Exception as e:
        print("[Tracker] Error in register: {}".format(e))
        return json.dumps({
            "status": "error",
            "message": "Registration failed: {}".format(str(e))
        })


@app.route('/unregister', methods=['POST'])
def unregister_peer(headers="guest", body="anonymous"):
    """
    Unregister a peer from the tracker.
    
    Expected JSON body:
    {
        "peer_id": "unique_peer_identifier"
    }
    
    Response:
    {
        "status": "success",
        "message": "Peer unregistered successfully"
    }
    """
    print("[Tracker] Handling peer unregistration")
    
    try:
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
        
        peer_id = data.get('peer_id')
        
        if not peer_id:
            return json.dumps({
                "status": "error",
                "message": "Missing peer_id"
            })
        
        with data_lock:
            if peer_id in active_peers:
                username = active_peers[peer_id].get('username', 'unknown')
                del active_peers[peer_id]
                print("[Tracker] Peer unregistered: {}".format(username))
                
                return json.dumps({
                    "status": "success",
                    "message": "Peer unregistered successfully"
                })
            else:
                return json.dumps({
                    "status": "error",
                    "message": "Peer not found"
                })
                
    except Exception as e:
        print("[Tracker] Error in unregister: {}".format(e))
        return json.dumps({
            "status": "error",
            "message": "Unregistration failed: {}".format(str(e))
        })


@app.route('/heartbeat', methods=['POST'])
def heartbeat(headers="guest", body="anonymous"):
    """
    Update peer's last seen timestamp (heartbeat mechanism).
    
    Expected JSON body:
    {
        "peer_id": "unique_peer_identifier"
    }
    
    Response:
    {
        "status": "success",
        "active_peers_count": 5
    }
    """
    try:
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
        
        peer_id = data.get('peer_id')
        
        if not peer_id:
            return json.dumps({
                "status": "error",
                "message": "Missing peer_id"
            })
        
        with data_lock:
            if peer_id in active_peers:
                active_peers[peer_id]['last_seen'] = get_current_timestamp()
                active_peers[peer_id]['last_seen_ts'] = time.time()
                
                return json.dumps({
                    "status": "success",
                    "active_peers_count": len(active_peers)
                })
            else:
                return json.dumps({
                    "status": "error",
                    "message": "Peer not registered"
                })
                
    except Exception as e:
        print("[Tracker] Error in heartbeat: {}".format(e))
        return json.dumps({
            "status": "error",
            "message": "Heartbeat failed: {}".format(str(e))
        })


@app.route('/get-peers', methods=['GET', 'POST'])
def get_peers(headers="guest", body="anonymous"):
    """
    Get list of all active peers.
    
    Optional JSON body (for filtering):
    {
        "peer_id": "requesting_peer_id",
        "channel": "channel_name"  // optional: filter by channel
    }
    
    Response:
    {
        "status": "success",
        "peers": [
            {
                "peer_id": "peer1",
                "ip": "192.168.1.100",
                "port": 9001,
                "username": "user1",
                "channels": ["general", "tech"]
            },
            ...
        ],
        "total_count": 5
    }
    """
    print("[Tracker] Handling get-peers request")
    
    try:
        # Parse body if provided
        channel_filter = None
        requesting_peer = None
        
        if body and body != "anonymous":
            try:
                if isinstance(body, str):
                    data = json.loads(body)
                else:
                    data = body
                channel_filter = data.get('channel')
                requesting_peer = data.get('peer_id')
            except:
                pass
        
        # Clean up inactive peers first
        cleanup_inactive_peers()
        
        with data_lock:
            peer_list = []
            for peer_id, peer_info in active_peers.items():
                # Exclude requesting peer from results
                if peer_id == requesting_peer:
                    continue
                
                # Apply channel filter if specified
                if channel_filter and channel_filter not in peer_info.get('channels', []):
                    continue
                
                peer_list.append({
                    'peer_id': peer_id,
                    'ip': peer_info['ip'],
                    'port': peer_info['port'],
                    'username': peer_info['username'],
                    'channels': peer_info.get('channels', [])
                })
        
        print("[Tracker] Returning {} peers".format(len(peer_list)))
        
        return json.dumps({
            "status": "success",
            "peers": peer_list,
            "total_count": len(peer_list),
            "timestamp": get_current_timestamp()
        })
        
    except Exception as e:
        print("[Tracker] Error in get-peers: {}".format(e))
        return json.dumps({
            "status": "error",
            "message": "Failed to get peers: {}".format(str(e))
        })


@app.route('/create-channel', methods=['POST'])
def create_channel(headers="guest", body="anonymous"):
    """
    Create a new chat channel.
    
    Expected JSON body:
    {
        "peer_id": "creator_peer_id",
        "channel_name": "my-channel",
        "description": "Channel description"
    }
    
    Response:
    {
        "status": "success",
        "channel_name": "my-channel",
        "message": "Channel created successfully"
    }
    """
    print("[Tracker] Handling create-channel request")
    
    try:
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
        
        peer_id = data.get('peer_id')
        channel_name = data.get('channel_name')
        description = data.get('description', '')
        
        if not all([peer_id, channel_name]):
            return json.dumps({
                "status": "error",
                "message": "Missing required fields: peer_id, channel_name"
            })
        
        with data_lock:
            # Check if peer exists
            if peer_id not in active_peers:
                return json.dumps({
                    "status": "error",
                    "message": "Peer not registered"
                })
            
            # Check if channel already exists
            if channel_name in channels:
                return json.dumps({
                    "status": "error",
                    "message": "Channel already exists"
                })
            
            # Create channel
            channels[channel_name] = {
                'creator': peer_id,
                'created_at': get_current_timestamp(),
                'members': [peer_id],
                'description': description
            }
            
            # Add channel to peer's channel list
            if 'channels' not in active_peers[peer_id]:
                active_peers[peer_id]['channels'] = []
            active_peers[peer_id]['channels'].append(channel_name)
        
        print("[Tracker] Channel created: {}".format(channel_name))
        
        return json.dumps({
            "status": "success",
            "channel_name": channel_name,
            "message": "Channel created successfully"
        })
        
    except Exception as e:
        print("[Tracker] Error in create-channel: {}".format(e))
        return json.dumps({
            "status": "error",
            "message": "Channel creation failed: {}".format(str(e))
        })


@app.route('/join-channel', methods=['POST'])
def join_channel(headers="guest", body="anonymous"):
    """
    Join an existing channel.
    
    Expected JSON body:
    {
        "peer_id": "peer_identifier",
        "channel_name": "my-channel"
    }
    
    Response:
    {
        "status": "success",
        "message": "Joined channel successfully",
        "members": ["peer1", "peer2", ...]
    }
    """
    print("[Tracker] Handling join-channel request")
    
    try:
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
        
        peer_id = data.get('peer_id')
        channel_name = data.get('channel_name')
        
        if not all([peer_id, channel_name]):
            return json.dumps({
                "status": "error",
                "message": "Missing required fields: peer_id, channel_name"
            })
        
        with data_lock:
            # Check if peer exists
            if peer_id not in active_peers:
                return json.dumps({
                    "status": "error",
                    "message": "Peer not registered"
                })
            
            # Check if channel exists
            if channel_name not in channels:
                return json.dumps({
                    "status": "error",
                    "message": "Channel does not exist"
                })
            
            # Add peer to channel
            if peer_id not in channels[channel_name]['members']:
                channels[channel_name]['members'].append(peer_id)
            
            # Add channel to peer's channel list
            if 'channels' not in active_peers[peer_id]:
                active_peers[peer_id]['channels'] = []
            if channel_name not in active_peers[peer_id]['channels']:
                active_peers[peer_id]['channels'].append(channel_name)
            
            members = channels[channel_name]['members']
        
        print("[Tracker] Peer {} joined channel {}".format(peer_id, channel_name))
        
        return json.dumps({
            "status": "success",
            "message": "Joined channel successfully",
            "channel_name": channel_name,
            "members": members
        })
        
    except Exception as e:
        print("[Tracker] Error in join-channel: {}".format(e))
        return json.dumps({
            "status": "error",
            "message": "Join channel failed: {}".format(str(e))
        })


@app.route('/leave-channel', methods=['POST'])
def leave_channel(headers="guest", body="anonymous"):
    """
    Leave a channel.
    
    Expected JSON body:
    {
        "peer_id": "peer_identifier",
        "channel_name": "my-channel"
    }
    """
    print("[Tracker] Handling leave-channel request")
    
    try:
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
        
        peer_id = data.get('peer_id')
        channel_name = data.get('channel_name')
        
        if not all([peer_id, channel_name]):
            return json.dumps({
                "status": "error",
                "message": "Missing required fields: peer_id, channel_name"
            })
        
        with data_lock:
            # Remove peer from channel
            if channel_name in channels:
                if peer_id in channels[channel_name]['members']:
                    channels[channel_name]['members'].remove(peer_id)
            
            # Remove channel from peer's list
            if peer_id in active_peers:
                if channel_name in active_peers[peer_id].get('channels', []):
                    active_peers[peer_id]['channels'].remove(channel_name)
        
        print("[Tracker] Peer {} left channel {}".format(peer_id, channel_name))
        
        return json.dumps({
            "status": "success",
            "message": "Left channel successfully"
        })
        
    except Exception as e:
        print("[Tracker] Error in leave-channel: {}".format(e))
        return json.dumps({
            "status": "error",
            "message": "Leave channel failed: {}".format(str(e))
        })


@app.route('/list-channels', methods=['GET', 'POST'])
def list_channels(headers="guest", body="anonymous"):
    """
    Get list of all available channels.
    
    Response:
    {
        "status": "success",
        "channels": [
            {
                "name": "general",
                "description": "General chat",
                "member_count": 5,
                "created_at": "2025-10-29T10:00:00Z"
            },
            ...
        ]
    }
    """
    print("[Tracker] Handling list-channels request")
    
    try:
        with data_lock:
            channel_list = []
            for name, info in channels.items():
                channel_list.append({
                    'name': name,
                    'description': info.get('description', ''),
                    'member_count': len(info.get('members', [])),
                    'created_at': info.get('created_at', '')
                })
        
        return json.dumps({
            "status": "success",
            "channels": channel_list,
            "total_count": len(channel_list)
        })
        
    except Exception as e:
        print("[Tracker] Error in list-channels: {}".format(e))
        return json.dumps({
            "status": "error",
            "message": "Failed to list channels: {}".format(str(e))
        })


@app.route('/status', methods=['GET'])
def server_status(headers="guest", body="anonymous"):
    """
    Get tracker server status and statistics.
    
    Response:
    {
        "status": "online",
        "active_peers": 10,
        "total_channels": 3,
        "uptime": "5 hours",
        "version": "1.0"
    }
    """
    with data_lock:
        return json.dumps({
            "status": "online",
            "active_peers": len(active_peers),
            "total_channels": len(channels),
            "version": "1.0",
            "timestamp": get_current_timestamp()
        })


# Main entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='TrackerServer',
        description='Tracker Server for Hybrid Chat Application',
        epilog='Part of CO3093/CO3094 Computer Network Assignment'
    )
    parser.add_argument('--server-ip', default='0.0.0.0', 
                       help='IP address to bind (default: 0.0.0.0)')
    parser.add_argument('--server-port', type=int, default=TRACKER_PORT,
                       help='Port number to listen on (default: 7000)')
    
    args = parser.parse_args()
    
    ip = args.server_ip
    port = args.server_port
    
    print("=" * 60)
    print("Tracker Server for Hybrid Chat Application")
    print("=" * 60)
    print("Server IP: {}".format(ip))
    print("Server Port: {}".format(port))
    print("=" * 60)
    print("\nAvailable API Endpoints:")
    print("  POST   /register       - Register a new peer")
    print("  POST   /unregister     - Unregister a peer")
    print("  POST   /heartbeat      - Update peer heartbeat")
    print("  GET    /get-peers      - Get list of active peers")
    print("  POST   /create-channel - Create a new channel")
    print("  POST   /join-channel   - Join an existing channel")
    print("  POST   /leave-channel  - Leave a channel")
    print("  GET    /list-channels  - List all channels")
    print("  GET    /status         - Get server status")
    print("=" * 60)
    print("\nStarting server...\n")
    
    # Prepare and run the application
    app.prepare_address(ip, port)
    app.run()