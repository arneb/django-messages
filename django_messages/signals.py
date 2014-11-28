from django.conf import settings
from django.dispatch import Signal

message_deleted = Signal(providing_args=["message", "user"])
message_sent = Signal(providing_args=["message", "user"])
message_repled = Signal(providing_args=["message", "user"])
mesage_recovered = Signal(providing_args=["message", "user"])
message_marked_as_unread = Signal(providing_args=["message", "user"])
message_purge = Signal(providing_args=["message", "user"])

try:
    #If it's during installation, we should configure the settings otherwise it fails
    settings.configure()
except RuntimeError:
    # Already configured (installation is complete)
    pass

if "notification" in settings.INSTALLED_APPS and getattr(settings, 'DJANGO_MESSAGES_NOTIFY', True):
    from notification import models as notification
    from django_messages.forms import ComposeForm
    from django_messages.views import delete, undelete, unread, purge

    def sent_notification(sender, **kwargs):
        msg = kwargs['message']
        notification.send([msg.sender], "messages_sent", {'message': msg})
        notification.send([msg.recipient], "messages_received", {'message': msg})

    def replied_notification(sender, **kwargs):
        msg = kwargs['message']
        notification.send([msg.sender], "messages_replied", {'message': msg})
        notification.send([msg.recipient], "messages_reply_received", {'message': msg})

    def deleted_notification(sender, **kwargs):
        msg = kwargs['message']
        user = kwargs['user']
        notification.send([user], "messages_deleted", {'message': msg})

    def recovered_notification(sender, **kwargs):
        msg = kwargs['message']
        user = kwargs['user']
        notification.send([user], "messages_recovered", {'message': msg})

    def unread_notification(sender, **kwargs):
        msg = kwargs['message']
        user = kwargs['user']
        notification.send([user], "messages_marked_unread", {'message': msg})

    def purge_notification(sender, **kwargs):
        msg = kwargs['message']
        user = kwargs['user']
        notification.send([user], "messages_purged", {'message': msg})

    message_deleted.connect(deleted_notification, sender=delete)
    message_sent.connect(sent_notification, sender=ComposeForm)
    message_repled.connect(replied_notification, sender=ComposeForm)
    mesage_recovered.connect(recovered_notification, sender=undelete)
    message_marked_as_unread.connect(unread_notification, sender=unread)
    message_purge.connect(purge_notification, sender=purge)

    # fallback for email notification if django-notification could not be found
    from django_messages.utils import new_message_email
    from django.db.models import signals
    from django_messages.models import Message
    signals.post_save.connect(new_message_email, sender=Message)
