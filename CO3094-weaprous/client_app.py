from socket import *
import json
import argparse


serverName = '127.0.0.1'
serverPort = 7000

def send_req(methods, path, body):
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
    body = json.dumps(
        {
            "peer_id": peer_id,
            "ip": ip, 
            "port": port
        }
    )

    send_req("POST", "/submit-info", body)
    return

def get_list():
    methods = "GET"
    path = "/get-list"
    send_req(methods, path)
    return

submit_info("alice", "127.0.0.1", 7001)

def user_input():
    def cmd_get_list(args):
        return get_list()
    
    cmd_list = {
        "ls": cmd_get_list
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




if __name__ == '__main__':
    print("^^--------------------------------------------------------------------^^")
    print("Welcome to to Client Application")  
    print("^^====================================================================^^")

    parser = argparse.ArgumentParser(description='Client Application')
    parser.add_argument('--client-id', default='alice', help='Identification Please!!!!')
    parser.add_argument('--client-ip', default='127.0.0.1', help='Client IP')
    parser.add_argument('--client-port', type=int, default='7001', help='Client Port')
    parser.add_argument('--server-ip', default='127.0.0.1', help='Server IP')
    parser.add_argument('--server-port', type=int, default=7000, help='Server Port')

    args = parser.parse_args()

    user_input()
