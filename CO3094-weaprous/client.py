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
client_new
~~~~~~~~~~

This module implements the P2P chat client for the CO3093/CO3094 course.
It features a 2-layer architecture:
1. ConnectionManager (Engine): Handles all low-level socket and threading.
2. ChatApp (Brain): Handles all business logic (channels, DMs, API calls).
The main() function provides a command-line interface (CLI) for user interaction.
"""

import socket
import json
import threading
import time
import queue
import getpass
import sys
from datetime import datetime
import argparse
# ^^--------------------------------------------------------------------^^#
# ^^====================================================================^^#

# --- [1. CONFIGURATION & GLOBAL FUNCTIONS] ---
g_ui_queue = queue.Queue()  # Queue for the User Interface (UI)
g_my_username = "Me"

# Color class for terminal output
class bcolors:
    """(Helper) ANSI escape codes for colored terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# --- [2. TECHNICAL LAYER (ENGINE)] ---

class ConnectionManager:
    """
    The "Engine" layer. This class ONLY manages sockets, connections, and threads.
    It is "dumb" and knows nothing about "channels" or "chat logic".
    It communicates with the "Brain" (ChatApp) via an event_queue.

    :ivar username (str): The username of this client.
    :ivar event_queue (queue.Queue): The internal queue to report events to ChatApp.
    :ivar peers (dict): Thread-safe dictionary mapping {username: socket}.
    :ivar peer_lock (threading.Lock): Lock for managing the peers dictionary.
    :ivar listening_socket (socket.socket): The main server socket.
    :ivar running (bool): Flag to control all threads.
    """
    def __init__(self, username, event_queue):
        """
        Initialize a new ConnectionManager instance.

        :param username (str): The username of this client.
        :param event_queue (queue.Queue): The internal queue to report events to ChatApp.
        """
        self.username = username
        self.event_queue = event_queue  

        self.peers = {}  
        self.peer_lock = threading.Lock()
        self.listening_socket = None
        self.running = False

    def start_listener(self, node_ip, node_port):
        """
        Starts listening for incoming P2P connections.

        :param node_ip (str): The IP address to bind to.
        :param node_port (int): The port to listen on.
        """
        self.running = True
        try:
            self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listening_socket.bind((node_ip, node_port))
            self.listening_socket.listen(10)

            # Send to ChatApp, which will send to UI
            self.event_queue.put(("log", "info", f"[Engine] Listening for P2P on {node_ip}:{node_port}"))

            listen_thread = threading.Thread(target=self._listen_loop)
            listen_thread.daemon = True
            listen_thread.start()
        except Exception as e:
            self.event_queue.put(("log", "error", f"[Engine] Critical P2P server error: {e}"))

    def _listen_loop(self):
        """Connection acceptance loop (accept). Runs in a dedicated thread."""
        while self.running:
            try:
                self.listening_socket.settimeout(1.0)
                conn, addr = self.listening_socket.accept()

                handler_thread = threading.Thread(target=self._handle_incoming_handshake, args=(conn, addr))
                handler_thread.daemon = True
                handler_thread.start()
            except socket.timeout:
                continue 
            except Exception as e:
                if self.running:
                    self.event_queue.put(("log", "error", f"[Engine] Error accepting connection: {e}"))

    def _handle_incoming_handshake(self, conn, addr):
        """
        Handle INCOMING (Passive) connection.
        Performs the 'identify' handshake.

        :param conn (socket.socket): The new connection socket.
        :param addr (tuple): The address (ip, port) of the incoming peer.
        """
        peer_username = "unknown"
        try:
            data = conn.recv(4096).decode('utf-8')
            if not data:
                conn.close()
                return

            message = json.loads(data)
            if message.get("command") == "identify":
                peer_username = message.get("sender", "unknown")

                with self.peer_lock:
                    self.peers[peer_username] = conn

                response = {"command": "identify", "sender": self.username}
                conn.sendall(json.dumps(response).encode('utf-8'))

                self.event_queue.put(("connected", peer_username, addr))

                self._start_message_stream(conn, peer_username)
            else:
                conn.close()  
        except Exception as e:
            self.event_queue.put(("log", "error", f"[Engine] Handshake error from {addr}: {e}"))
            try:
                conn.close()
            except:
                pass

    def initiate_connection(self, peer_username, peer_ip, peer_port):
        """
        Actively initiate OUTGOING connection to a peer.

        :param peer_username (str): The username of the peer to connect to.
        :param peer_ip (str): The IP address of the peer.
        :param peer_port (int): The port of the peer.
        """
        if peer_username == self.username:
            return  # Don't connect yourself
        with self.peer_lock:
            if peer_username in self.peers:
                return  # Already connected

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((peer_ip, peer_port))

            # Send "identify" 
            identify_msg = {"command": "identify", "sender": self.username}
            sock.sendall(json.dumps(identify_msg).encode('utf-8'))

            # Wait for "identify" response
            response_data = json.loads(sock.recv(4096).decode('utf-8'))

            if response_data.get("command") == "identify":
                with self.peer_lock:
                    self.peers[peer_username] = sock

                self.event_queue.put(("connected", peer_username, (peer_ip, peer_port)))

                # Start the message listening thread
                self._start_message_stream(sock, peer_username)
            else:
                sock.close() 
        except Exception as e:
            self.event_queue.put(("log", "error", f"[Engine] Cannot connect to {peer_username}: {e}"))

    def _start_message_stream(self, conn, peer_username):
        """
        Start the recv() thread for a peer.

        :param conn (socket.socket): The peer's connection socket.
        :param peer_username (str): The username of the peer.
        """
        stream_thread = threading.Thread(target=self._stream_peer_messages, args=(conn, peer_username))
        stream_thread.daemon = True
        stream_thread.start()

    def _stream_peer_messages(self, conn, peer_username):
        """
        Message recv() loop. Runs in a dedicated thread per peer.

        :param conn (socket.socket): The peer's connection socket.
        :param peer_username (str): The username of the peer.
        """
        try:
            while self.running:
                data = conn.recv(4096).decode('utf-8')
                if not data:
                    break  # Peer disconnected

                message = json.loads(data)
                # Push raw data up to ChatApp for processing
                self.event_queue.put(("message", peer_username, message))

        except Exception as e:
            pass  

        finally:
            with self.peer_lock:
                if peer_username in self.peers:
                    del self.peers[peer_username]
            try:
                conn.close()
            except:
                pass

            self.event_queue.put(("disconnected", peer_username, None))

    def send_message_to_peer(self, peer_username, data):
        """
        Send JSON data to a specific peer.

        :param peer_username (str): The username of the target peer.
        :param data (dict): The JSON (dict) to send.
        :rtype: bool: True if send was successful, False otherwise.
        """
        try:
            with self.peer_lock:
                conn = self.peers.get(peer_username)
            if conn:
                conn.sendall(json.dumps(data).encode('utf-8'))
                return True
        except Exception:
            return False  
        return False

    def broadcast_message(self, data):
        """
        Send JSON data to ALL connected peers.

        :param data (dict): The JSON (dict) to send.
        """
        with self.peer_lock:
            all_connections = list(self.peers.values())

        for conn in all_connections:
            try:
                conn.sendall(json.dumps(data).encode('utf-8'))
            except Exception:
                pass  

    def stop(self):
        """Stop all threads and sockets gracefully."""
        self.running = False
        with self.peer_lock:
            for conn in self.peers.values():
                try:
                    conn.close()
                except:
                    pass
        if self.listening_socket:
            try:
                self.listening_socket.close()
            except:
                pass


