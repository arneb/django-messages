from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DjangoMessagesConfig(AppConfig):
    name = 'rest_messages'
    verbose_name = _('Rest Messages')
