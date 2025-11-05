"""
websocket_server.py
~~~~~~~~~~~~~~~~~~~
WebSocket bridge for the P2P Chat Client
Allows web clients to interact with the chat system via WebSocket
"""

import asyncio
import websockets
import json
import threading
import queue
from client import ChatApp, http_request, parse_cookie

class WebSocketBridge:
    def __init__(self):
        self.clients = {}  # {websocket: {"username": str, "app": ChatApp}}
        self.client_lock = threading.Lock()
        
    async def handle_client(self, websocket, path):
        client_id = id(websocket)
        print(f"[WebSocket] New connection: {client_id}")
        
        try:
            async for message in websocket:
                data = json.loads(message)
                command = data.get("command")
                
                if command == "login":
                    await self.handle_login(websocket, data)
                elif command == "chat":
                    await self.handle_chat(websocket, data)
                elif command == "subscribe":
                    await self.handle_subscribe(websocket, data)
                elif command == "get_channels":
                    await self.handle_get_channels(websocket)
                elif command == "get_peers":
                    await self.handle_get_peers(websocket, data)
                    
        except websockets.exceptions.ConnectionClosed:
            print(f"[WebSocket] Connection closed: {client_id}")
        finally:
            await self.cleanup_client(websocket)
    
    async def handle_login(self, websocket, data):
        username = data.get("username")
        password = data.get("password")
        backend_server = (data.get("backend_ip", "127.0.0.1"), 
                         data.get("backend_port", 9000))
        tracker_server = (data.get("tracker_ip", "127.0.0.1"), 
                         data.get("tracker_port", 7000))
        p2p_port = data.get("p2p_port", 9001)
        
        # Authenticate with backend
        login_body = f"username={username}&password={password}"
        login_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        header, body = http_request(backend_server, 'POST', '/login', 
                                   headers=login_headers, body=login_body)
        
        cookie = parse_cookie(header)
        if not cookie:
            await websocket.send(json.dumps({
                "type": "login_response",
                "success": False,
                "message": "Invalid credentials"
            }))
            return
        
        # Create UI queue for this client
        ui_queue = queue.Queue()
        
        # Create ChatApp instance
        app = ChatApp(
            username=username,
            node_ip="127.0.0.1",
            node_port=p2p_port,
            tracker_addr=tracker_server,
            ui_queue=ui_queue
        )
        
        app.start(cookie)
        
        # Store client info
        with self.client_lock:
            self.clients[websocket] = {
                "username": username,
                "app": app,
                "ui_queue": ui_queue
            }
        
        # Start UI message forwarder
        asyncio.create_task(self.forward_ui_messages(websocket))
        
        # Auto-connect to peers
        await asyncio.sleep(0.5)
        all_peers = app.get_peer_list()
        for peer in all_peers:
            peer_id = peer.get("peer_id")
            if peer_id:
                app.manager.initiate_connection(peer_id, peer.get("ip"), peer.get("port"))
                await asyncio.sleep(0.1)
        
        await websocket.send(json.dumps({
            "type": "login_response",
            "success": True,
            "username": username
        }))
    
    async def forward_ui_messages(self, websocket):
        """Forward messages from UI queue to WebSocket"""
        client_info = self.clients.get(websocket)
        if not client_info:
            return
            
        ui_queue = client_info["ui_queue"]
        
        try:
            while websocket in self.clients:
                try:
                    # Non-blocking get with timeout
                    message = ui_queue.get(timeout=0.1)
                    if message:
                        await websocket.send(json.dumps({
                            "type": "message",
                            "content": message
                        }))
                except queue.Empty:
                    await asyncio.sleep(0.1)
        except Exception as e:
            print(f"[WebSocket] Error forwarding messages: {e}")
    
    async def handle_chat(self, websocket, data):
        client_info = self.clients.get(websocket)
        if not client_info:
            return
        
        app = client_info["app"]
        message = data.get("message", "")
        app.handle_ui_command(message)
    
    async def handle_subscribe(self, websocket, data):
        client_info = self.clients.get(websocket)
        if not client_info:
            return
        
        app = client_info["app"]
        channel = data.get("channel")
        app.subscribe_to_channel(channel)
    
    async def handle_get_channels(self, websocket):
        client_info = self.clients.get(websocket)
        if not client_info:
            return
        
        app = client_info["app"]
        await websocket.send(json.dumps({
            "type": "channels_list",
            "channels": app.channels
        }))
    
    async def handle_get_peers(self, websocket, data):
        client_info = self.clients.get(websocket)
        if not client_info:
            return
        
        app = client_info["app"]
        channel = data.get("channel")
        peers = app.get_peer_list(channel=channel)
        
        await websocket.send(json.dumps({
            "type": "peers_list",
            "peers": peers
        }))
    
    async def cleanup_client(self, websocket):
        with self.client_lock:
            client_info = self.clients.pop(websocket, None)
            if client_info:
                app = client_info["app"]
                app.stop()
                print(f"[WebSocket] Cleaned up client: {client_info['username']}")

async def main():
    bridge = WebSocketBridge()
    async with websockets.serve(bridge.handle_client, "localhost", 8765):
        print("[WebSocket] Server started on ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())