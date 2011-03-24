import os, sys
sys.path.append('/Users/seeker/Sites/Seeker/')
sys.path.append('/Users/seeker/Sites/Seeker/clue')
os.environ['DJANGO_SETTINGS_MODULE'] = 'clue.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
