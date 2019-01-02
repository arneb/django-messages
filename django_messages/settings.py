from django.conf import settings

BASE_TEMPLATE = getattr(settings, 'MESSAGES_BASE_TEMPLATE', 'django_messages/base.html')
