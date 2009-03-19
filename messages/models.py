import datetime
from django.db import models
from django.conf import settings
from django.db.models import signals
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class MessageManager(models.Manager):

    def inbox_for(self, user):
        """
        Returns all messages that were received by the given user and are not
        marked as deleted.
        """
        return self.filter(
            recipients=user,
            messagerecipient__deleted_at__isnull=True,
            #recipient_deleted_at__isnull=True,
        )

    def outbox_for(self, user):
        """
        Returns all messages that were sent by the given user and are not
        marked as deleted.
        """
        return self.filter(
            sender=user,
            sender_deleted_at__isnull=True,
            sent_at__isnull=False,
        )

    def trash_for(self, user):
        """
        Returns all messages that were either received or sent by the given
        user and are marked as deleted.
        """
        return self.filter(
            recipients=user,
            messagerecipient__deleted_at__isnull=False,
        ) | self.filter(
            sender=user,
            sender_deleted_at__isnull=False,
        )
        
    def drafts_for(self, user):
        """
        Returns all messages where ``sent_at`` is Null and where the given
        user is the sender and which are not yet deleted by the sender.
        """
        return self.filter(
            sender=user,
            sent_at__isnull=True,
            sender_deleted_at__isnull=True,
        )


class Message(models.Model):
    """
    A private message from user to user
    """
    subject = models.CharField(_("Subject"), max_length=120)
    body = models.TextField(_("Body"))
    sender = models.ForeignKey(User, related_name='sent_messages', verbose_name=_("Sender"))
    recipients = models.ManyToManyField(User, through='MessageRecipient', related_name="received_messages", verbose_name=_("Recipients"))
    parent_msg = models.ForeignKey('self', related_name='next_messages', null=True, blank=True, verbose_name=_("Parent message"))
    sent_at = models.DateTimeField(_("sent at"), null=True, blank=True)
    sender_deleted_at = models.DateTimeField(_("Sender deleted at"), null=True, blank=True)
    
    objects = MessageManager()
    
    def __unicode__(self):
        return self.subject
    
    def get_absolute_url(self):
        return ('messages_detail', [self.id])
    get_absolute_url = models.permalink(get_absolute_url)
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")


class MessageRecipient(models.Model):
    """
    Intermediate model to allow per recipient marking as
    deleted, read etc. of a message.
    
    """
    user = models.ForeignKey(User, verbose_name=_("Recipient"))
    message = models.ForeignKey(Message, verbose_name=_("Message"))
    read_at = models.DateTimeField(_("read at"), null=True, blank=True)
    deleted_at = models.DateTimeField(_("Recipient deleted at"), null=True, blank=True)
    replied_at = models.DateTimeField(_("replied at"), null=True, blank=True)
    
    def __unicode__(self):
        return "%s (%s)" % (self.message, self.user)

    def new(self):
        """returns whether the recipient has read the message or not"""
        return self.read_at is None
        
    def replied(self):
        """returns whether the recipient has written a reply to this message"""
        return self.replied_at is not None
        
    class Meta:
        verbose_name = _("Recipient")
        verbose_name_plural = _("Recipients")
        
            
def inbox_count_for(user):
    """
    returns the number of unread messages for the given user but does not
    mark them seen
    """
    return Message.objects.filter(recipients=user, 
                                  messagerecipient__read_at__isnull=True, 
                                  messagerecipient__deleted_at__isnull=True).count()

# fallback for email notification if django-notification could not be found
if 'notification' not in settings.INSTALLED_APPS:
    from messages.utils import new_message_email
    signals.post_save.connect(new_message_email, sender=Message)
