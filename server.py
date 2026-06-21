import socket

HOST = '0.0.0.0'
PORT = 8080
BUFFER_SIZE = 4096

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Allow immediate reuse of the port after restart
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

        print(f"Raw bytes received: {data}")

        # Parse the HTTP request line
        request_line = data.split(b"\r\n")[0].decode()
        method, path, version = request_line.split(" ")
        print(f"Method: {method}")
        print(f"Path: {path}")
        print(f"Version: {version}")
