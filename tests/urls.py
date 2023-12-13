from django.urls import re_path, include


urlpatterns = [
    re_path(r'^messages/', include('django_messages.urls')),
]
