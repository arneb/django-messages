from django.urls import path, include


urlpatterns = [
    path(r'messages/', include('django_messages.urls')),
]
