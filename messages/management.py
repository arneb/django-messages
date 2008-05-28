from django.dispatch import dispatcher
from django.db.models import get_models, signals

from django.utils.translation import ugettext_noop as _

try:
    from notification import models as notification
    
    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("messages_received", _("Message Received"), _("you have received a message"), default=2)
        notification.create_notice_type("messages_sent", _("Message Sent"), _("you have sent a message"), default=1)
        notification.create_notice_type("messages_replied", _("Message Replied"), _("you have replied to a message"), default=1)
        notification.create_notice_type("messages_reply_received", _("Reply Received"), _("you have received a reply to a message"), default=2)
        notification.create_notice_type("messages_deleted", _("Message Deleted"), _("you have deleted a message"), default=1)
        notification.create_notice_type("messages_recovered", _("Message Recovered"), _("you have undelete a message"), default=2)
    
    dispatcher.connect(create_notice_types, signal=signals.post_syncdb, sender=notification)
except ImportError:
    print "Skipping creation of NoticeTypes as notification app not found"
