# start_client.py
#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
#
# Entry point for launching the Chat Client
# -----------------------------------------

import argparse
import sys
import os

# Ensure the root path is added for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the ChatClient class
from server.chat_client import ChatClient


def main():
    """Main entry point for Chat Client launcher."""
    parser = argparse.ArgumentParser(
        prog='ChatClient',
        description='Client-side program for P2P Chat Application',
        epilog='CO3094 WeApRous Assignment - HCMUT'
    )

    parser.add_argument('--peer-id', required=True, help='Unique Peer ID')
    parser.add_argument('--server-ip', default='127.0.0.1', help='Central server IP')
    parser.add_argument('--server-port', type=int, default=8000, help='Central server port')
    parser.add_argument('--my-ip', default='127.0.0.1', help='This peer’s IP address')
    parser.add_argument('--my-port', type=int, default=5001, help='This peer’s listening port')

    args = parser.parse_args()

    # Initialize client
    client = ChatClient(args.peer_id, args.server_ip, args.server_port)

    print("\n=== Starting Chat Client ===\n")

    # 1️⃣ Login
    if not client.login():
        print("✗ Login failed, exiting.")
        return

    # 2️⃣ Register this peer info
    if not client.register_peer_info(args.my_ip, args.my_port):
        print("✗ Peer registration failed, exiting.")
        return

    # 3️⃣ Get peer list
    peers = client.get_peer_list()
    print(f"✓ Found {len(peers)} active peers")

    # 4️⃣ Join default channel
    if client.join_channel("general"):
        print("✓ Joined channel 'general'")

    # 5️⃣ Get channel list
    channels = client.get_channel_list()
    print(f"✓ Available channels: {channels}")

    # 6️⃣ Get channel members
    members = client.get_channel_members("general")
    print(f"✓ Members in 'general': {members}")

    print("\n=== Chat Client setup complete ===\n")


if __name__ == "__main__":
    main()
