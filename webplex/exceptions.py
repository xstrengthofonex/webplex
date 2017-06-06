import http.client
from html import escape

class HTTPException(Exception):
    pass

class HTTPError(HTTPException):
    def __init__(self, message, status_code):
        super(HTTPError, self).__init__(message)
        self.message = message
        self.status_code = status_code

    def serve_http(self, request, response):
        response.content_type = "text/plain"
        response.status_int = self.status_code
        response.write(self.message)

class HTTPNotFound(HTTPError):
    def __init__(self, message="404 Page Not Found",
                 status_code=http.client.NOT_FOUND):
        super(HTTPNotFound, self).__init__(status_code, message)


def redirect(request, response, url, status_code):
    response.location = url
    response.cache_control.no_cache = False
    response.status_code = status_code
    if request.method == "GET":
        note = "<a href=\"" + escape(url) + "\">" +\
        http.client.responses[int(status_code)] + "</a>.\n"
        response.write(note)


class HTTPRedirect(HTTPError):
    def __init__(self, url, status_code, message=None):
        super(HTTPRedirect, self).__init__(status_code, message)
        self.url = url

    def serve_http(self, request, response):
        return redirect(request, response, self.url, self.status_code)

