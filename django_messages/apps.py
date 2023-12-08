from django.apps import AppConfig
try:
    from django.utils.translation import ugettext_lazy as _
except:
    from django.utils.translation import gettext_lazy as _


class DjangoMessagesConfig(AppConfig):
    name = 'django_messages'
    verbose_name = _('Messages')
