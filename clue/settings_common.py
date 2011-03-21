import os

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
LOGGING_PATH = os.path.join(PROJECT_PATH, 'log/')
# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'assets/')
ADMINS = (
    ('Lincoln', 'bryant.lincoln@gmail.com'),
)

MANAGERS = ADMINS
#Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '@6vv2ju2fkp-(@$07-8gko5hg1a6zyqgdm1oi5*w!&0__-fl45'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'facebook.djangofb.FacebookMiddleware',
    'facebookconnect.middleware.FacebookConnectMiddleware',
    'lb.util.AJAXSimpleExceptionResponse',
    'lb.middleware.SlowQueryLogMiddleware'
    
)

ROOT_URLCONF = 'clue.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'templates')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django_memcached',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'userprofile',
    'lobby',
    'seeker',
    'www',
    'lb',
    'facebookconnect'
)

AUTHENTICATION_BACKENDS = (
    'facebookconnect.models.FacebookBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'

AVATAR_WEBSEARCH = False
FACEBOOK_API_KEY = 'baa973193a1795271a02548dbc26d511'
FACEBOOK_SECRET_KEY = '099e81627dc77c30ab2888e4565524b7'
FACEBOOK_INTERNAL = True
LOGGING_PATH = 'log/'

SMTP_USERNAME = 'noreply@seekr.us'
SMTP_PASSWORD = 'secret'

AUTH_PROFILE_MODULE = 'userprofile.UserProfile'
I18N_URLS = False
DEFAULT_AVATAR_WIDTH = 96
DEFAULT_AVATAR = os.path.join(MEDIA_ROOT, 'img', 'chars', 'char1.png')
AVATAR_WEBSEARCH = False
GOOGLE_MAPS_API_KEY = "ABQIAAAAH9I7_xiZKQB_dhdYw-OhbxT7HHcoM5zc4zKY9lkdWM1EdbPSLhSSWxHIixE4Q3-zKe0UGwqItjiCMg"
REQUIRE_EMAIL_CONFIRMATION = True
USERPROFILE_CSS_CLASSES = 'blueprint'
