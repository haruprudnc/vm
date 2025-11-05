"""
- Peer registration: When a new peer joins, it must submit its IP and port to the centralized server.
- Tracker update: The centralized server must maintain a tracking list of active peers.
- Peer discovery: Peers can request the current list of active peers from the server.
- Connection setup: Peers use the tracking list to initiate direct P2P connections.
"""

from daemon.weaprous import WeApRous
import argparse
import json



class TrackerServer:
    def __init__(self):
        self.app = WeApRous()

        self.peers = []
        self.channels = {}

        self.setup_API()

    def setup_API(self):
        app = self.app

        @app.route('/login', methods=['POST'])
        def login(headers="guest", body="anonymous"):
            """
            Handle user login via POST request.

            This route simulates a login process and prints the provided headers and body
            to the console.

            :param headers (str): The request headers or user identifier.
            :param body (str): The request body or login payload.
            """
            print("[SampleApp] Logging in {} to {}".format(headers, body))

        @app.route('/peer-register', methods=['POST'])
        def peer_register(headers, body):
            # return (json.dumps({"hello"})).encode('utf-8')
            return self.handle_peer_register(body)
        
        @app.route('/get-peer-list', methods=['GET'])
        def get_peer_list(headers, body):
            return {"hello"}
        #     return {
        # "username": "test_user",
        # "email": "test@example.com",
        # "bio": "This is a long test profile",
        # "preferences": {
        #     "notifications": "true",
        #     "theme": "dark",
        #     "language": "en"
        # },
        # "friends": [
        #     {"id": 1, "name": "Alice"},
        #     {"id": 2, "name": "Bob"},
        #     {"id": 3, "name": "Charlie"}
        # ],
        # "posts": [
        #     {
        #     "id": 1,
        #     "title": "My first post",
        #     "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        #     }
        # ],
        # "data": [
        #     {"index": 0, "value": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"},
        #     {"index": 1, "value": "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"},
        #     {"index": 2, "value": "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"},
        #     {"index": 3, "value": "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD"}
        # ]
        # }
            return self.handle_get_peer_list()

        @app.route('/add-peer-to-channel', methods=['POST'])
        def add_peer_to_channel(headers, body):
            return self.handle_add_peer_to_channel(body)
        
        @app.route('/get-channel-list', methods=['GET'])
        def get_channel_list(headers, body):
            return self.handle_get_channel_list()

    def handle_peer_register(self, body):
        """
        incoming JSON format:
        {
            "username": "<_____>",
            "clientIP": "<_____>",
            "clientPort": "<_____>"
        }
        """

        try:
            if not body:
                return
            
            print(body)
            # data = json.loads(body)
            data = body
            peer = data.get('username')
            peer_ip = data.get('clientIP')
            peer_port = data.get('clientPort')
            
            if not all([peer, peer_ip, peer_port]):
                return json.dumps(
                    {
                        "status": "error",
                        "msg": "username, clientIP, and clientPort are required!!!!"
                    }
                )

            self.peers.append(body)
            print("^^--------------------------------------------------------------------^^")

            print(self.peers)
            print("^^====================================================================^^")
            
            return json.dumps(
                {
                    "status": "sucess",
                    "msg": ""
                }
            )
        except Exception as e:
            print("[tracker_server.py-peer_register] Failed {}!!!!!!!!!!!!!!!!!!!!".format(e))
            return json.dumps(
                {
                    "status": "error",
                    "msg": ""
                }
            )
        return
        
    def handle_get_peer_list(self):
        return

    def handle_add_peer_to_channel(self, body):
        return
    
    def handle_get_channel_list(self):
        return json.dumps(
                {
                    "status": "error",
                    "msg": ""
                })

    def add_peer(self, JSON):
        #TODO check dup
        for peer in self.peers:
            if peer == JSON:
                raise "Duplcated peer"
        self.peers.append(JSON)
        return
    
    def rm_peer(self, index=None, name=None):
        """
        Remove last peer if not specify
        """
        if index and name:
            raise "Fail in remocing peer!!!!"
        
        if index is None and name is None:
            self.peers.pop(-1)

        if index:
            self.peers.pop(index)
            return
        else:
            return


    def run(self, ip, port):
        """
        Start tracker server
        """
        print("[ChatServer] Starting on {}:{}".format(ip, port))
        self.app.prepare_address(ip, port)
        self.app.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tracker Server')
    parser.add_argument('--server-ip', default='127.0.0.1', help='Server IP')
    parser.add_argument('--server-port', type=int, default=8000, help='Server port')
    args = parser.parse_args()
    
    server = TrackerServer()
    server.run(args.server_ip, args.server_port)