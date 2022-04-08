from django.views.generic import RedirectView
from django.urls import include, path
from django_messages.views import *

urlpatterns = [
    path('', RedirectView.as_view(permanent=True, url='inbox/'), name='messages_redirect'),
    path('inbox/', inbox, name='messages_inbox'),
    path('outbox/', outbox, name='messages_outbox'),
    path('compose/', compose, name='messages_compose'),
    path('compose/(?P<recipient>[\w.@+-]+)/', compose, name='messages_compose_to'),
    path('reply/(?P<message_id>[\d]+)/', reply, name='messages_reply'),
    path('view/(?P<message_id>[\d]+)/', view, name='messages_detail'),
    path('delete/(?P<message_id>[\d]+)/', delete, name='messages_delete'),
    path('undelete/(?P<message_id>[\d]+)/', undelete, name='messages_undelete'),
    path('trash/$', trash, name='messages_trash'),
]
