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
        template = template.lstrip('/')
        filename = os.path.join(self.directory, template)
        return self._get_template(filename)

    def _get_template(self, filename):
        filename = os.path.abspath(filename)
        if os.path.commonprefix([filename, self.directory]) != self.directory:
            raise Exception("Illegal template: outside template directory")
        return tempita.Template.from_filename(filename, encoding=self.encoding,
                                              get_template=self._tempita_get_template)

    def _tempita_get_template(self, name, from_template):
        if name.startswith('/'):
            basedir = self.directory
            name = name.lstrip('/')
        else:
            basedir = os.path.dirname(from_template.name)
        filename = os.path.join(basedir, name)
        return self._get_template(filename)

