from django.conf.urls import patterns, url
from django.views.generic import RedirectView

from django_messages.views import *

# For Django 1.4
try:
    from django.template import add_to_builtins
    from django import VERSION as DJANGO_VERSION
    if DJANGO_VERSION[0] == 1 and DJANGO_VERSION[1] < 5:
        add_to_builtins('django.templatetags.future')
except:
    pass


urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(permanent=True, url='inbox/'), name='messages_redirect'),
    url(r'^inbox/$', inbox, name='messages_inbox'),
    url(r'^outbox/$', outbox, name='messages_outbox'),
    url(r'^compose/$', compose, name='messages_compose'),
    url(r'^compose/(?P<recipient>[\w.@+-]+)/$', compose, name='messages_compose_to'),
    url(r'^reply/(?P<message_id>[\d]+)/$', reply, name='messages_reply'),
    url(r'^view/(?P<message_id>[\d]+)/$', view, name='messages_detail'),
    url(r'^delete/(?P<message_id>[\d]+)/$', delete, name='messages_delete'),
    url(r'^undelete/(?P<message_id>[\d]+)/$', undelete, name='messages_undelete'),
    url(r'^trash/$', trash, name='messages_trash'),
)
