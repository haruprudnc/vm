from daemon.weaprous import WeApRous
import socket
import argparse

import json
app = WeApRous()


@app.route("/", methods=["GET"])
def home(_):
    return {"message": "Welcome to the RESTful TCP WebApp"}

@app.route("/user", methods=["GET"])
def get_user(_):
    print("[SampleApp] /user")
    return {"id": 1, "name": "Alice", "email": "alice@example.com"}

@app.route("/echo", methods=["POST"])
def echo(body):
    try:
        data = json.loads(body)
        return {"received": data}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON"}

if __name__ == "__main__":
    # Parse command-line arguments to configure server IP and port
    parser = argparse.ArgumentParser(prog='Backend', description='', epilog='Beckend daemon')
    parser.add_argument('--server-ip', default='0.0.0.0')
    parser.add_argument('--server-port', type=int, default=9100)
 
    args = parser.parse_args()
    ip = args.server_ip
    port = args.server_port

    # Prepare and launch the RESTful application
    app.prepare_address(ip, port)
    app.run()