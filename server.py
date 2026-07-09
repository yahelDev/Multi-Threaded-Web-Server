import os
import socket
from concurrent.futures import ThreadPoolExecutor

from config import (
    ALLOWED_SUBDIRS,
    BUFFER_SIZE,
    CLIENT_TIMEOUT_SECONDS,
    CONTENT_TYPES,
    DEFAULT_CONTENT_TYPE,
    DEFAULT_PAGE,
    HOST,
    HTTP_VERSION,
    MAX_REQUEST_HEADER_SIZE,
    PORT,
    STATIC_DIR,
    THREAD_POOL_SIZE,
)

class BadRequestError(Exception):
    pass


def receive_request(client_sock):
    data = b""
    while b"\r\n\r\n" not in data:
        if len(data) > MAX_REQUEST_HEADER_SIZE:
            raise BadRequestError("Request header too large")
        chunk = client_sock.recv(BUFFER_SIZE)
        if not chunk:
            break
        data += chunk
    return data


def parse_request(raw_data):
    try:
        request_line = raw_data.split(b"\r\n")[0].decode("ascii")
        method, path, version = request_line.split(" ")
    except (UnicodeDecodeError, ValueError) as exc:
        raise BadRequestError("Malformed request line") from exc
    return method, path, version


def has_traversal(url_path):
    return ".." in url_path


def resolve_file_path(url_path):
    if url_path == "/":
        url_path = DEFAULT_PAGE
    file_path = os.path.join(STATIC_DIR, url_path.lstrip("/"))
    return os.path.realpath(file_path)


def is_path_safe(file_path):
    real_static = os.path.realpath(STATIC_DIR)
    return file_path == real_static or file_path.startswith(real_static + os.sep)


def is_in_allowed_subdir(file_path):
    real_static = os.path.realpath(STATIC_DIR)
    rel_path = os.path.relpath(file_path, real_static)
    # Files directly in the static root (index.html) are allowed
    if os.sep not in rel_path:
        return True
    top_dir = rel_path.split(os.sep)[0]
    return top_dir in ALLOWED_SUBDIRS


def get_content_type(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    return CONTENT_TYPES.get(ext, DEFAULT_CONTENT_TYPE)


def build_response(status_code, status_text, body, content_type="text/html"):
    # Build the HTTP response header and concatenate it with the body
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


def handle_client(client_sock, client_addr):
    with client_sock:
        client_sock.settimeout(CLIENT_TIMEOUT_SECONDS)
        try:
            raw_data = receive_request(client_sock)
        except socket.timeout:
            print(f"Timeout receiving from {client_addr}")
            return
        except BadRequestError:
            client_sock.sendall(build_error_response(400, "Bad Request"))
            return

        if not raw_data:
            return

        if b"\r\n\r\n" not in raw_data:
            client_sock.sendall(build_error_response(400, "Bad Request"))
            return

        try:
            method, path, version = parse_request(raw_data)
        except BadRequestError:
            client_sock.sendall(build_error_response(400, "Bad Request"))
            return

        print(f"{client_addr} - {method} {path} {version}")

        if method != "GET":
            client_sock.sendall(build_error_response(405, "Method Not Allowed"))
            return

        if has_traversal(path):
            client_sock.sendall(build_error_response(400, "Bad Request"))
            return

        file_path = resolve_file_path(path)

        if not is_path_safe(file_path):
            client_sock.sendall(build_error_response(403, "Forbidden"))
            return

        if not is_in_allowed_subdir(file_path):
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
    print(f"Listening on {HOST}:{PORT} with {THREAD_POOL_SIZE} worker threads")

    with ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE) as pool:
        try:
            while True:
                client_sock, client_addr = server_sock.accept()
                print(f"Connection from {client_addr}")
                pool.submit(handle_client, client_sock, client_addr)
        finally:
            server_sock.close()


if __name__ == "__main__":
    run_server()
