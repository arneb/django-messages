from django.apps import AppConfig
from django.utils.translation import gettext as _


class DjangoMessagesConfig(AppConfig):
    name = 'django_messages'
    default_auto_field = 'django.db.models.AutoField'
    verbose_name = _('Messages')
