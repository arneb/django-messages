from django.conf import settings
from appconf import AppConf

class MessagesAppConf(AppConf):
    DELETED_MAX_AGE = 30

    class Meta:
        prefix = 'MESSAGES'
