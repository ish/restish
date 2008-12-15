**************************
An Introduction to Restish
**************************

Restish is a minimal but fully formed rest oriented wsgi web framework.

Why Restish?
============

Background
----------

We were looking around for a web framework for a new project. Previously we had
worked with Twisted and Nevow and had developed the Formal form handling
library for it. However for this project we wanted something that would be a
little more accessible and that would allow us to make use of the full range of
libraries has to offer. The three obvious frameworks were pylons, turbogears
and django. We wanted to use SqlAlchemy and hence Django wasn't really a
contender. Turbogears looked in a s tate of flux and we were looking for
something a lot lower level. So by process of elimination we h ad to look at
pylons.

Pylons started out looking quite good but we started to find the odd problem.
The initial problem w as pylon's use of threadlocals. Using threadlocals
precludes any use of single threaded servers. So we removed threadlocals. Next
we started to make pylons more templating agnostic, eventually removing
templating completely. Finally, when we had removed all trace of pylons, we
realised what we had was a new lightweight web framework. 

Advantages & Disadvantages
--------------------------

The advantages that restish has are 

* Well tested and powerful url handling, parsing and creation
* Simple integration with templating frameworks
* Powerful but simple http request and response handling

The three libraries we have used in the creation of restsh are paste (for
initial project template creation), decorator (used to decorate methods as
children or http handlers and for adding page templating) and webob (for it's
http.request and response)

.. note::  Matt: Add some notes here on the whys behind restish?? I don't know enough about what you did to write anything


How to start a restish project
==============================

Using paster create
-------------------

First you use paste with a 'restish' template:: 

  $ paster create --template=restish

This will create a basic, minimal restish project::

   paster create --template=restish
    Selected and implied templates:
      restish#restish  Template for creating a basic Restish package
    Enter project name: myproject 
    Variables:
      egg:      myproject
      package:  myproject
      project:  myproject
    Creating template restish
    Creating directory ./myproject
      Recursing into +package+
        Creating ./myproject/myproject/
        Copying __init__.py to ./myproject/myproject/__init__.py
        Recursing into lib
          Creating ./myproject/myproject/lib/
          Copying __init__.py to ./myproject/myproject/lib/__init__.py
          Copying guard.py to ./myproject/myproject/lib/guard.py
          Copying templating.py_tmpl to ./myproject/myproject/lib/templating.py
        Recursing into public
          Creating ./myproject/myproject/public/
          Copying index.html_tmpl to ./myproject/myproject/public/index.html
        Recursing into resource
          Creating ./myproject/myproject/resource/
          Copying __init__.py to ./myproject/myproject/resource/__init__.py
          Copying root.py_tmpl to ./myproject/myproject/resource/root.py
        Copying wsgiapp.py_tmpl to ./myproject/myproject/wsgiapp.py
      Copying +package+.ini_tmpl to ./myproject/myproject.ini
      Copying development.ini_tmpl to ./myproject/development.ini
      Copying live.ini_tmpl to ./myproject/live.ini
      Copying setup.py_tmpl to ./myproject/setup.py
    Running /Users/timparkin/py/bin/python setup.py egg_info
    Manually creating paster_plugins.txt (deprecated! pass a paster_plugins keyword to setup() instead)
    Adding Restish to paster_plugins.txt


What is in the template project
-------------------------------

The files in this project are as follows::

    .
    |-- development.ini
    |-- live.ini
    |-- myproject
    |   |-- __init__.py
    |   |-- lib
    |   |   |-- __init__.py
    |   |   |-- guard.py
    |   |   `-- templating.py
    |   |-- public
    |   |   `-- index.html
    |   |-- resource
    |   |   |-- __init__.py
    |   |   `-- root.py
    |   `-- wsgiapp.py
    |-- myproject.egg-info
    |   |-- PKG-INFO
    |   |-- SOURCES.txt
    |   |-- dependency_links.txt
    |   |-- entry_points.txt
    |   |-- not-zip-safe
    |   |-- paster_plugins.txt
    |   |-- requires.txt
    |   `-- top_level.txt
    |-- myproject.ini
    `-- setup.py

We'll simplify that a bit in order to describe what we have in the actual project::

    .
    |-- myproject.ini
    |-- development.ini
    |-- live.ini
    |
    |-- myproject
    |   |-- lib
    |   |   |-- guard.py
    |   |   `-- templating.py
    |   |-- public
    |   |   `-- index.html
    |   |-- resource
    |   |   `-- root.py
    |   `-- wsgiapp.py

The ini files are paste configuration files and setup up the project. There is
a base configuration file that contains project settings and then there are two
deployment files, live and development, which contain information on how to
serve the project. 

The project itself has three directories. 

The ``lib`` directory
^^^^^^^^^^^^^^^^^^^^^

The lib directory has an example authenticator called 'guard.py' and a sample
templating package which shows how to setup templating with Mako, Genshi or
Jinja.

We tend to put most of our project library code in here.

The ``public`` directory
^^^^^^^^^^^^^^^^^^^^^^^^

The public directory is used to serve static resources in preference to any
dynamic resources. The sample index.html just contains some information on what
the file is for.

A typical use for this would be to have a css, images and js directory
underneath with your assets in. Placing files directly inside public will also
make them available on root of your website, useful for favicons, google
analytics files, etc.

The ``resource`` directory
^^^^^^^^^^^^^^^^^^^^^^^^^^

The resource directory contains our root resource. This is the first file that
will handle any requests.

Finally, our wsgiapp.py can be used to wire up any other wsgi applications,
such as cookies, authentication, etc.

Let's take a look at the resource first as that is where the fun stuff is.. 

Starting a server
-----------------

Your can start your example project right now by using the command::

  $ paster serve development.ini

Which should return the following::

  $ paster serve development.ini
  Starting server in PID 22237.
  serving on http://127.0.0.1:8080

Next Steps..
------------

Next we'll talk about how to build resources and use templating...

