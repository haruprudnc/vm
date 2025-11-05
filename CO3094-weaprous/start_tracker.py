#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
#
# WeApRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#

"""
start_tracker
~~~~~~~~~~~~~~~

Entry point for starting the Tracker Server for the chat application.
Uses WeApRous framework to provide RESTful APIs for peer management.
"""

import argparse
from daemon.weaprous import WeApRous
from tracker_server import login, submit_info, get_list, add_list, connect_peer, broadcast_peer, send_peer

PORT = 7000  # Default port for tracker server

app = WeApRous()


@app.route('/login', methods=['POST'])
def handle_login(headers, body):
    """
    Handle POST /login - Peer authentication
    
    :param headers: Request headers (dict).
    :param body: Request body (JSON string or dict).
    
    :rtype dict: JSON response.
    """
    result, status_code, reason = login(headers, body)
    # Note: WeApRous defaults to 200 OK, error status codes need to be handled separately
    # For now, return dict and let httpadapter handle errors via exception
    if status_code != 200:
        # Return error dict - status code handling can be improved in httpadapter
        return result
    return result


@app.route('/submit-info', methods=['POST'])
def handle_submit_info(headers, body):
    """
    Handle POST /submit-info - Peer registration
    
    :param headers: Request headers (dict).
    :param body: Request body (JSON string or dict).
    
    :rtype dict: JSON response.
    """
    result, status_code, reason = submit_info(headers, body)
    if status_code != 200:
        return result
    return result


@app.route('/get-list', methods=['POST'])
def handle_get_list(headers, body):
    """
    Handle GET /get-list - Get active peers list
    
    :param headers: Request headers (dict).
    :param body: Request body (JSON string or dict).
    
    :rtype dict: JSON response with peer list.
    """
    result, status_code, reason = get_list(headers, body)
    if status_code != 200:
        return result
    return result


@app.route('/add-list', methods=['POST'])
def handle_add_list(headers, body):
    """
    Handle POST /add-list - Add peer to list
    
    :param headers: Request headers (dict).
    :param body: Request body (JSON string or dict).
    
    :rtype dict: JSON response.
    """
    result, status_code, reason = add_list(headers, body)
    if status_code != 200:
        return result
    return result


@app.route('/connect-peer', methods=['POST'])
def handle_connect_peer(headers, body):
    """
    Handle POST /connect-peer - Initiate P2P connection
    
    :param headers: Request headers (dict).
    :param body: Request body (JSON string or dict).
    
    :rtype dict: JSON response with target peer info.
    """
    result, status_code, reason = connect_peer(headers, body)
    if status_code != 200:
        return result
    return result


@app.route('/broadcast-peer', methods=['POST'])
def handle_broadcast_peer(headers, body):
    """
    Handle POST /broadcast-peer - Broadcast message to peers
    
    :param headers: Request headers (dict).
    :param body: Request body (JSON string or dict).
    
    :rtype dict: JSON response with list of target peers.
    """
    result, status_code, reason = broadcast_peer(headers, body)
    if status_code != 200:
        return result
    return result


@app.route('/send-peer', methods=['POST'])
def handle_send_peer(headers, body):
    """
    Handle POST /send-peer - Send message to specific peer
    
    :param headers: Request headers (dict).
    :param body: Request body (JSON string or dict).
    
    :rtype dict: JSON response with target peer info.
    """
    result, status_code, reason = send_peer(headers, body)
    if status_code != 200:
        return result
    return result


if __name__ == "__main__":
    """
    Entry point for launching the tracker server.
    
    Parses command-line arguments to configure the server's IP address and port,
    then launches the WeApRous application with all tracker API routes.
    
    :arg --server-ip (str): IP address to bind the server (default: 0.0.0.0).
    :arg --server-port (int): Port number to bind the server (default: 7000).
    """
    parser = argparse.ArgumentParser(
        prog='Tracker',
        description='Tracker Server for Chat Application',
        epilog='Tracker daemon for peer management'
    )
    parser.add_argument(
        '--server-ip',
        type=str,
        default='0.0.0.0',
        help='IP address to bind the server. Default is 0.0.0.0'
    )
    parser.add_argument(
        '--server-port',
        type=int,
        default=PORT,
        help='Port number to bind the server. Default is {}.'.format(PORT)
    )
    
    args = parser.parse_args()
    ip = args.server_ip
    port = args.server_port
    
    print("=" * 60)
    print("Tracker Server - Chat Application Client-Server Module")
    print("=" * 60)
    print("Starting tracker server on {}:{}".format(ip, port))
    print("APIs available:")
    print("  POST   /login         - Peer authentication")
    print("  POST   /submit-info    - Peer registration")
    print("  POST   /get-list       - Get active peers list")
    print("  POST   /add-list       - Add peer to list")
    print("  POST   /connect-peer    - Initiate P2P connection")
    print("  POST   /broadcast-peer  - Broadcast message to peers")
    print("  POST   /send-peer      - Send message to specific peer")
    print("=" * 60)
    
    # Prepare and launch the RESTful application
    app.prepare_address(ip, port)
    app.run()

