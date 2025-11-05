#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course.
#
# WeApRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#

"""
tracker_server
~~~~~~~~~~~~~~~

Tracker server module implementing the Client-Server paradigm for chat application.
Provides APIs for peer registration, discovery, and connection management.
"""

from peer_manager import PeerManager
import json


# Global peer manager instance
peer_manager = PeerManager(peer_timeout=300)


# API 1: POST /login - Peer authentication
def login(headers="guest", body="anonymous"):
    """
    Handle peer login/authentication.
    
    :param headers: Request headers (dict).
    :param body: Request body (can be dict if JSON, or string).
    
    :rtype dict: JSON response with status and peer_id.
    """
    print("[TrackerServer] POST /login - Peer authentication")
    
    try:
        # Parse JSON body if string
        if isinstance(body, str):
            try:
                body_data = json.loads(body)
            except json.JSONDecodeError:
                body_data = {}
        else:
            body_data = body
        
        peer_id = body_data.get('peer_id', '')
        password = body_data.get('password', '')
        
        if not peer_id:
            return {
                "status": "error",
                "message": "peer_id is required"
            }, 400, "Bad Request"
        
        # Authenticate peer
        if peer_manager.authenticate_peer(peer_id, password):
            print("[TrackerServer] Peer {} authenticated successfully".format(peer_id))
            return {
                "status": "success",
                "message": "Login successful",
                "peer_id": peer_id
            }, 200, "OK"
        else:
            print("[TrackerServer] Peer {} authentication failed".format(peer_id))
            return {
                "status": "error",
                "message": "Authentication failed"
            }, 401, "Unauthorized"
            
    except Exception as e:
        print("[TrackerServer] Error in login: {}".format(e))
        return {
            "status": "error",
            "message": "Internal server error: {}".format(str(e))
        }, 500, "Internal Server Error"


# API 2: POST /submit-info - Peer registration
def submit_info(headers="guest", body="anonymous"):
    """
    Handle peer registration - submit IP and port to tracker.
    
    :param headers: Request headers (dict).
    :param body: Request body (can be dict if JSON, or string).
    
    :rtype dict: JSON response with status.
    """
    print("[TrackerServer] POST /submit-info - Peer registration")
    
    try:
        # Parse JSON body if string
        if isinstance(body, str):
            try:
                body_data = json.loads(body)
            except json.JSONDecodeError:
                body_data = {}
        else:
            body_data = body
        
        peer_id = body_data.get('peer_id', '')
        ip = body_data.get('ip', '')
        port = body_data.get('port', '')
        metadata = body_data.get('metadata', {})
        
        # Validate required fields
        if not peer_id:
            return {
                "status": "error",
                "message": "peer_id is required"
            }, 400, "Bad Request"
        
        if not ip:
            return {
                "status": "error",
                "message": "ip is required"
            }, 400, "Bad Request"
        
        if not port:
            return {
                "status": "error",
                "message": "port is required"
            }, 400, "Bad Request"
        
        # Convert port to int if string
        try:
            port = int(port)
        except (ValueError, TypeError):
            return {
                "status": "error",
                "message": "port must be a valid integer"
            }, 400, "Bad Request"
        
        # Register peer
        success = peer_manager.register_peer(peer_id, ip, port, metadata)
        
        if success:
            print("[TrackerServer] Peer {} registered at {}:{}".format(peer_id, ip, port))
            return {
                "status": "success",
                "message": "Peer registered successfully",
                "peer_id": peer_id,
                "ip": ip,
                "port": port
            }, 200, "OK"
        else:
            return {
                "status": "error",
                "message": "Failed to register peer"
            }, 500, "Internal Server Error"
            
    except Exception as e:
        print("[TrackerServer] Error in submit_info: {}".format(e))
        return {
            "status": "error",
            "message": "Internal server error: {}".format(str(e))
        }, 500, "Internal Server Error"


# API 3: GET /get-list - Get active peers list
def get_list(headers="guest", body="anonymous"):
    """
    Get list of all active peers.
    
    :param headers: Request headers (dict).
    :param body: Request body (can be dict if JSON, or string).
    
    :rtype dict: JSON response with list of peers.
    """
    print("[TrackerServer] GET /get-list - Get active peers list")
    
    try:
        # Parse body to get optional exclude_id

        channel = None
        if isinstance(body, str) and body and body != "anonymous":
            try:
                body_data = json.loads(body)
                channel = body_data.get('channel')
            except json.JSONDecodeError:
                pass
        elif isinstance(body, dict):
            channel = body.get('channel')
        exclude_id = None        
        if channel:
            print(f"[TrackerServer] Return all peers in channel: {channel}")
            requesting_peer_id = body.get('peer_id')
            peers_list = peer_manager.get_peers_in_channel(channel, exclude_id=requesting_peer_id)
        else:
            peers_list = peer_manager.get_all_peers(exclude_id=exclude_id)
            print("[TrackerServer] Returning {} active peers".format(len(peers_list)))
        # Get all active peers
        
        
        return {
            "status": "success",
            "message": "Retrieved peer list successfully",
            "count": len(peers_list),
            "peers": peers_list
        }, 200, "OK"
        
    except Exception as e:
        print("[TrackerServer] Error in get_list: {}".format(e))
        return {
            "status": "error",
            "message": "Internal server error: {}".format(str(e))
        }, 500, "Internal Server Error"


