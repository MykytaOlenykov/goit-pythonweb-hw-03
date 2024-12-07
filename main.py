from http import HTTPStatus
from http.server import HTTPServer


from server import HttpResponse, HttpRequestHandler
from forms import MessageForm
from repositories import messages_repository, courses_repository


nav_menu = {"/": "Home", "/message": "Send message"}


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


@HttpRequestHandler.register_route("/read", "GET")
def messages_list(request: HttpRequestHandler):
    messages = messages_repository.get_all()
    context = {"nav_menu": nav_menu, "messages": messages}
    request.render_template("messages-list.html", context)


def run(server_class=HTTPServer, handler_class=HttpRequestHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)

    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()
