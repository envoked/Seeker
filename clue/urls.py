from django.conf.urls.defaults import *
from django.contrib.comments.urls import *
#git
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
    (r'^lobby/', include('clue.lobby.urls')),
    (r'^userprofile/', include('clue.userprofile.urls.en')),
    (r'^facebook/', include('facebookconnect.urls')),
    (r'^seeker/', include('clue.seeker.urls')),
    #(r'^m/', include('django_memcached.urls')),
    (r'^login/$', 'lobby.views.login'),
    (r'^logout/', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    (r'^accounts/profile/$', 'lobby.views.profile'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^', include('www.urls')),
    (r'^/$', 'lobby.views.index'),
)
