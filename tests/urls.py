from django.conf.urls import include, patterns


urlpatterns = patterns(
    '',
    (r'^messages/', include('django_messages.urls')),
)
