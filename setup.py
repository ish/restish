from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='restish',
      version=version,
      description="WSGI library for resource- and rest- oriented web sites",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Matt Goodall',
      author_email='matt@jdi-associates.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'decorator',
          'WebOb',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
