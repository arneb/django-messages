from django.db.models import signals
from django.conf import settings
from django.utils.translation import ugettext_noop as _

if "pinax.notifications" in settings.INSTALLED_APPS and getattr(settings, 'DJANGO_MESSAGES_NOTIFY', True):
    from pinax.notifications import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("messages_received", _("Message Received"), _("you have received a message"), default=2)
        notification.create_notice_type("messages_sent", _("Message Sent"), _("you have sent a message"), default=1)
        notification.create_notice_type("messages_replied", _("Message Replied"), _("you have replied to a message"), default=1)
        notification.create_notice_type("messages_reply_received", _("Reply Received"), _("you have received a reply to a message"), default=2)
        notification.create_notice_type("messages_deleted", _("Message Deleted"), _("you have deleted a message"), default=1)
        notification.create_notice_type("messages_recovered", _("Message Recovered"), _("you have undeleted a message"), default=1)

    signals.post_migrate.connect(create_notice_types, sender=notification)
else:
    print("Skipping creation of NoticeTypes as notification app not found")
