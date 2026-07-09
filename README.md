# Subbmitters: Yahel Ozeri and Efrat Roth
# Multi-Threaded Web Server (HTTP/1.0)

## Project Overview

This repository contains a lightweight HTTP/1.0 web server implemented from scratch using low-level socket APIs in Python. The server is built for a Computer Networks mid-term programming assignment and demonstrates a concurrent, multi-threaded architecture using a thread pool to serve multiple clients efficiently.

## Features

- **Multi-threaded architecture:** Uses `ThreadPoolExecutor` to handle multiple concurrent client connections with a fixed-size thread pool.
- **GET method support only:** The server implements and responds to HTTP `GET` requests; other methods receive an appropriate error response.
- **Robust stream reading:** Handles partial reads and edge cases in request parsing, including detection of double `\r\n\r\n` sequences and reading until a full HTTP request header is received.
- **Security controls:** Prevents directory traversal (rejects requests containing `..`) and enforces access control so only files within the server's static content directory may be served.
- **Proper HTTP responses:** Returns correctly formatted HTTP status lines, headers (including appropriate `Content-Type`/MIME types), and well-formed response bodies.

## How to Run

### Prerequisites

- Python 3.x is required.

### Running the server

From the project root, run:

```
python3 server.py
```

This will start the server and begin listening for incoming connections on the configured port.

### Configuration

Server settings such as the listening `PORT` and `THREAD_POOL_SIZE` can be adjusted in [config.py](config.py). Typical settings to check or change:

- `PORT` — TCP port the server listens on.
- `THREAD_POOL_SIZE` — Number of worker threads in the thread pool.

Make sure any changes in [config.py](config.py) are saved before starting the server.

## Demo Video

https://drive.google.com/file/d/1nM1canirS--lan5p2HaGAgzl2QzoT0LM/view?usp=sharing

## Academic Integrity

This project was developed as a mid-term programming assignment for the Computer Networks course.

---

If you would like, I can also:

- Add a short README section with example requests and expected responses.
- Create a minimal test script that performs basic `GET` requests against the running server.
- Commit the README to the repository and prepare a git-friendly commit message.

Let me know which of these you'd like me to do next.
