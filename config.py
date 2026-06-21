import os

HOST = "0.0.0.0"
PORT = 8080
BUFFER_SIZE = 4096
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
DEFAULT_PAGE = "/index.html"
HTTP_VERSION = "HTTP/1.0"

CONTENT_TYPES = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".gif": "image/gif",
    ".txt": "text/plain",
}
DEFAULT_CONTENT_TYPE = "application/octet-stream"

ALLOWED_SUBDIRS = {"css", "js", "images"}
