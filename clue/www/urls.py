from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^portal/$', 'django.views.generic.simple.direct_to_template', {'template': 'portal.html'}),
    (r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'index.html'}),
)
