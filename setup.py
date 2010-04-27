from setuptools import setup, find_packages
import sys, os

version = '0.11'

setup(name='restish',
      version=version,
      description="WSGI framework/library for building resource- and rest- oriented web sites",
      long_description="""\
Restish is a simple to use, lightweight WSGI web framework and library with a
strong focus on resources, request/response, URLs and content negotiation.
Restish has very few dependencies and does not assume any particular templating
or database engine.

      Changlog at `http://github.com/ish/restish/raw/master/CHANGELOG <http://github.com/ish/restish/raw/master/CHANGELOG>`_

""",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Web Environment",
          "Framework :: Paste",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
          "Topic :: Internet :: WWW/HTTP :: WSGI",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='web wsgi rest framework',
      author='ish',
      author_email='developers@ish.io',
      url='http://ish.io/projects/show/restish',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'decorator',
          'mimeparse',
          'WebOb',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.paster_create_template]
      restish = restish.pastertemplate:RestishTemplate
      """,
      test_suite="restish.tests",
      tests_require=['WebTest', 'Jinja2', 'mako', 'Genshi', 'Tempita', 'Django'],
      )
