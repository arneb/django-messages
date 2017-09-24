from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class DjangoMessagesConfig(AppConfig):
    name = 'django_messages'
    verbose_name = _('Messages')
