from memopol.base.settings import *

PROJECT_PATH = os.path.abspath(os.path.split(__file__)[0])

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '%s/memopol2.sqlite' % PROJECT_PATH,
    },
}


try:
    from settings_local import *
except ImportError:
    pass
