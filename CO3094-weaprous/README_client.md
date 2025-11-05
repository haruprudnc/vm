Chat Client - P2P & UI Module
Status: ✅ Complete - All features implemented and tested. Integrates with both Backend (Task 1) and Tracker  modules.

Last Updated: 2025-11-04 (Final 2-layer architecture)

Overview
The Chat Client is the user-facing component of the hybrid chat application. It implements the Peer-to-Peer (P2P) paradigm for messaging and the Client-Server (C/S) paradigm for authentication and peer discovery.

This client is built on a 2-layer architecture for clean separation of concerns:

ConnectionManager (Engine): Manages all low-level socket operations, multi-threading, and P2P handshakes.

ChatApp (Brain): Manages all application logic, including API calls, channel/DM routing, and UI command processing.

It provides a rich Command-Line Interface (CLI) for users to log in, join channels, and send public, private, or channel-specific messages.

Architecture
The client integrates with all other parts of the system.

     ┌─────────────────┐
     │ Backend Server  │ (Task 1: Login)
     │ (localhost:9000)│
     └────────┬────────┘
              │ 1. Login (POST /login, form-data)
              │    (Receives 'auth=true' cookie)
              │
┌─────────────▼─────────────┐      ┌────────────────┐
│       Chat Client         │◄────►│ Tracker Server │ (Task 2: C/S)
│     (client_new.py)       │ 2. API│ (localhost:7001) │
└─────────────┬─────────────┘ calls └────────────────┘
              │ 3. P2P      (e.g., /submit-info, /get-list)
              │
     ┌────────▼────────┐
     │ Other Chat Client │ (Task 2: P2P)
     └───────────────────┘
Files Implemented & Modified
1. Core Module

client_new.py - Main Client Application

This is the primary entry point and contains all client-side logic.

ConnectionManager Class (Engine):

start_listener(): Binds to the user's P2P port (9001, 9002, etc.).

_listen_loop(): Runs in a thread to accept incoming connections.

initiate_connection(): Actively connects to peers from the Tracker list.

_handle_incoming_handshake(): Performs the identify JSON handshake.

_stream_peer_messages(): Creates one dedicated recv() thread for each peer.

send_message_to_peer() / broadcast_message(): Low-level send functions.

ChatApp Class (Brain):

start(): Initializes the Engine and registers with the Tracker.

_process_events(): Runs in a thread, processing events from the Engine (e.g., "message", "disconnected").

handle_ui_command(): Parses user input (e.g., /dm, /channel).

_do_send_...(): Logic for sending DMs, public, or channel messages.

register_with_tracker(): Calls POST /submit-info.

get_peer_list(): Calls POST /get-list.

subscribe_to_channel(): Calls POST /add-list.

Global Functions: g_ui_queue

main(): Handles login, argparse, and the main UI input loop.

ui_receiver_thread(): Manages printing messages from the g_ui_queue without breaking user input.

http_request(): Helper function. A custom HTTP client built on raw sockets, supporting both application/x-www-form-urlencoded (for Login) and application/json (for Tracker).

2. Modified Server Files (Integration Fixes)

To achieve integration, several server-side files required critical fixes:

trackerserver.py (Modified)
Implemented channel-based logic for the GET-LIST API, allowing peer list filtering by channel.
Enhanced ADD-LIST to support adding peers to specific channels.

peer_manager.py (Modified)
Added join_channel and get_peers_in_channel methods to manage channel-based peer operations.

start_tracker.py (Modified)
Updated GET-LIST request handling from GET to POST to support reading request body data.

httpadapter.py (Modified)
Added a set of valid users for authentication and request validation.

Core Features
1. Two-Layer Architecture (Engine/Brain)

Engine (ConnectionManager): Only knows sockets. recv() data and puts it in an internal queue.

Brain (ChatApp): Only knows logic. Reads from the internal queue, processes the command, and puts a formatted string into the g_ui_queue for printing.

Decoupling: This design allows the Engine to be tested independently of the chat logic.

2. P2P Handshake Protocol

On connection (both incoming and outgoing), the client sends an identify command:

JSON
{"command": "identify", "sender": "my_username"}
The other peer responds with their own identify message.

Only after this handshake is the connection added to the active peer list (self.peers).

3. P2P Message Protocol

All subsequent chat messages are sent as JSON objects:

JSON
{
  "command": "dm", // "channel" or "public"
  "sender": "my_username",
  "payload": "This is the message text",
  "channel": "gen", // Optional
  "time": "2025-11-04T21:30:00.000"
}
4. Multi-Threaded UI

The main thread is dedicated to blocking on input().

A separate ui_receiver_thread blocks on g_ui_queue.get().

When a message arrives, the receiver thread prints it and redraws the user's prompt (> ), providing a seamless, non-blocking chat experience.

5. Multi-Threaded P2P Engine

The ConnectionManager spawns N+1 threads:

1 thread (_listen_loop) for accepting new connections.

N threads (_stream_peer_messages), one for each of the N active peers, dedicated to blocking on recv().

How to Run
Start Backend (Task 1) Server (Port 9000):

Bash
python3 start_backend.py
Start Tracker (C/S) Server (Port 7001):

Bash
python3 start_tracker.py --server-port 7001
Start Client 1 (admin) (P2P Port 9001):

Bash
# Connects to Tracker on port 7001
python3 client_new.py 

# --- Follow prompts ---
# Username: admin
# Password: <admin_password>
# Enter your P2P port: 9001
Start Client 2 (admin2) (P2P Port 9002):

Bash
# Connects to Tracker on port 7001
python3 client_new.py 

# --- Follow prompts ---
# Username: admin2
# Password: <admin2_password>
# Enter your P2P port: 9002
Test Cases
✅ Test 1: Authentication (Task 1)

Action: Run client_new.py, login with admin / password.

Expected: ✓ Login successful!

Result: ✓ PASS

✅ Test 2: Tracker Registration (C/S)

Action: After login, client automatically calls register_with_tracker().

Expected: Log [App] Tracker registration successful.

Result: ✓ PASS

✅ Test 3: Peer Discovery & Auto-Connect

Action: Client 1 (admin) starts. Client 2 (admin2) starts.

Expected: Client 2 log shows [App] Found 1 peer(s). Auto-connecting... followed by [App] P2P connection successful with admin.

Result: ✓ PASS

✅ Test 4: Public Chat (P2P)

Action: Client 1 types Hello public.

Expected: Client 2 receives admin: Hello public.

Result: ✓ PASS

✅ Test 5: Channel Subscription & Chat (C/S + P2P)

Action (Client 1): /subscribe general

Action (Client 2): /subscribe general

Action (Client 1): /channel general hello channel

Expected: Client 2 receives (Channel general) admin: hello channel.

Result: ✓ PASS (This confirms the tracker_server.py bug is fixed).

✅ Test 6: DM Chat (P2P)

Action (Client 1): /dm admin2 this is a secret

Expected: Client 2 receives (Private) admin: this is a secret.

Result: ✓ PASS

