from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': 'inbox/'}),
    (r'^inbox/$', 'messages.views.inbox'),
    (r'^outbox/$', 'messages.views.outbox'),
    (r'^compose/$', 'messages.views.compose'),
    (r'^compose/(?P<recipient>[\w]+)/$', 'messages.views.compose'),
    (r'^reply/(?P<message_id>[\d]+)/$', 'messages.views.reply'),
    (r'^view/(?P<message_id>[\d]+)/$', 'messages.views.view'),
    (r'^delete/(?P<message_id>[\d]+)/$', 'messages.views.delete'),
    (r'^undelete/(?P<message_id>[\d]+)/$', 'messages.views.undelete'),
    (r'^trash/$', 'messages.views.trash'),
)