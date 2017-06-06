import six
from abc import ABCMeta, abstractmethod

from webplex import exceptions as exc


@six.add_metaclass(ABCMeta)
class BaseHandler(object):
    """The Abstract class for all Handlers"""
    @abstractmethod
    def serve_http(self, request, response):
        pass


class Handler(BaseHandler):
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
            raise exc.HTTPNotFound('No action for {}'.format(action))

        resp = method(**request.urlvars)
        if isinstance(resp, six.string_types):
            self.response.write(resp)


class HandlerFunc(BaseHandler):
    def __init__(self, func):
        self.func = func

    def serve_http(self, request, response):
        return self.func(request, response)