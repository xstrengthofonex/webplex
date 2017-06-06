from string import Template
from urllib.parse import urlencode
from webplex.router import local_request


def render_string(string, **context):
    template = Template(string)
    return template.safe_substitute(**context)


def render_template(filepath, **context):
    with open(filepath, "r") as f:
        contents = f.read()
    return render_string(contents, **context)


def url(*segments, **vars):
    base_url = local_request().application_url
    path = '/'.join(str(s) for s in segments)
    if not path.startswith('/'):
        path = "/" + path
    if vars:
        path += "?" + urlencode(vars)
    return base_url + path
