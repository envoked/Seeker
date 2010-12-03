from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'lobby.views.join'),
    (r'^home/$', 'lobby.views.home'),
    (r'^create/$', 'lobby.views.create'),
    (r'^register/$', 'lobby.views.register'),
    (r'^profile/$', 'lobby.views.profile'),
    (r'^profile/(?P<lobby_id>[0-9a-zA-Z.]+)/$', 'lobby.views.profile'),
    (r'^settings/$', 'lobby.views.settings'),
    (r'^(?P<id>[0-9]+)/$', 'lobby.views.lobby'),
    (r'^start_game/(?P<lobby_id>[0-9]+)/$', 'lobby.views.start_game'),
    
    #API
    (r'^messages/send/$', 'lobby.ajax.send_message'),
    (r'^messages/get/$', 'lobby.ajax.get_messages'),
    (r'^members/get/$', 'lobby.ajax.get_members'),
    (r'^get_lobby/$', 'lobby.ajax.get_lobby'),
    (r'^members/invite/$', 'lobby.ajax.invite_member'),
    #for testing
    (r'^members/add_cpu_user/$', 'lobby.ajax.add_cpu_user'),
    (r'^members/remove_member/$', 'lobby.ajax.remove_member')
)
                       