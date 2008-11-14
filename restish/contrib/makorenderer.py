from mako.lookup import TemplateLookup


class MakoRenderer(object):

    def __init__(self, *a, **k):
        self.lookup = TemplateLookup(*a, **k)

    def __call__(self, template, args={}):
        return self.lookup.get_template(template).render(**args)

