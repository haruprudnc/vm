# start_server.py
#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
#
# Entry point for launching the Chat Server
# -----------------------------------------

import argparse
import sys
import os

# Ensure project root path is added for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import ChatServer
from server.chat_server import ChatServer


def main():
    """Main entry point for Chat Server launcher."""
    parser = argparse.ArgumentParser(
        prog='ChatServer',
        description='Central tracker for P2P Chat Application',
        epilog='CO3094 WeApRous Assignment - HCMUT'
    )

    parser.add_argument('--server-ip', default='0.0.0.0', help='Server IP address to bind')
    parser.add_argument('--server-port', type=int, default=8000, help='Port to listen on')

    args = parser.parse_args()

    # Initialize and run the chat server
    server = ChatServer()
    server.run(args.server_ip, args.server_port)


if __name__ == "__main__":
    main()
