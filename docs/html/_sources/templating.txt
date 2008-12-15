*********************
Templating in Restish
*********************

``lib/templating.py``
=====================

.. code-block:: python

    def make_renderer(app_conf):
        """
        Create and return a restish.templating "renderer".
        """

        import pkg_resources
        import os.path
        from restish.contrib.makorenderer import MakoRenderer
        return MakoRenderer(
                directories=[
                    pkg_resources.resource_filename('myproject', 'templates')
                    ],
                module_directory=os.path.join(app_conf['cache_dir'], 'templates'),
                input_encoding='utf-8', output_encoding='utf-8',
                default_filters=['unicode', 'h']
                )

