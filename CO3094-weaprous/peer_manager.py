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
peer_manager
~~~~~~~~~~~~~

Thread-safe peer management module for tracking active peers in the chat application.
"""

import threading
import time
from typing import Dict, List, Optional, Set


class PeerManager:
    """
    Thread-safe peer manager for tracking active peers.
    
    Manages peer registration, tracking, and connection information in a thread-safe manner.
    Uses in-memory storage for peer data.
    
    Attributes:
        peers (dict): Dictionary mapping peer_id to peer info.
        lock (threading.Lock): Lock for thread-safe operations.
        peer_timeout (int): Timeout in seconds for peer inactivity (default: 300).
    """
    
    def __init__(self, peer_timeout=300):
        """
        Initialize the PeerManager.
        
        :param peer_timeout (int): Timeout in seconds before considering peer inactive (default: 300).
        """
        self.peers: Dict[str, dict] = {}
        self.lock = threading.Lock()
        self.peer_timeout = peer_timeout
        #Channel support
        self.channels: Dict[str, Set[str]] = {}

    def register_peer(self, peer_id: str, ip: str, port: int, metadata: dict = None) -> bool:
        """
        Register a new peer or update existing peer information.
        
        :param peer_id (str): Unique identifier for the peer.
        :param ip (str): IP address of the peer.
        :param port (int): Port number of the peer.
        :param metadata (dict): Optional metadata about the peer.
        
        :rtype bool: True if successful, False otherwise.
        """
        try:
            with self.lock:
                self.peers[peer_id] = {
                    'peer_id': peer_id,
                    'ip': ip,
                    'port': port,
                    'last_seen': time.time(),
                    'metadata': metadata or {},
                    'status': 'active'
                }
                print("[PeerManager] Registered peer: {} at {}:{}".format(peer_id, ip, port))
                return True
        except Exception as e:
            print("[PeerManager] Error registering peer {}: {}".format(peer_id, e))
            return False
    
    def get_peer(self, peer_id: str) -> Optional[dict]:
        """
        Get information about a specific peer.
        
        :param peer_id (str): Unique identifier for the peer.
        
        :rtype dict: Peer information or None if not found.
        """
        with self.lock:
            peer = self.peers.get(peer_id)
            if peer:
                # Update last_seen timestamp
                peer['last_seen'] = time.time()
            return peer.copy() if peer else None
    
    def get_all_peers(self, exclude_id: str = None) -> List[dict]:
        """
        Get list of all active peers.
        
        :param exclude_id (str): Optional peer_id to exclude from the list.
        
        :rtype list: List of peer dictionaries.
        """
        with self.lock:
            # Remove inactive peers
            self._cleanup_inactive_peers()
            
            peers_list = []
            for peer_id, peer_info in self.peers.items():
                if peer_info['status'] == 'active':
                    if exclude_id is None or peer_id != exclude_id:
                        peer_copy = peer_info.copy()
                        # Remove sensitive internal data
                        peer_copy.pop('last_seen', None)
                        peers_list.append(peer_copy)
            
            return peers_list
    
    def add_peer_to_list(self, peer_id: str) -> bool:
        """
        Add a peer to the active list (marks as active).
        
        :param peer_id (str): Unique identifier for the peer.
        
        :rtype bool: True if successful, False if peer not found.
        """
        with self.lock:
            if peer_id in self.peers:
                self.peers[peer_id]['status'] = 'active'
                self.peers[peer_id]['last_seen'] = time.time()
                print("[PeerManager] Added peer {} to active list".format(peer_id))
                return True
            return False
    
    def join_channel(self, peer_id: str, channel: str) -> bool:
        """
        Add a peer to a channel.
        Automatically creates the channel if it doesn't exist.
        
        :param peer_id (str): The peer (username) joining.
        :param channel (str): The channel to join.
        :rtype: bool: True if successful, False if peer not registered.
        """
        with self.lock:
            if peer_id not in self.peers:
                print(f"[PeerManager] Error: Peer {peer_id} does not exist.")
                return False
                
            if channel not in self.channels:
                self.channels[channel] = set()
                
            self.channels[channel].add(peer_id)
            self.peers[peer_id]['last_seen'] = time.time()
            print(f"[PeerManager] Peer {peer_id} joined channel {channel}")
            return True

    def get_peers_in_channel(self, channel: str, exclude_id: str = None) -> List[dict]:
        """
        Get the info list (IP, port) of peers in a specific channel.
        
        :param channel (str): The channel name.
        :param exclude_id (str, optional): Peer ID to exclude (the asker).
        :rtype: list: List of peer info dictionaries.
        """
        with self.lock:
            self._cleanup_inactive_peers()
            
            peer_ids_in_channel = self.channels.get(channel, set())
            
            if not peer_ids_in_channel:
                return [] 
            
            channel_peers_info = []
            for peer_id in peer_ids_in_channel:
                if peer_id == exclude_id:
                    continue
                    
                peer_info = self.peers.get(peer_id)
                if peer_info and peer_info['status'] == 'active':
                    peer_copy = peer_info.copy()
                    peer_copy.pop('last_seen', None)
                    peer_copy["username"] = peer_copy.get("peer_id") 
                    channel_peers_info.append(peer_copy)
            
            return channel_peers_info

    def remove_peer(self, peer_id: str) -> bool:
        """
        Remove a peer from tracking.
        
        :param peer_id (str): Unique identifier for the peer.
        
        :rtype bool: True if successful, False if peer not found.
        """
        with self.lock:
            if peer_id in self.peers:
                del self.peers[peer_id]
                for peer_set in self.channels.values():
                    peer_set.discard(peer_id)
                print("[PeerManager] Removed peer: {}".format(peer_id))
                return True
            return False
    
    def update_peer_status(self, peer_id: str, status: str) -> bool:
        """
        Update peer status.
        
        :param peer_id (str): Unique identifier for the peer.
        :param status (str): New status ('active', 'inactive', etc.).
        
        :rtype bool: True if successful, False if peer not found.
        """
        with self.lock:
            if peer_id in self.peers:
                self.peers[peer_id]['status'] = status
                self.peers[peer_id]['last_seen'] = time.time()
                return True
            return False
    
    def _cleanup_inactive_peers(self):
        """
        Remove peers that haven't been seen for a while.
        Internal method called automatically.
        """
        current_time = time.time()
        to_remove = []
        
        for peer_id, peer_info in self.peers.items():
            if current_time - peer_info['last_seen'] > self.peer_timeout:
                to_remove.append(peer_id)
        
        for peer_id in to_remove:
            print("[PeerManager] Removing inactive peer: {}".format(peer_id))
            del self.peers[peer_id]
            for peer_set in self.channels.values():
                peer_set.discard(peer_id)
    def get_peer_count(self) -> int:
        """
        Get total number of active peers.
        
        :rtype int: Number of active peers.
        """
        with self.lock:
            self._cleanup_inactive_peers()
            return len([p for p in self.peers.values() if p['status'] == 'active'])
    
    def authenticate_peer(self, peer_id: str, password: str = None) -> bool:
        """
        Authenticate a peer (simple authentication).
        
        :param peer_id (str): Unique identifier for the peer.
        :param password (str): Optional password for authentication.
        
        :rtype bool: True if authenticated, False otherwise.
        """
        # Simple authentication - can be extended
        # For now, accept any peer_id
        return True