# --- [3. BUSINESS LOGIC LAYER (BRAIN)] ---

class ChatApp:
    """
    This class is the "Brain", handling chat logic.
    It owns the ConnectionManager and communicates with the UI Queue.
    It knows about "channels", "DMs", and "public" chat.

    :ivar username (str): The client's username.
    :ivar node_ip (str): The IP this client will listen on.
    :ivar node_port (int): The Port this client will listen on.
    :ivar tracker_addr (tuple): (ip, port) of the Tracker Server.
    :ivar ui_queue (queue.Queue): The queue to send messages to the UI.
    :ivar internal_event_queue (queue.Queue): Queue for Engine -> Brain events.
    :ivar manager (ConnectionManager): The socket management instance.
    :ivar channels (list): List of channels this client has joined.
    :ivar my_cookie (str): The auth cookie from the login server.
    :ivar running (bool): Flag to control all threads.
    """
    def __init__(self, username, node_ip, node_port, tracker_addr, ui_queue):
        """
        Initialize a new ChatApp instance.

        :param username (str): The client's username.
        :param node_ip (str): The IP this client will listen on.
        :param node_port (int): The Port this client will listen on.
        :param tracker_addr (tuple): (ip, port) of the Tracker Server.
        :param ui_queue (queue.Queue): The queue to send messages to the UI.
        """
        self.username = username
        self.node_ip = node_ip
        self.node_port = node_port
        self.tracker_addr = tracker_addr
        self.ui_queue = ui_queue  # UI Queue 

        self.internal_event_queue = queue.Queue() 
        self.manager = ConnectionManager(username, self.internal_event_queue)

        self.channels = []
        self.my_cookie = None
        self.running = False

    def start(self, user_cookie):
        """
        Start the ChatApp.

        :param user_cookie (str): The auth cookie received from login.
        """
        self.running = True
        self.my_cookie = user_cookie

        # 1. Start the Technical Layer
        self.manager.start_listener(self.node_ip, self.node_port)

        # 2. Start the Event Processing Thread 
        event_thread = threading.Thread(target=self._process_events)
        event_thread.daemon = True
        event_thread.start()

        # 3. Register with Tracker
        self.register_with_tracker()

    def stop(self):
        """Stop the ChatApp and its ConnectionManager."""
        self.running = False
        self.manager.stop()
        self.ui_queue.put("[App] Stopped.")

    def _process_events(self):
        """Event processing loop from ConnectionManager. Runs in a thread."""
        while self.running:
            try:
                event_type, username, data = self.internal_event_queue.get(timeout=1.0)

                if event_type == "log":
                    log_level = username
                    log_message = data
                    self.ui_queue.put(log_message)

                elif event_type == "connected":
                    addr = data
                    self.ui_queue.put(f"{bcolors.OKGREEN}[App] P2P connection successful with {username}{bcolors.ENDC}")

                elif event_type == "disconnected":
                    self.ui_queue.put(f"{bcolors.WARNING}[App] Lost P2P connection with {username}{bcolors.ENDC}")

                elif event_type == "message":
                    self._dispatch_p2p_message(data)

            except queue.Empty:
                continue

    def _dispatch_p2p_message(self, message):
        """
        Process message logic based on 'command'.

        :param message (dict): The message object (JSON) received from a peer.
        """
        command = message.get("command", "")
        sender = message.get("sender", "unknown")
        payload = message.get("payload", "")
        channel_name = message.get("channel", "unknown")

        if command == "dm":
            formatted_msg = f"{bcolors.WARNING}(Private) {sender}{bcolors.ENDC}: {payload}"
            self.ui_queue.put(formatted_msg)
        elif command == "public":
            formatted_msg = f"{bcolors.OKGREEN}{sender}{bcolors.ENDC}: {payload}"
            self.ui_queue.put(formatted_msg)
        elif command == "channel":
            formatted_msg = f"{bcolors.HEADER}(Channel {channel_name}) {sender}{bcolors.ENDC}: {payload}"
            self.ui_queue.put(formatted_msg)

    # --- UI Command Handlers ---

    def handle_ui_command(self, cmd):
        """
        Main function to handle user input from the UI.

        :param cmd (str): The raw command string from user input.
        """
        if cmd.startswith('/subscribe '):
            channel = cmd.split(' ', 1)[1]
            self.subscribe_to_channel(channel)

        elif cmd.startswith('/channel '):
            parts = cmd.split(' ', 2)
            if len(parts) < 3:
                self.ui_queue.put(f"{bcolors.FAIL}[System] Error: /channel <channel> <message>{bcolors.ENDC}")
            else:
                self._do_send_channel(parts[1], parts[2])

        elif cmd.startswith('/dm '):
            parts = cmd.split(' ', 2)
            if len(parts) < 3:
                self.ui_queue.put(f"{bcolors.FAIL}[System] Error: /dm <username> <message>{bcolors.ENDC}")
            else:
                self._do_send_dm(parts[1], parts[2])

        elif cmd == '/channels':
            self.ui_queue.put(f"{bcolors.OKGREEN}[System] Joined channels: {self.channels}{bcolors.ENDC}")

        else:
            # Default is Public
            self._do_send_public(cmd)

    def _do_send_dm(self, peer_username, message_payload):
        """
        Build and Send 1-1 message.

        :param peer_username (str): The target user's name.
        :param message_payload (str): The text message to send.
        """
        msg_data = {
            "command": "dm",
            "sender": self.username,
            "payload": message_payload,
            "time": datetime.now().isoformat()
        }
        if self.manager.send_message_to_peer(peer_username, msg_data):
            self.ui_queue.put(f"{bcolors.WARNING}(Sending DM to {peer_username}){bcolors.ENDC}: {message_payload}")
        else:
            self.ui_queue.put(f"{bcolors.FAIL}[Node] Not connected to {peer_username}{bcolors.ENDC}")

    def _do_send_public(self, message_payload):
        """
        Build and Send Public message (Broadcast).

        :param message_payload (str): The text message to send.
        """
        msg_data = {
            "command": "public",
            "sender": self.username,
            "payload": message_payload,
            "time": datetime.now().isoformat()
        }
        self.manager.broadcast_message(msg_data)
        self.ui_queue.put(f"[App] Sent (public).") 

    def _do_send_channel(self, channel, message_payload):
        """
        Build and Send Channel message.

        :param channel (str): The name of the channel.
        :param message_payload (str): The text message to send.
        """
        peers_in_channel = self.get_peer_list(channel=channel)
        if not peers_in_channel:
            self.ui_queue.put(f"{bcolors.FAIL}[System] Channel '{channel}' is empty or does not exist.{bcolors.ENDC}")
            return

        users_in_channel = {p.get("peer_id") for p in peers_in_channel if p.get("peer_id") != self.username}
        if not users_in_channel:
            self.ui_queue.put(f"[System] No one else in channel '{channel}'.")
            return

        msg_data = {
            "command": "channel",
            "sender": self.username,
            "channel": channel,
            "payload": message_payload,
            "time": datetime.now().isoformat()
        }

        sent_count = 0
        for username in users_in_channel:
            if self.manager.send_message_to_peer(username, msg_data):
                sent_count += 1

        self.ui_queue.put(f"{bcolors.HEADER}(Sending channel '{channel}') [Sent to {sent_count} users]{bcolors.ENDC}: {message_payload}")

    # --- Tracker Call Functions ---

    def register_with_tracker(self):
        """Register this peer with Tracker (API /submit-info)."""
        try:
            body = {"peer_id": self.username, "ip": self.node_ip, "port": self.node_port}
            headers = {'Cookie': self.my_cookie}
            header, body_raw = http_request(self.tracker_addr, 'POST', '/submit-info', headers=headers, body=body)
            if header and "200 OK" in header:
                self.ui_queue.put("[App] Tracker registration successful.")
            else:
                self.ui_queue.put("[App] Tracker registration failed.")
        except Exception as e:
            self.ui_queue.put(f"{bcolors.FAIL}[App] Tracker registration error: {e}{bcolors.ENDC}")

    def get_peer_list(self, channel=None):
        """
        Get peer list from Tracker (API /get-list).

        :param channel (str, optional): If specified, get peers for this channel only.
        :rtype: list: A list of peer info dictionaries.
        """
        try:
            body = {}
            if channel:
                body = {"channel": channel}
            body["peer_id"] = self.username 
            headers = {'Cookie': self.my_cookie}
            header, body_raw = http_request(self.tracker_addr, 'POST', '/get-list', headers=headers, body=body)
            if body_raw:
                data = json.loads(body_raw.decode('utf-8'))
                if data.get("status") == "success":
                    return data.get("peers", [])
            return []
        except Exception as e:
            self.ui_queue.put(f"{bcolors.FAIL}[App] Error getting peer list: {e}{bcolors.ENDC}")
            return []

    def subscribe_to_channel(self, channel):
        """
        Join a channel (API /add-list).

        :param channel (str): The name of the channel to join.
        """
        try:
            body = {"peer_id": self.username, "channel": channel}
            headers = {'Cookie': self.my_cookie}
            header, body_raw = http_request(self.tracker_addr, 'POST', '/add-list', headers=headers, body=body)
            if body_raw:
                data = json.loads(body_raw.decode('utf-8'))
                if data.get("status") == "success":
                    if channel not in self.channels:
                        self.channels.append(channel)
                    self.ui_queue.put(f"{bcolors.OKGREEN}[App] Joined channel: {channel}{bcolors.ENDC}")

                    # After joining, automatically connect to peers already in the channel
                    peers_in_channel = self.get_peer_list(channel=channel)
                    for peer in peers_in_channel:
                        
                        peer_id_from_tracker = peer.get("peer_id")
                        self.manager.initiate_connection(peer_id_from_tracker, peer.get("ip"), peer.get("port"))
                        time.sleep(0.1)  
                else:
                    self.ui_queue.put(f"{bcolors.FAIL}[App] Error joining channel: {data.get('message')}{bcolors.ENDC}")
            else:
                self.ui_queue.put(f"{bcolors.FAIL}[App] Error API /add-list (No body).{bcolors.ENDC}")
        except Exception as e:
            self.ui_queue.put(f"{bcolors.FAIL}[App] Error API /add-list: {e}{bcolors.ENDC}")


