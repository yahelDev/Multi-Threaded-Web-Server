import os
import socket

from config import (
    BUFFER_SIZE,
    CONTENT_TYPES,
    DEFAULT_CONTENT_TYPE,
    DEFAULT_PAGE,
    HOST,
    HTTP_VERSION,
    PORT,
    STATIC_DIR,
)


def receive_request(client_sock):
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = client_sock.recv(BUFFER_SIZE)
        if not chunk:
            break
        data += chunk
    return data


def parse_request(raw_data):
    request_line = raw_data.split(b"\r\n")[0].decode()
    method, path, version = request_line.split(" ")
    return method, path, version


def resolve_file_path(url_path):
    if url_path == "/":
        url_path = DEFAULT_PAGE
    file_path = os.path.join(STATIC_DIR, url_path.lstrip("/"))
    return os.path.realpath(file_path)


def is_path_safe(file_path):
    return file_path.startswith(STATIC_DIR)


def get_content_type(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    return CONTENT_TYPES.get(ext, DEFAULT_CONTENT_TYPE)


def build_response(status_code, status_text, body, content_type="text/html"):
    header = (
        f"{HTTP_VERSION} {status_code} {status_text}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"\r\n"
    )
    return header.encode() + body


def build_error_response(status_code, status_text):
    body = b""
    header = (
        f"{HTTP_VERSION} {status_code} {status_text}\r\n"
        f"Content-Length: 0\r\n"
        f"\r\n"
    )
    return header.encode() + body


def serve_file(file_path):
    with open(file_path, "rb") as f:
        body = f.read()
    content_type = get_content_type(file_path)
    return build_response(200, "OK", body, content_type)


def handle_client(client_sock):
    with client_sock:
        raw_data = receive_request(client_sock)
        if not raw_data:
            return

        method, path, version = parse_request(raw_data)
        print(f"{method} {path} {version}")

        if method != "GET":
            client_sock.sendall(build_error_response(405, "Method Not Allowed"))
            return

        file_path = resolve_file_path(path)

        if not is_path_safe(file_path):
            client_sock.sendall(build_error_response(403, "Forbidden"))
            return

        if os.path.isfile(file_path):
            client_sock.sendall(serve_file(file_path))
        else:
            body = b"<h1>404 Not Found</h1>"
            client_sock.sendall(build_response(404, "Not Found", body))


def create_server_socket():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen()
    return server_sock


def run_server():
    server_sock = create_server_socket()
    print(f"Listening on {HOST}:{PORT}")

    try:
        while True:
            client_sock, client_addr = server_sock.accept()
            print(f"Connection from {client_addr}")
            handle_client(client_sock)
    finally:
        server_sock.close()


if __name__ == "__main__":
    run_server()
