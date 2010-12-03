import os, sys
sys.path.append('/home/capstone/Seeker/')
sys.path.append('/home/capstone/Seeker/clue')
os.environ['DJANGO_SETTINGS_MODULE'] = 'clue.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
