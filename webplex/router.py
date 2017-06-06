import inspect
import threading

import six
from webob import Request, Response

from webplex.route import Route
from webplex import exceptions as exc
from webplex.handlers import  BaseHandler, HandlerFunc, Handler
from webplex.utils import load_from_string

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


class HTTPRouter(object):
    request_class = Request
    response_class = Response

    def __init__(self):
        self.routes = []
        self.named_routes = dict()

    def handle(self, methods, path, handler):
        if path[0] != "/":
            raise exc.HTTPException("path must begin with '/'")
        if isinstance(handler, six.string_types):
            handler = load_from_string(handler)
        if inspect.isfunction(handler):
            handler = HandlerFunc(handler)
        if not isinstance(handler, BaseHandler):
            raise TypeError("handlers must be a subclass of BaseHandler")
        self.add_route(path, handler, methods)


    def add_route(self, path, handler, methods=None, action=None, name=None):
        """
           Arguments are used to construct a new Route instance
           If route is valid it is appended to the routes list
           If route_name is given route is also added to named_routes list
        """
        route = Route(path=path, handler=handler, methods=methods,
                      action=action, name=name)
        if route.is_valid():
            if route.name is not None:
                self.named_routes[route.name] = route
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
        raise exc.HTTPNotFound()

    @staticmethod
    def adapt_handler(handler):
        if isinstance(handler, Handler):
            handler = handler()
        return handler

    def dispatch(self, request, response):
        try:
            handler = self.match(request)
            adapted_handler = self.adapt_handler(handler)
            adapted_handler.serve_http(request, response)
        except exc.HTTPError as error:
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



