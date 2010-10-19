from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'lobby.views.join'),
    (r'^create/$', 'lobby.views.create'),
    (r'^register/$', 'lobby.views.register'),
    (r'^(?P<id>[0-9]+)/$', 'lobby.views.lobby'),
    
    #API
    (r'^messages/send/$', 'lobby.ajax.send_message'),
    (r'^messages/get/$', 'lobby.ajax.get_messages'),
    (r'^members/get/$', 'lobby.ajax.get_members'),
)
                       