# API 4: POST /add-list - Add peer to list
def add_list(headers="guest", body="anonymous"):
    """
    Add a peer to the active list.
    
    :param headers: Request headers (dict).
    :param body: Request body (can be dict if JSON, or string).
    
    :rtype dict: JSON response with status.
    """
    print("[TrackerServer] POST /add-list - Add peer to list")
    
    try:
        # Parse JSON body if string
        if isinstance(body, str):
            try:
                body_data = json.loads(body)
            except json.JSONDecodeError:
                body_data = {}
        else:
            body_data = body
        
        peer_id = body_data.get('peer_id', '')
        channel = body_data.get('channel', '')
        if peer_id and channel:
            print(f"[TrackerServer]... processing Join Channel for {peer_id} into {channel}")
            joined = peer_manager.join_channel(peer_id, channel)
            if joined:
                print(f"[TrackerServer] Peer {peer_id} joined channel {channel}")
                return {
                    "status": "success",
                    "message": f"Peer {peer_id} joined channel {channel}",
                    "peer_id": peer_id,
                    "channel": channel
                }, 200, "OK"
            else:
                return {
                    "status": "error",
                    "message": f"Peer '{peer_id}' couldn't join channel '{channel}'",
                }, 404, "Not Found"
        elif peer_id:
            
            success = peer_manager.add_peer_to_list(peer_id)
            
            if success:
                print(f"[TrackerServer] Peer {peer_id} added to active list.")
                return {
                    "status": "success",
                    "message": "Peer added to list successfully (pinged)",
                    "peer_id": peer_id
                }, 200, "OK"
            else:
                return {
                    "status": "error",
                    "message": "Peer not found. Register peer first using /submit-info"
                }, 404, "Not Found"
        else:
            return {
                "status": "error",
                "message": "peer_id is required"
            }, 400, "Bad Request"
            
    except Exception as e:
        print("[TrackerServer] Error in add_list: {}".format(e))
        return {
            "status": "error",
            "message": "Internal server error: {}".format(str(e))
        }, 500, "Internal Server Error"


# API 5: POST /connect-peer - Initiate P2P connection
def connect_peer(headers="guest", body="anonymous"):
    """
    Initiate P2P connection between peers.
    Returns target peer information for direct connection.
    
    :param headers: Request headers (dict).
    :param body: Request body (can be dict if JSON, or string).
    
    :rtype dict: JSON response with target peer info.
    """
    print("[TrackerServer] POST /connect-peer - Initiate P2P connection")
    
    try:
        # Parse JSON body if string
        if isinstance(body, str):
            try:
                body_data = json.loads(body)
            except json.JSONDecodeError:
                body_data = {}
        else:
            body_data = body
        
        from_peer_id = body_data.get('from_peer_id', '')
        to_peer_id = body_data.get('to_peer_id', '')
        
        if not from_peer_id:
            return {
                "status": "error",
                "message": "from_peer_id is required"
            }, 400, "Bad Request"
        
        if not to_peer_id:
            return {
                "status": "error",
                "message": "to_peer_id is required"
            }, 400, "Bad Request"
        
        # Get target peer information
        target_peer = peer_manager.get_peer(to_peer_id)
        
        if not target_peer:
            return {
                "status": "error",
                "message": "Target peer not found"
            }, 404, "Not Found"
        
        if target_peer['status'] != 'active':
            return {
                "status": "error",
                "message": "Target peer is not active"
            }, 400, "Bad Request"
        
        print("[TrackerServer] Connection from {} to {} initiated".format(from_peer_id, to_peer_id))
        
        # Return target peer connection info
        return {
            "status": "success",
            "message": "Connection information retrieved",
            "target_peer": {
                "peer_id": target_peer['peer_id'],
                "ip": target_peer['ip'],
                "port": target_peer['port'],
                "metadata": target_peer.get('metadata', {})
            }
        }, 200, "OK"
        
    except Exception as e:
        print("[TrackerServer] Error in connect_peer: {}".format(e))
        return {
            "status": "error",
            "message": "Internal server error: {}".format(str(e))
        }, 500, "Internal Server Error"


