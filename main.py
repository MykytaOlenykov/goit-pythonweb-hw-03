import urllib.parse
import mimetypes
import pathlib

from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader

from server import HttpResponse
from forms import MessageForm
from repositories import messages_repository, courses_repository


ROOT_PATH = pathlib.Path().joinpath()
TEMPLATES_PATH = ROOT_PATH / "templates"

nav_menu = {"/": "Home", "/message": "Send message"}


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
        handler = self.routes.get((pr_url.path, "GET"))

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


def handle_404(request: HttpRequestHandler):
    context = {"nav_menu": nav_menu}
    request.render_template("error.html", context, status=HTTPStatus.NOT_FOUND)


HttpRequestHandler.handle_404 = handle_404


@HttpRequestHandler.register_route("/", "GET")
def index(request: HttpRequestHandler):
    courses = courses_repository.get_all()
    context = {"nav_menu": nav_menu, "courses": courses}
    request.render_template("index.html", context)


@HttpRequestHandler.register_route("/message", "GET")
def message_form(request: HttpRequestHandler):
    form = MessageForm()
    context = {"nav_menu": nav_menu, "form": form}
    request.render_template("message.html", context)


@HttpRequestHandler.register_route("/message", "POST")
def create_message(request: HttpRequestHandler, body):
    form = MessageForm(body)

    if form.is_valid():
        messages_repository.create(form.get_clean_data())
        response = HttpResponse(status=HTTPStatus.FOUND, headers={"Location": "/"})
        response.send(request)
    else:
        context = {
            "nav_menu": nav_menu,
            "form": form,
        }
        request.render_template("message.html", context, status=HTTPStatus.BAD_REQUEST)


def run(server_class=HTTPServer, handler_class=HttpRequestHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)

    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()