# --- [4. HELPER FUNCTIONS (HTTP & UI)] ---

def http_request(server_addr, method, path, headers=None, body=None):
    """
    (Helper) Sends a raw HTTP request using sockets.
    Supports both form-data (str) and JSON (dict) for body.

    :param server_addr (tuple): (ip, port) of the target server.
    :param method (str): HTTP method (e.g., "GET", "POST").
    :param path (str): API path (e.g., "/login").
    :param headers (dict, optional): Request headers.
    :param body (dict or str, optional): Request body.

    :rtype: tuple (str, bytes): (raw_header_str, raw_body_bytes)
                                 or (None, None) if connection error.
    """
    headers = headers or {}
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(server_addr)
        request_line = f"{method} {path} HTTP/1.1\r\n"
        headers['Host'] = f"{server_addr[0]}:{server_addr[1]}"
        headers['Connection'] = 'close'
        if body:
            if isinstance(body, dict):
                body_bytes = json.dumps(body).encode('utf-8')
                if 'Content-Type' not in headers:
                    headers['Content-Type'] = 'application/json'
            else:
                body_bytes = body.encode('utf-8')
            headers['Content-Length'] = str(len(body_bytes))
        else:
            body_bytes = b''
        header_lines = "\r\n".join(f"{k}: {v}" for k, v in headers.items())
        request_data = f"{request_line}{header_lines}\r\n\r\n".encode('utf-8') + body_bytes
        s.sendall(request_data)
        response_data = b''
        while True:
            chunk = s.recv(1024)
            if not chunk:
                break
            response_data += chunk
        s.close()
        parts = response_data.split(b'\r\n\r\n', 1)
        header_raw = parts[0].decode('utf-8')
        body_raw = parts[1] if len(parts) > 1 else b''
        return header_raw, body_raw
    except Exception as e:
        print(f"[HTTP Request Error] Cannot connect to {server_addr}: {e}")
        return None, None


