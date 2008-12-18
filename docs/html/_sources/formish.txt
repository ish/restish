****************************
Using Formish within Restish
****************************

Introduction
============

Formish is a forms library that was developed in parralel with Restish, although the library itself can be used completely independently. Formish started life as formal, a form library written for Twisted/Nevow. The goal of the project was to create a simple forms library that allowed separation of the component parts such as schema, widgets, validation, data conversion and templates. The result is a suite of components formish, validatish, convertish and schemaish. These can all be used independently but work seamlessly when needed. 

Using a simple form withing Restish
===================================

We'll start off with one of the examples from the Formish documentation. 

.. code-block:: python

    class SimpleSchema(schemaish.Structure):
        """ A simple sommets form """
        email = schemaish.String(validator=schemaish.All(schemaish.NotEmpty, schemaish.Email))
        first_names = schemaish.String(validator=schemaish.NotEmpty)
        last_name = schemaish.String(validator=schemaish.NotEmpty)
        comments = schemaish.String()


    def get_form():
        """ Creates a form and assigns a widget """
        form = formish.Form(SimpleSchema())
        form['comments'].widget = formish.TextArea()
        return form  


    class Root(resource.Resource):
        """ Our form resource """

        @resource.GET()
        @templating.page('test.html')
        def html(self, request, form=None):
            """
            If the form is None then we get a clean form, otherwise show the
            form that was passsed back from an unsuccessful POST
            """
            if form is None:
                form = get_form()
            return {'form': form}

        @resource.POST()
        def POST(self, request):
            """
            Get a clean form and validate it against the request data that was
            submitted. Errors pass the form (with attached errors) back up to
            the page renderer. Success shows a thanks page (typically you would
            redirect here.
            """
            form = get_form()
            try:
                data = form.validate(request)
            except formish.FormError, e:
                return self.html(request, form)
            return self.thanks(request,data)

        @templating.page('thanks.html')
        def thanks(self, request, data):
            """ Just show the data """
            return {'data': data}


We need to have the following in the ``test.html`` file

.. code-block:: html
 
    <div id="formbox">
      ${form()|n}
    </div>

The steps when this form is created are as follows

1. Get a copy of the form and put it on the page
2. When POST'd, validate the returned request data. If this raises an exception, errors will have been bound to the form instance. 
3. (On Error): Pass the form with bound errors back up the page renderer.
4. (On Success): Show a thanks page.

We can also pass the success and failure callables to the validate function to simplify the form handling.

.. code-block:: python

    class Root(resource.Resource):

        @resource.GET()
        @templating.page('test.html')
        def html(self, request, form=None):
            if form is None:
                form = get_form()
            return {'form': form}

        @resource.POST()
        def POST(self, request):
            return get_form().validate(request, self.html, self.thanks)

        @templating.page('thanks.html')
        def thanks(self, request, data):
            return {'data': data}


Multiple Actions on a Form
==========================

If we have more than one action on a form


.. code-block:: python

    class Root(resource.Resource):

        def get_form(self):
            form = formish.Form( ('email', schemaish.String()) )
            form.addAction(self.check_email_domain, 'check')
            form.addAction(self.send_test_email, 'test')
            return form

        def check_email_domain(self, request, data):
            """ Check the domain has an MX or A record """

        def send_test_email(self, request, data):
            """ Send a test email to this address """

        @resource.GET()
        @templating.page('test.html')
        def html(self, request, form=None):
            if form is None:
                form = self.get_form()
            return {'form': form}

        @resource.POST()
        def POST(self, request):
            form = self.get_form()
            return form.validate(request, self.html, form.action)

Here we have pass the ``form.action`` method as the success callable. The whatever is in ``form.action`` (for example, ``check_email_domain``) is called with ``(request, data)``.



Multiple Forms on a Page
========================

If we have more than one form on a page, we can use the utility function, ``form_in_request`` to find out which one was posted.


.. code-block:: python

    class Root(resource.Resource):

        ##
        # Forms

        def _email_form(self):
            return formish.Form( ('email', schemaish.String()), name='email' )

        def _domain_form(self):
            return formish.Form( ('domain', schemaish.String()), name='domain' )

        ##
        # Form Handling

        def _POST_email(self, request):
            form = self._email_form()
            return form.validate(request, self.html, self.thanks)

        def _POST_domain(self, request):
            form = self._domain_form()
            return form.validate(request, self.html, self.thanks)

        ##
        # GET, POST, templating and thanks

        @resource.GET()
        def GET(self, request):
            return self.html(request)

        @resource.POST()
        def POST(self, request):
            handlers = {'email': self._POST_email, 'domain': self._POST_domain}
            return handlers[formish.form_in_request(request)](request)

        @templating.page('forms.html')
        def html(self, request, form=None):
            form_name = formish.form_in_request(request)
            form = {form_name: form}
            if form_name is not 'email':
                form['email'] = self._email_form()
            if form_name is not 'domain':
                form['domain'] = self._domain_form()
            return {'forms': forms}

        @templating.page('thanks.html')
        def thanks(self, request, data):
            pass

We could simplify this further, although I'm not sure this is quite as readable.. 

.. code-block:: python

    class Root(resource.Resource):

        def form(self,name):
            if name is 'email': 
                return formish.Form( ('email', schemaish.String()), name='email' )
            if name is 'domain':
                return formish.Form( ('domain', schemaish.String()), name='domain' )

        @resource.GET()
        def GET(self, request):
            return self.html(request)

        @resource.POST()
        def POST(self, request):
            form_name = formish.form_in_request(request)
            return self.form(name).validate(request, self.html, self.thanks)

        @templating.page('forms.html')
        def html(self, request, form=None):
            form_name = formish.form_in_request(request)
            form = {form_name: form}
            # Check each form, if it isn't the one passed in then fetch it.
            for f in ['email','domain']:
                if form_name is not f:
                    form[f] = self.form(f)
            return {'forms': forms}

        @templating.page('thanks.html')
        def thanks(self, request, data):
            pass
