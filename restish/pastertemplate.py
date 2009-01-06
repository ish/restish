from paste.script import templates


class RestishTemplate(templates.Template):
    """
    Configure the paster template
    """
    egg_plugins = ['Restish']
    summary = "Template for creating a basic Restish package"
    _template_dir = 'pastertemplate'