def parse_cookie(header_raw):
    """
    (Helper) Parses the 'Set-Cookie: auth=true' header.

    :param header_raw (str): The raw HTTP response header string.
    :rtype: str or None: The cookie string if found, else None.
    """
    if not header_raw:
        return None
    for line in header_raw.split('\r\n'):
        if line.lower().startswith('set-cookie:'):
            if 'auth=true' in line:
                return 'auth=true'
    return None


def ui_receiver_thread():
    """
    UI Thread. Receives messages from g_ui_queue and prints them.
    Handles redrawing the input prompt.
    """
    global g_ui_queue, g_my_username
    while True:
        message = g_ui_queue.get()
        if message is None:
            break
        print(f"\r\033[K{message}\n{bcolors.BOLD}{g_my_username}{bcolors.ENDC}> ", end="", flush=True)


# --- [5. MAIN FUNCTION (USER INTERFACE)] ---

def main():
    """
    Main entry point for the client.
    Handles command-line arguments, login, and the main UI loop.
    """
    global g_my_username
    parser = argparse.ArgumentParser(description="P2P Chat Client")
    parser.add_argument('--bip', default='127.0.0.1', help='IP of Backend (Login) Server')
    parser.add_argument('--bport', type=int, default=9000, help='Port of Backend (Login) Server')
    parser.add_argument('--tip', default='127.0.0.1', help='IP of Tracker Server')
    parser.add_argument('--tport', type=int, default=7000, help='Port of Tracker Server')
    args = parser.parse_args()

    # Create server variables from parameters
    BACKEND_SERVER = (args.bip, args.bport)
    TRACKER_SERVER = (args.tip, args.tport)
    print("--- WELCOME TO THE CHAT APPLICATION ---")

    # 1. LOGIN 
    my_cookie = None
    while not my_cookie:
        g_my_username = input(f"   {bcolors.OKBLUE}Username:{bcolors.ENDC} ")
        password = getpass.getpass(f"   {bcolors.OKBLUE}Password:{bcolors.ENDC} ")
        login_body_str = f"username={g_my_username}&password={password}"
        login_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        print(f"   {bcolors.WARNING}Authenticating...{bcolors.ENDC}")
        header, body = http_request(BACKEND_SERVER, 'POST', '/login', headers=login_headers, body=login_body_str)

        temp_cookie = parse_cookie(header)
        if temp_cookie:
            my_cookie = temp_cookie
            print(f"   {bcolors.OKGREEN}✓ Login successful!{bcolors.ENDC}")
            break
        else:
            print(f"   {bcolors.FAIL}✗ Error: Incorrect Username or Password.{bcolors.ENDC}")

    # 2. INITIALIZE APP 
    my_p2p_port = int(input(f"   {bcolors.OKBLUE}Enter your P2P port (e.g., 9001):{bcolors.ENDC} "))
    my_p2p_ip = '127.0.0.1'  

    # Create "Brain" object
    app = ChatApp(
        username=g_my_username,
        node_ip=my_p2p_ip,
        node_port=my_p2p_port,
        tracker_addr=TRACKER_SERVER,
        ui_queue=g_ui_queue
    )

    # 3. STARTING THREADS
    app.start(my_cookie)  # Starts the ChatApp 
    receiver_thread = threading.Thread(target=ui_receiver_thread, daemon=True)  # Starts the UI thread
    receiver_thread.start()

    time.sleep(1) 

    g_ui_queue.put("[App] Getting ALL peers list from Tracker...")
    # Call get_peer_list WITHOUT channel to auto-connect
    all_peers = app.get_peer_list()

    if all_peers:
        g_ui_queue.put(f"[App] Found {len(all_peers)} peer(s). Auto-connecting...")
        for peer in all_peers:
            peer_id = peer.get("peer_id")
            if peer_id:  
                app.manager.initiate_connection(peer_id, peer.get("ip"), peer.get("port"))
                time.sleep(0.1)  
    else:
        g_ui_queue.put("[App] No other peers found.")

    # 4. COMMAND LOOP (Main thread)
    print("\n" + "="*60)
    print(f"Ready. Welcome {g_my_username}!")
    print("Type /subscribe <channel> to join a channel.")
    print("Type /channel <channel> <message> to send to a channel.")
    print("Type /dm <username> <message> to send a private message.")
    print("Type <message> to chat publicly.")
    print("Type /quit to exit.")
    print("="*60 + "\n")

    print(f"{bcolors.BOLD}{g_my_username}{bcolors.ENDC}> ", end="", flush=True)

    try:
        while True:
            cmd = input() 

            if not cmd:
                continue  
            if cmd.lower() == "/quit":
                break

            # Send command to the ChatApp for processing
            app.handle_ui_command(cmd)

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        app.stop()
        g_ui_queue.put(None)  
        print("Exited. Goodbye!")


if __name__ == "__main__":
    main()