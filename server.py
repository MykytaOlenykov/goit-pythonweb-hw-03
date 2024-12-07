import urllib.parse
import mimetypes
import pathlib

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader


ROOT_PATH = pathlib.Path().joinpath()
TEMPLATES_PATH = ROOT_PATH / "templates"


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


class HttpRequestHandler(BaseHTTPRequestHandler):
    env = Environment(loader=FileSystemLoader("templates"))

    routes = {}

    @classmethod
    def register_route(cls, path, method):
        def wrapper(func):
            cls.routes[(path, method)] = func
            return func

        return wrapper

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)

        if pr_url.path.startswith("/static/"):
            self.send_static()
        else:
            handler = self.routes.get((pr_url.path, "GET"))
            if handler:
                handler(self)
            else:
                self.handle_404()

    def do_POST(self):
        pr_url = urllib.parse.urlparse(self.path)
        handler = self.routes.get((pr_url.path, "POST"))
        if handler:
            data = self.rfile.read(int(self.headers["Content-Length"]))
            data_parse = urllib.parse.unquote_plus(data.decode())
            data_dict = dict(el.split("=") for el in data_parse.split("&"))
            handler(self, data_dict)
        else:
            self.handle_404()

    def render_template(self, template_name, context=None, status=HTTPStatus.OK):
        template = self.env.get_template(template_name)
        content = template.render({"request": self, **(context or {})})

        response = HttpResponse(content, status)
        response.send(self)

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        self.send_header("Content-type", mt[0] or "text/plain")
        self.end_headers()

        with open(ROOT_PATH / f".{self.path}", "rb") as file:
            self.wfile.write(file.read())

    def handle_404(self):
        response = HttpResponse("Not found", status=HTTPStatus.NOT_FOUND)
        response.send(self)
