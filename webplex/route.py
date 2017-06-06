import re
import six
from abc import ABCMeta, abstractmethod

@six.add_metaclass(ABCMeta)
class BaseRoute(object):

    @abstractmethod
    def match(self, request):
        pass

class Route(BaseRoute):
    default_methods = ['GET']
    def __init__(self, path, handler, methods=None, action=None, name=None):
        self.path = path
        self.handler = handler
        self.regex = re.compile(template_to_regex(path))
        self.urlvars = {}
        self.action = action
        self.name = name

        if methods is None:
            self.methods = self.default_methods
        else: self.methods = methods

    def match(self, request):
        if request.method in self.methods:
            match = self.regex.match(request.path)
            if match:
                self.urlvars.update(match.groupdict())
                request.urlvars.update(self.urlvars)
                request.route = self
                return True
        return False


var_regex = re.compile(r'''
    \{             # The exact character "{"
    (\w+)          # The variable name {restricted to a-z, 0-9, _}
    (?::([^}]+))?  # The optional :regex part
    \}             # The exact character "}"
    ''', re.VERBOSE)

def template_to_regex(template):
    regex = ''
    last_pos = 0
    for match in var_regex.finditer(template):
        regex += re.escape(template[last_pos:match.start()])
        var_name = match.group(1)
        expr = match.group(2) or '[^/]+'
        expr = '(?P<%s>%s)' % (var_name, expr)
        regex += expr
        last_pos = match.end()
    regex += re.escape(template[last_pos:])
    regex = "^%s$" % regex
    return regex
