import inspect
import threading

import six
from webob import Request, Response

from webplex.route import Route, BaseRoute
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

    def __init__(self, routes=()):
        self.routes = []
        self.named_routes = dict()

        for route in routes:
            self.add_route(route)

    def handle(self, path, handler, methods=None, action=None, name=None):
        if path[0] != "/":
            # implicitly add a slash to the start of the path
            path = "/" + path
        if isinstance(handler, six.string_types):
            # load the handler from a string
            handler = load_from_string(handler)
        if inspect.isfunction(handler):
            # use the HandlerFunc wrapper for function based handlers
            handler = HandlerFunc(handler)
        if not isinstance(handler, BaseHandler):
            raise TypeError("handlers must be a subclass of BaseHandler")
        route = Route(path=path, handler=handler, methods=methods,
                      action=action, name=name)
        self.add_route(route)

    def add_route(self, route):
        if isinstance(route, BaseRoute):
            if route.name is not None:
                if not self.named_routes.get(route.name):
                    self.named_routes[route.name] = route
                else:
                    raise KeyError('named route is already registered')
            self.routes.append(route)

    def get(self, path, handler, action=None, name=None):
        """Shortcut for GET handle"""
        self.handle(path, handler, action=None,
                    name=None, methods=['GET'])

    def post(self, path, handler, action=None, name=None):
        """Shortcut for POST handle"""
        self.handle(path, handler, action=None,
                    name=None, methods=["POST"])

    def head(self, path, handler, action=None, name=None):
        """Shortcut for HEAD handle"""
        self.handle(path, handler,action=None,
                    name=None, methods=["HEAD"])

    def options(self, path, handler, action=None, name=None):
        """Shortcut for OPTIONS handle"""
        self.handle(path, handler, action=None,
                    name=None, methods=["OPTIONS"])

    def put(self, path, handler, action=None, name=None):
        """Shortcut for PUT handle"""
        self.handle(path, handler, action=None,
                    name=None, methods=["PUT"])

    def patch(self, path, handler, action=None, name=None):
        """Shortcut for PATCH handle"""
        self.handle(path, handler, action=None,
                    name=None, methods=["PUT"])

    def delete(self, path, handler, action=None, name=None):
        """Shortcut for DELETE handle"""
        self.handle(path, handler, action=None,
                    name=None, methods=["DELETE"])

    def match(self, request):
        for route in self.routes:
            if route.match(request):
                return route.handler
        raise exc.HTTPNotFound()

    @staticmethod
    def adapt_handler(handler):
        if isinstance(handler, Handler):
            # Handler classes instance must be initiated
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



