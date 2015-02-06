from setuptools import setup, find_packages
import codecs

# Get the long description from the relevant file
with codecs.open('README', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='restish',

    version='0.13.2',

    description="WSGI framework/library for building resource- and rest- oriented web sites",
    long_description=long_description,

    url='http://ish.io/projects/show/restish',

    author='ish',
    author_email='developers@ish.io',

    license='BSD',

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

    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    package_data={
        'restish': ['restish/pastertemplate/*'],
    },
    zip_safe=False,

    install_requires=[
        # -*- Extra requirements: -*-
        'mimeparse>=0.1.3',
        'WebOb',
    ],

    test_suite="restish.tests",
    tests_require=['WebTest', 'Jinja2', 'mako', 'Genshi', 'Tempita', 'Django'],

    entry_points="""
    # -*- Entry points: -*-
    [paste.paster_create_template]
    restish = restish.pastertemplate:RestishTemplate
    """,
)
