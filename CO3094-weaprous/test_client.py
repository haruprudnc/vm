from socket import *
import json

serverIP = '127.0.0.1'
serverPort = 8000
data = json.dumps(
    {
        "username": "admin",
        "password": "password"
    }
)
# print(len(data.encode('utf-8')))
# req = ( 
#     "GET /user HTTP/1.1\r\n"
#     "Content-Type: application/json\r\n"
#     "\r\n"
#     "{}").format(data)
# print(req)
# sckt = socket(AF_INET, SOCK_STREAM)
# sckt.connect((serverIP, serverPort))
# sckt.send(req.encode('utf-8'))

# res = sckt.recv(1024)
# print(res)
# sckt.close()

def send(serverIP="127.0.0.1", serverPort=8000, method="GET", path="/", body=None):
    req = (
        "{} {} HTTP1.1\r\n"
        "Content-Type: application/json\r\n"
        "Host: {}:{}\r\n"
        "\r\n"
        "{}"
    ).format(method, path, serverIP, serverPort, body)

    sckt = socket(AF_INET, SOCK_STREAM)
    sckt.connect((serverIP, serverPort))
    sckt.send(req.encode('utf-8'))

    res = sckt.recv(1024)
    print(res)
    return

send(path="/user")