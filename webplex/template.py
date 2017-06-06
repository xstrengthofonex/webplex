from string import Template
import os

class HTMLTemplate(object):
    def __init__(self, base):
        self.base = None
        self.loaded = {}
        self.blocks = {}
        self.partials = {}
        self.set_base(base)

    def load_file(self, filepath):
        content = self.loaded.get(filepath)
        if not content:
            if os.path.exists(filepath) and filepath.endswith('.html'):
                with open(filepath, "r") as f:
                    content = f.read()
                self.loaded[filepath] = content
            else:
                filename = os.path.split(filepath)[-1]
                raise OSError('file %s does not exist' % filename)
        return content

    def set_base(self, filepath):
        self.base = self.load_file(filepath)

    def add_block(self, name, filepath):
        content = self.load_file(filepath)
        self.add_block_string(name, content)

    def add_block_string(self, name, string):
        name = "block_%s" % name
        self.blocks[name] = string

    def add_partial(self, partial_name, filepath, **kwargs):
        content = self.load_file(filepath)
        partial_name = "partial_%s" % partial_name
        partial_template = Template(content)
        partial_string = partial_template.safe_substitute(**kwargs)
        self.add_partial_string(partial_name, partial_string)

    def add_partial_string(self, partial_name, string):
        partial = self.partials.get(partial_name)
        if not partial:
            self.partials[partial_name] = ""
        self.partials[partial_name] += string

    def render(self):
        content = ""
        if self.base is not None:
            base_template = Template(self.base)
            content += base_template.safe_substitute(**self.blocks)
        rendered_template = Template(content)
        content = rendered_template.safe_substitute(**self.partials)
        return content