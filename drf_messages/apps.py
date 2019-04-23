from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DrfMessagesConfig(AppConfig):
    name = 'drf_messages'
    verbose_name = _('DRF Messages')
