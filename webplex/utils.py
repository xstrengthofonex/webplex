import sys
import posixpath

def load_from_string(string):
    module_name, func_name = string.split(':', 1)
    __import__(module_name)
    module = sys.modules[module_name]
    func = getattr(module, func_name)
    return func

# Return the canonical path for p, eliminating . and .. elements.
def clean_path(path):
    if path == "":
        return "/"
    if path[0] != "/":
        path = "/" + path
    new_path = posixpath.normpath(path)
    if new_path == "//":
        new_path = "/"
    if path.endswith('/') and not new_path.endswith('/'):
        new_path += "/"
    return new_path

# path match pattern
def path_match(pattern, path):
    if len(pattern) == 0:
        return False
    n = len(pattern)
    if pattern.endswith('/'):
        return pattern == path
    return len(path) >= n and path[:n] == pattern

def strip_host_port(host):
    if ":" not in host:
        return host
    host, _ = host.split(':', 1)
    return host