from socket import *
import json
import argparse



def send_req(methods, path, body=None):
    try:
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName,serverPort))

        request = (
            "{} {} HTTP/1.1\r\n"
            "Content-Type: application/json\r\n"
            "User-Agent: client_app.py\r\n"
            "Host: {}:{}\r\n"
            "\r\n"
            "{}"
        ).format(methods, path, serverName, serverPort, body)

        # print("[client_app.py] request \n{}".format(request))

        clientSocket.send(request.encode('utf-8'))
        RAWresponse = clientSocket.recv(1024)
        clientSocket.close()

        response = RAWresponse.decode('utf-8')
        return response
    
    except Exception as e:
        print("[client_app.py-send_req]", e)
        return "Failed"

def submit_info(peer_id, ip, port):
    """ Register  """
    methods = "POST"
    path = "/submit-info"
    
    body = json.dumps(
        {
            "peer_id": peer_id,
            "ip": ip, 
            "port": port
        }
    )

    res = send_req(methods, path, body)
    return res.get("status")

def get_list():
    methods = "GET"
    path = "/get-list"
    res = send_req(methods, path)

    
    return

def

submit_info("alice", "127.0.0.1", 7001)

def user_input():
    def cmd_get_list(args):
        return get_list()

    def cmd_get_channel(args)
        return get_channel_list()
    
    cmd_list = {
        "ls": cmd_get_list,
        "ls-channel": cmd_get_channel
    }

    while True:
        prompt = input("> ").strip()

        syntax = prompt.split()
        cmd =  syntax[0]
        args = syntax[1:]

        if cmd == "quit":
            break

        handler = cmd_list.get(cmd)
        handler(args)

#^^ Helper Function
def is200(response):
    if response.get("status") == "success"
        return True
    else
        return False
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Client Application')
    parser.add_argument('--client-id', default='alice', help='Identification Please!!!!')
    parser.add_argument('--client-ip', default='127.0.0.1', help='Client IP')
    parser.add_argument('--client-port', type=int, default='7001', help='Client Port')
    parser.add_argument('--server-ip', default='127.0.0.1', help='Server IP')
    parser.add_argument('--server-port', type=int, default=7000, help='Server Port')
    
    args = parser.parse_args()

    clientID = args.client_id
    clientIP = args.client_ip
    clientPort = args.client_port
    serverName = args.server_ip
    serverPort = args.server_port

    activePeers = []
    

    print("^^--------------------------------------------------------------------^^")
    print("Welcome to to Client Application")  
    print("^^====================================================================^^")
    print("Connecting to sever...")
    if submit_info(clientID, clientIP, clientPort) != "success"
        print("Failed to connect to server!!!!")
    else:
        print("Successfully connect to server!!!!")
    print("Basic command:")
    print("    ls - list and add all peers connect to server to local memory.")
    print("    ls-channel - list all active channels.")


    user_input()
