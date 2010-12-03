from django.conf.urls.defaults import *
from django.contrib.comments.urls import *
#git
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^$', 'lobby.views.index'),
    (r'^lobby/', include('clue.lobby.urls')),
    (r'^up/', include('clue.userprofile.urls.en')),
    (r'^facebook/', include('facebookconnect.urls')),
    (r'^seeker/', include('clue.seeker.urls')),
    (r'^login/$', 'lobby.views.login'),
    (r'^logout/$', 'lobby.views.logout'),
    (r'^accounts/profile/$', 'lobby.views.profile'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
