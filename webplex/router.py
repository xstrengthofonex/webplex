import inspect
import sys
import threading
from string import Template
from urllib.parse import urlencode

import six
from webob import Request, Response

from webplex.route import Route


class Local(object):
    def __init__(self):
        self.local = threading.local()

    def register(self, obj):
        self.local.obj = obj

    def unregister(self):
        del self.local.obj

    def __call__(self):
        try:
            return self.local.obj
        except AttributeError:
            raise TypeError("No object has been registered")

local_request = Local()


class HTTPException(Exception):
    pass

class HTTPError(HTTPException):
    def __init__(self, status_code, message):
        super(HTTPError, self).__init__(message)
        self.message = message
        self.status_code = status_code

    def serve_http(self, request, response):
        response.status_int = self.status_code
        response.write(self.message)

class HTTPNotFound(HTTPError):
    def __init__(self, message="404 Not Found", status_code=404):
        super(HTTPNotFound, self).__init__(status_code, message)


class HandlerFunc(object):
    def __init__(self, func):
        self.func = func

    def serve_http(self, request, response):
        return self.func(request, response)

def render_string(string, **context):
    template = Template(string)
    return template.safe_substitute(**context)


def render_template(filepath, **context):
    with open(filepath, "r") as f:
        contents = f.read()
    return render_string(contents, **context)


class Handler(object):
    def __init__(self, request=None, response=None):
        """request and response is set in serve_http"""
        self.request = request
        self.response = response

    def serve_http(self, request, response):
        self.request = request
        self.response = response

        action = self.request.route.action
        if not action:
            action = self.request.method.lower()
        try:
            method = getattr(self, action)
        except AttributeError:
            raise HTTPNotFound('No action for {}'.format(action))
        return method(**request.urlvars)


class HTTPRouter(object):
    request_class = Request
    response_class = Response

    def __init__(self):
        self.routes = []

    def handle(self, methods, path, handler):
        if path[0] != "/":
            raise HTTPException("path must begin with '/' in path")
        if isinstance(handler, six.string_types):
            handler = load_from_string(handler)
        if inspect.isfunction(handler):
            handler = HandlerFunc(handler)
        self.add_route(path, handler, methods)


    def add_route(self, path, handler, methods=None, action=None):
        """Adds a new route with a default GET method"""
        route = Route(path, handler, methods, action)
        self.routes.append(route)

    def get(self, path, handler):
        self.handle(["GET"], path, handler)

    def post(self, path, handler):
        self.handle(["POST"], path, handler)

    def head(self, path, handler):
        self.handle(["HEAD"], path, handler)

    def options(self, path, handler):
        self.handle(["OPTIONS"], path, handler)

    def put(self, path, handler):
        self.handle(["PUT"], path, handler)

    def patch(self, path, handler):
        self.handle(["PATCH"], path, handler)

    def delete(self, path, handler):
        self.handle(["DELETE"], path, handler)

    def match(self, request):
        for route in self.routes:
            if route.match(request):
                return route.handler
        raise HTTPNotFound()

    @staticmethod
    def adapt_handler(handler):
        if not isinstance(handler, HandlerFunc):
            handler = handler()
        return handler

    def dispatch(self, request, response):
        try:
            handler = self.match(request)
            adapted_handler = self.adapt_handler(handler)
            adapted_handler.serve_http(request, response)
        except HTTPError as error:
            error.serve_http(request, response)


    def __call__(self, environ, start_response):
        request = self.request_class(environ)
        response = self.response_class()
        local_request.register(request)
        self.dispatch(request, response)
        try:
            return response(environ, start_response)
        finally:
            local_request.unregister()

def url(*segments, **vars):
    base_url = local_request().application_url
    path = '/'.join(str(s) for s in segments)
    if not path.startswith('/'):
        path = "/" + path
    if vars:
        path += "?" + urlencode(vars)
    return base_url + path


def load_from_string(string):
    module_name, func_name = string.split(':', 1)
    __import__(module_name)
    module = sys.modules[module_name]
    func = getattr(module, func_name)
    return func
