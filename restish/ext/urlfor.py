"""
Create a canonical URL (permalink) for a resource.

Status: utterly experimental, don't use.


Example:

    class NewsItem(Resource):
        pass

    class News(Resource):
        news_item = child('{id}', NewsItem)

    class Root(Resource):
        news = child('news', News)


That will add News and NewsItem to the registry allowing url_for(request, News)
(producing a URL of /news) *and* assign @resource.child-decorated methods with
a simple, default implementation to Root.news and News.news_item.


Thoughts, Ideas and Notes
-------------------------

Warning: some of these are likely to contradict others.

--

Why use AddOns? Because I'm not convinced a URL registry of this sort can ever
fully support restish's flexibility.

Integrating this directly into the Resource base class *at this stage* will
almost certainly mean a lot of untangling of code later. Of course, if it turns
out to work just fine then we can look at full integration.

Changing the core restish code to better support something like this is just
fine as long as it doesn't limit restish at the same time.

--

Ambiguous "root" resource. Any Resource that has no parent will look like it's
at the root of the application. We should probably raise an error if the
Resource has not been wired up using this extension.

Perhaps some of this behaviour really belongs to the application. Also, I've
got an idea for application "plugins" in mind - a collection of resources
packaged as a drop-in component (a little like a Django application I guess).
Perhaps the plugin would be an even better place than the application?

--

Limits a resource type to only appearing once in the hierarchy (can only have
one parent). Not a problem, just a limitation that must be documented. Should
also raise an error if the developer tries to add a Resource to multiple
points in the resource tree.

--

Probably not that useful in its current form, especially for templating where
it will probably be most useful. e.g. how often are are the resource types
going to be available in the template?

--

I can see the need for named reverse URLs and to be able to create a URL for
whatever the template has a reference to.

    url_for('faq') -- useful for very fixed resources
    url_for('blog_post', 3) -- same as 'faq', but with an arg
    url_for(some_instance) -- permalink kind of thing

In fact, wouldn't the name by more useful than the resource type in general? No
problem having both, i.e. registering something with multiple keys, e.g. name
and class.

I can't help but feel this is calling out for a generic function!

--

Need to pass args to url_for() and we'll need to parse @child matchers for
{...} segments somehow so that url_for() can construct the URL correctly. Do we
need to worry about a constructed URL contains query params (probably not)?

--

No explicit child function anymore (an automatically generated one is
automagically added), so the resource type can only pass string args to the
registered Resource's initialiser.  I think the args would need to kwargs too
as {matcher} segments are named.

--

How do we actually pass {matched} args to resource types, just pass the
**kwargs through? 

--

It feels like there's a big overlap with URI templates here. I've been thinking
about adding support for those (in some way) for a while. Problem, is I'm not
sure URI template patterns will make good @child matchers.

    http://bitworking.org/projects/URI-Templates/

--

I think the root resource of the application has to be involved everytime.
Otherwise, there's only a partial path to the application root.

--

Adding a resource hierarchy (say from a different package) that uses this
technique to another application could cause ambiguity, especially if allowed
to use names instead of classes.

--

This whole thing feels like working out the correct compromise between
flexibility and control vs DRY. restish must remain on the flexible end but
it's ok for an extension like this to remove some flexibility in favour of
simplicity.

"""

__all__ = ['child', 'url_for']

from peak.util import addons
from restish import resource


def child(matcher, cls):
    """
    Register the resource type, cls, as the factory for a resource's child that
    matches the matcher.
    """
    registry = ChildRegistry.for_enclosing_class()
    registry.register(matcher, cls)
    def child_method(self, request, segments, *a, **k):
        return cls(*a, **k)
    return resource.child(matcher)(child_method)


def url_for(request, cls):
    """
    Construct an absolute URL for the resource type, cls.
    """
    parents = []
    registry = ChildRegistry(cls)
    while True:
        if registry.parent is None:
            break
        parent_registry = ChildRegistry(registry.parent)
        parents.append(parent_registry.by_class[cls])
        cls, registry = registry.parent, parent_registry
    if not parents:
        parents = ['']
    else:
        parents.reverse()
    return request.application_path.child(*parents)


class ChildRegistry(addons.ClassAddOn):

    def __init__(self, subject):
        self.parent = None
        self.by_matcher = {}
        self.by_class = {}
        addons.ClassAddOn.__init__(self, subject)

    def created_for(self, subject):
        for cls in self.by_class:
            ChildRegistry(cls).parent = subject

    def register(self, matcher, cls):
        self.by_matcher[matcher] = cls
        self.by_class[cls] = matcher

