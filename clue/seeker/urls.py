from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^game/(?P<game_id>[0-9]+)/$', 'seeker.play.game'),
    (r'^game/(?P<game_id>[0-9]+)/complete/$', 'seeker.play.game_complete'),
    (r'^game/(?P<game_id>[0-9]+)/guesser/$', 'seeker.play.guesser'),
    (r'^game/(?P<game_id>[0-9]+)/guess/$', 'seeker.play.guess'),
    (r'^game/(?P<game_id>[0-9]+)/guess_for_cpus/$', 'seeker.play.guess_for_cpus'),
    (r'^game/(?P<game_id>[0-9]+)/quit/$', 'seeker.play.quit'),
    (r'^game/(?P<game_id>[0-9]+)/player/$', 'seeker.play.clues_for_player'),
    (r'^game/(?P<game_id>[0-9]+)/clues/$', 'seeker.play.clues'),
    
    (r'^game/(?P<game_id>[0-9]+)/alerts/$', 'seeker.play.alerts'),
    (r'^game/(?P<game_id>[0-9]+)/alert/viewed/$', 'seeker.play.alert_viewed'),
    (r'^game/(?P<game_id>[0-9]+)/debug_clues/$', 'seeker.play.debug_clues'),
    (r'^game/show_notification/(?P<text>[_0-9a-zA-Z.]+)/$', 'seeker.play.show_notification'),
)