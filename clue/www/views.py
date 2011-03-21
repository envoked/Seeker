from django.views.generic.simple import direct_to_template
from django.http import Http404

def staticpage(request, page_name):
    # Use some exception handling, just to be safe
    try:
        return direct_to_template(request, '%s.html' % (page_name, ))
    except TemplateDoesNotExist:
        raise Http404
