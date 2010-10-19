from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^join/$', 'lobby.views.join'),
    (r'^create/$', 'lobby.views.create'),
    (r'^register/$', 'lobby.views.register'),
    (r'^login/$', 'lobby.views.login'),
    (r'^logout/$', 'lobby.views.logout'),
    
    (r'^messages/send/$', 'lobby.ajax.send_message'),
    (r'^messages/get/$', 'lobby.ajax.get_messages'),
    
    (r'^(?P<id>[0-9]+)/$', 'lobby.views.lobby')
    
)
                       