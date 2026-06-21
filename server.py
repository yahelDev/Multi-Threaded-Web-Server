import socket
import os

HOST = '0.0.0.0'
PORT = 8080
BUFFER_SIZE = 4096
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

CONTENT_TYPES = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".gif": "image/gif",
    ".txt": "text/plain",
}

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_sock.bind((HOST, PORT))
server_sock.listen()

print(f"Listening on {HOST}:{PORT}")

while True:
    client_sock, client_addr = server_sock.accept()
    print(f"Connection from {client_addr}")

    with client_sock:
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = client_sock.recv(BUFFER_SIZE)
            if not chunk:
                break
            data += chunk

        if not data:
            continue

        request_line = data.split(b"\r\n")[0].decode()
        method, path, version = request_line.split(" ")
        print(f"{method} {path} {version}")

        if method != "GET":
            response = f"HTTP/1.0 405 Method Not Allowed\r\nContent-Length: 0\r\n\r\n"
            client_sock.sendall(response.encode())
            continue

        if path == "/":
            path = "/index.html"

        file_path = os.path.join(STATIC_DIR, path.lstrip("/"))

        # Prevent directory traversal
        file_path = os.path.realpath(file_path)
        if not file_path.startswith(STATIC_DIR):
            response = "HTTP/1.0 403 Forbidden\r\nContent-Length: 0\r\n\r\n"
            client_sock.sendall(response.encode())
            continue

        if os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                body = f.read()

            ext = os.path.splitext(file_path)[1].lower()
            content_type = CONTENT_TYPES.get(ext, "application/octet-stream")

            header = (
                f"HTTP/1.0 200 OK\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(body)}\r\n"
                f"\r\n"
            )
            client_sock.sendall(header.encode() + body)
        else:
            body = b"<h1>404 Not Found</h1>"
            header = (
                f"HTTP/1.0 404 Not Found\r\n"
                f"Content-Type: text/html\r\n"
                f"Content-Length: {len(body)}\r\n"
                f"\r\n"
            )
            client_sock.sendall(header.encode() + body)