# API 6: POST /broadcast-peer - Broadcast message to all peers
def broadcast_peer(headers="guest", body="anonymous"):
    """
    Handle broadcast message request.
    Returns list of peers for the sender to broadcast message to.
    
    :param headers: Request headers (dict).
    :param body: Request body (can be dict if JSON, or string).
    
    :rtype dict: JSON response with list of target peers.
    """
    print("[TrackerServer] POST /broadcast-peer - Broadcast message request")
    
    try:
        # Parse JSON body if string
        if isinstance(body, str):
            try:
                body_data = json.loads(body)
            except json.JSONDecodeError:
                body_data = {}
        else:
            body_data = body
        
        sender_peer_id = body_data.get('sender_peer_id', '')
        channel = body_data.get('channel', None)
        message = body_data.get('message', {})
        
        if not sender_peer_id:
            return {
                "status": "error",
                "message": "sender_peer_id is required"
            }, 400, "Bad Request"
        
        # Verify sender exists
        sender_peer = peer_manager.get_peer(sender_peer_id)
        if not sender_peer:
            return {
                "status": "error",
                "message": "Sender peer not found. Register peer first using /submit-info"
            }, 404, "Not Found"
        
        # Get target peers based on channel or all peers
        if channel:
            print("[TrackerServer] Broadcasting to peers in channel: {}".format(channel))
            target_peers = peer_manager.get_peers_in_channel(channel, exclude_id=sender_peer_id)
        else:
            print("[TrackerServer] Broadcasting to all active peers")
            target_peers = peer_manager.get_all_peers(exclude_id=sender_peer_id)
        
        print("[TrackerServer] Found {} target peers for broadcast from {}".format(len(target_peers), sender_peer_id))
        
        # Return list of target peers for client to broadcast directly
        return {
            "status": "success",
            "message": "Broadcast targets retrieved successfully",
            "sender_peer_id": sender_peer_id,
            "channel": channel,
            "count": len(target_peers),
            "target_peers": target_peers,
            "message_data": message
        }, 200, "OK"
        
    except Exception as e:
        print("[TrackerServer] Error in broadcast_peer: {}".format(e))
        return {
            "status": "error",
            "message": "Internal server error: {}".format(str(e))
        }, 500, "Internal Server Error"


# API 7: POST /send-peer - Send message to specific peer
def send_peer(headers="guest", body="anonymous"):
    """
    Handle send message to specific peer request.
    Returns target peer information for direct P2P message sending.
    
    :param headers: Request headers (dict).
    :param body: Request body (can be dict if JSON, or string).
    
    :rtype dict: JSON response with target peer info.
    """
    print("[TrackerServer] POST /send-peer - Send message to peer request")
    
    try:
        # Parse JSON body if string
        if isinstance(body, str):
            try:
                body_data = json.loads(body)
            except json.JSONDecodeError:
                body_data = {}
        else:
            body_data = body
        
        from_peer_id = body_data.get('from_peer_id', '')
        to_peer_id = body_data.get('to_peer_id', '')
        message = body_data.get('message', {})
        
        if not from_peer_id:
            return {
                "status": "error",
                "message": "from_peer_id is required"
            }, 400, "Bad Request"
        
        if not to_peer_id:
            return {
                "status": "error",
                "message": "to_peer_id is required"
            }, 400, "Bad Request"
        
        # Verify sender exists
        sender_peer = peer_manager.get_peer(from_peer_id)
        if not sender_peer:
            return {
                "status": "error",
                "message": "Sender peer not found. Register peer first using /submit-info"
            }, 404, "Not Found"
        
        # Get target peer information
        target_peer = peer_manager.get_peer(to_peer_id)
        
        if not target_peer:
            return {
                "status": "error",
                "message": "Target peer not found"
            }, 404, "Not Found"
        
        if target_peer['status'] != 'active':
            return {
                "status": "error",
                "message": "Target peer is not active"
            }, 400, "Bad Request"
        
        print("[TrackerServer] Message from {} to {} prepared".format(from_peer_id, to_peer_id))
        
        # Return target peer connection info for direct P2P sending
        return {
            "status": "success",
            "message": "Target peer information retrieved",
            "from_peer_id": from_peer_id,
            "target_peer": {
                "peer_id": target_peer['peer_id'],
                "ip": target_peer['ip'],
                "port": target_peer['port'],
                "metadata": target_peer.get('metadata', {})
            },
            "message_data": message
        }, 200, "OK"
        
    except Exception as e:
        print("[TrackerServer] Error in send_peer: {}".format(e))
        return {
            "status": "error",
            "message": "Internal server error: {}".format(str(e))
        }, 500, "Internal Server Error"

