
from django_messages.backends import BaseMessageBackend
from django.contrib.auth.models import User

class UsernameBackend(BaseMessageBackend):
    """
    Select user with username of `django.contrib.auth` User.
    """
    def get_name(self, user):
        return user.username

    def filter_users(self, names_set):
        return list(User.objects.filter(username__in=names_set))
