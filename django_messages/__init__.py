from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import importlib

VERSION = (0, 5, 0, 'pre')
__version__ = '.'.join(map(str, VERSION))

BACKEND = getattr(settings, 'MESSAGES_BACKEND',
                  'django_messages.backends.username.UsernameBackend')

def _get_backend(full_backend_path):
    from django_messages.backends import BaseMessageBackend
    module, attr = full_backend_path.rsplit('.', 1)
    try:
        mod = importlib.import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                   (module, e))
    try:
        Backend = getattr(mod, attr)
    except AttributeError, e:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" '
                                   'class.' % (module, attr))

    if not issubclass(Backend, BaseMessageBackend):
        raise ImproperlyConfigured('Backend "%s" is not a subclass of "%s"' %
                                   (Backend, BaseMessageBackend))

    return Backend()

backend = _get_backend(BACKEND)