from django.urls import path, re_path
from django.views.generic import RedirectView

from django_messages.views import *

urlpatterns = [
    path('', RedirectView.as_view(permanent=True, url='inbox/'), name='messages_redirect'),
    path('inbox/', inbox, name='messages_inbox'),
    path('outbox/', outbox, name='messages_outbox'),
    path('compose/', compose, name='messages_compose'),
    re_path(r'^compose/(?P<recipient>[\w\s.@+-]+)/$', compose, name='messages_compose_to'),
    path('reply/<int:message_id>/', reply, name='messages_reply'),
    path('view/<int:message_id>/', view, name='messages_detail'),
    path('delete/<int:message_id>/', delete, name='messages_delete'),
    path('undelete/<int:message_id>/', undelete, name='messages_undelete'),
    path('trash/', trash, name='messages_trash'),
]
