from http import HTTPStatus
from http.server import BaseHTTPRequestHandler


class HttpResponse:
    def __init__(
        self, content="", status=HTTPStatus.OK, content_type="text/html", headers=None
    ):
        self.content = content.encode("utf-8") if isinstance(content, str) else content
        self.status = status
        self.content_type = content_type
        self.headers = headers or {}

    def send(self, request: BaseHTTPRequestHandler):
        request.send_response(self.status)
        request.send_header("Content-type", self.content_type)

        for key, value in self.headers.items():
            request.send_header(key, value)

        request.end_headers()
        request.wfile.write(self.content)
