from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import importlib
from django_messages.backends import BaseMessageBackend

class ProfilenameBackend(BaseMessageBackend):
    """
    Select user with configured fieldname of AUTH_PROFILE_MODULE.
    The MESSAGES_PROFILENAME_FIELDNAME setting is required.
    """
    def __init__(self):
        if not getattr(settings, 'AUTH_PROFILE_MODULE', False):
            raise ImproperlyConfigured(
                'You need to set AUTH_PROFILE_MODULE in your project settings')
        try:
            app, attr = settings.AUTH_PROFILE_MODULE.split('.')
            module = app + '.models'
        except ValueError:
            raise ImproperlyConfigured(
                'app_label and model_name should be separated by a dot in the '
                'AUTH_PROFILE_MODULE setting')
        
        try:
            mod = importlib.import_module(module)
        except ImportError, e:
            raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                       (module, e))
        try:
            Profile = getattr(mod, attr)
        except AttributeError, e:
            raise ImproperlyConfigured('Module "%s" does not define a "%s" '
                                       'class.' % (module, attr))
       
        self.Profile = Profile

        if not getattr(settings, 'MESSAGES_PROFILENAME_FIELDNAME', False):
            raise ImproperlyConfigured(
                'The MESSAGES_PROFILENAME_FIELDNAME setting is required for Pro'
                'filename backend.')
        self.fieldname = settings.MESSAGES_PROFILENAME_FIELDNAME

        #if not hasattr(self.Profile, self.fieldname): # any idea?
        #    raise ImproperlyConfigured(
        #        'Profile class "%s" does not define a "%s" field' %
        #        (attr, self.fieldname))

    def get_name(self, user):
        return getattr(user.get_profile(), self.fieldname)

    def filter_users(self, names_set):
        filterdict = {self.fieldname + '__in': names_set}
        query = self.Profile.objects.select_related().filter(**filterdict)
        users = [profile.user for profile in query]
        return users
