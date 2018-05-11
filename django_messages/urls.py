from django.urls import path, re_path
from django.views.generic import RedirectView

from django_messages.views import *

urlpatterns = [
    path(r'', RedirectView.as_view(permanent=True, url='inbox/'), name='messages_redirect'),
    path(r'inbox/', inbox, name='messages_inbox'),
    path(r'outbox/', outbox, name='messages_outbox'),
    path(r'compose/', compose, name='messages_compose'),
    re_path(r'compose/(?P<recipient>[\w.@+-]+)/', compose, name='messages_compose_to'),
    path(r'reply/<int:message_id>/', reply, name='messages_reply'),
    path(r'view/<int:message_id>/', view, name='messages_detail'),
    path(r'delete/<int:message_id>/', delete, name='messages_delete'),
    path(r'undelete/<int:message_id>/', undelete, name='messages_undelete'),
    path(r'trash/', trash, name='messages_trash'),
]
