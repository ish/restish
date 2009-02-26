"""
Tempita templating renderer that loads a template via a configurable loader.

A TempitaRenderer instance can be used as the renderer passed to the
templating.Templating instance that is added to the WSGI environ.
"""

import os.path
import tempita


class TempitaRenderer(object):

    def __init__(self, loader):
        self.loader = loader

    def __call__(self, template, args, encoding):
        template = self.loader.get_template(template)
        output = template.substitute(**args)
        if encoding is None:
            return output
        return output.encode(encoding)


class TempitaFileSystemLoader(object):

    def __init__(self, directory, encoding='utf-8'):
        self.directory = directory
        self.encoding = encoding

    def get_template(self, template):
        filename = os.path.join(self.directory, template)
        return tempita.Template.from_filename(filename, encoding=self.encoding)

