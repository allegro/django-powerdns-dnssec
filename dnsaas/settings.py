# Django settings for standalone django_powerdns.
import os
import sys


DEBUG = True
TEMPLATE_DEBUG = DEBUG

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dnsaas',
        'USER': os.environ.get('DNSAAS_DB_USER', 'dnsaas'),
        'PASSWORD': os.environ.get('DNSAAS_DB_PASSWORD', 'dnsaas'),
        'HOST': os.environ.get('DNSAAS_DB_HOST', 'localhost'),
        'PORT': '3306',
        'TEST': {
            'NAME': 'test_dnsaas',
        },
    }
}

if TESTING:
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    SKIP_MIGRATIONS = os.environ.get('SKIP_MIGRATIONS', None)
    if SKIP_MIGRATIONS:
        print('skipping migrations')

        class DisableMigrations(object):

            def __contains__(self, item):
                return True

            def __getitem__(self, item):
                return "notmigrations"

        MIGRATION_MODULES = DisableMigrations()

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '5w%2cqg#kb1w&amp;mm-ss67(eo&amp;3+d9%pbu+5pesa*l&amp;pk7g-m48d'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'threadlocals.middleware.ThreadLocalMiddleware',
    'dnsaas.api.middleware.VersionSwitch',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'dnsaas.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'dnsaas.wsgi.application'

TEMPLATE_DIRS = ()

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'django_nose',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',
    'powerdns',
    'dnsaas',
    'ui',
    'autocomplete_light',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'rules',
)

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '-c.noserc',
    '--verbosity=2',
    '--exclude=integration-tests',  # To be run in docker
]

DNSAAS_DEFAULT_REVERSE_DOMAIN_TEMPLATE = 'reverse'

REST_FRAMEWORK = {
    'VIEW_DESCRIPTION_FUNCTION':
        'rest_framework_swagger.views.get_restructuredtext',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.DjangoObjectPermissions',
    ),
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_VERSIONING_CLASS':
        'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_VERSION': 'v1',
    'PAGE_SIZE': 50,
}

if TESTING:
    REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.


if os.environ.get('DJANGO_SETTINGS_PROFILE') == 'tests':
    DATABASES['default']['NAME'] = ':memory:'

ENABLE_OWNER_NOTIFICATIONS = TESTING  # E-mail backend required

FROM_EMAIL = 'dnsaas@example.com'

OWNER_NOTIFICATIONS = {
    'Domain': (
        'Domain {object} created for you!',
        """
        User {creator-name} ({creator-email}) has created a domain
        {object} and set its owner to you!
        """,
    ),
    'Record': (
        'Record {object} created for you!',
        """
        User {creator-name} ({creator-email}) has created a record
        {object} and set its owner to you!
        """,
    )
}

SITE_TITLE = 'Django powerdns'


if not TESTING:
    try:
        from settings_local import *  # noqa
    except ImportError:
        pass
