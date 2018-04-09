from django.urls import path
from django.views.generic import RedirectView

from django_messages.views import *

urlpatterns = [
    path(r'$', RedirectView.as_view(permanent=True, url='inbox/'), name='messages_redirect'),
    path(r'inbox/$', inbox, name='messages_inbox'),
    path(r'outbox/$', outbox, name='messages_outbox'),
    path(r'compose/$', compose, name='messages_compose'),
    path(r'compose/(?P<recipient>[\w.@+-]+)/$', compose, name='messages_compose_to'),
    path(r'reply/(?P<message_id>[\d]+)/$', reply, name='messages_reply'),
    path(r'view/(?P<message_id>[\d]+)/$', view, name='messages_detail'),
    path(r'delete/(?P<message_id>[\d]+)/$', delete, name='messages_delete'),
    path(r'undelete/(?P<message_id>[\d]+)/$', undelete, name='messages_undelete'),
    path(r'trash/$', trash, name='messages_trash'),
]
