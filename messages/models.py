import datetime
from django.dispatch import dispatcher
from django.db import models
from django.db.models import signals
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from messages.utils import new_message_email

class HideDeletedQuerySet(QuerySet):
    """
    Subclasses the model manager's QuerySet to exclude deleted messages
    Taken from: http://django-pm.googlecode.com/svn/trunk/myproject/pm/models.py
    """
    def _filter_or_exclude(self, mapper, *args, **kwargs):
        if 'sender__pk' in kwargs:
            kwargs['sender_deleted_at__isnull'] = True
        if 'recipient__pk' in kwargs:
            kwargs['recipient_deleted_at__isnull'] = True
        return super(HideDeletedQuerySet, self)._filter_or_exclude(mapper, *args, **kwargs)

class MessageManager(models.Manager):
    """
    Hides deleted Messages from sender or recipient.
    Taken from: http://django-pm.googlecode.com/svn/trunk/myproject/pm/models.py
    TODO: is this stuff really needed?
    """
    def get_accessor_name(self):
        "Returns the messagebox related manager name"
        if not hasattr(self, 'core_filters'):
            raise AttributeError, "Method is only accessible through RelatedManager instances"
        if self.core_filters.has_key('recipient__pk'):
            return 'inbox'
        elif self.core_filters.has_key('sender__pk'):
            if self.model == Message:
                return 'outbox'
            else:
                return 'drafts'
        elif self.core_filters.has_key('previous_message__pk'):
            return 'next_messages'
        raise AttributeError, "Method not available for this RelatedManager"
    
    def get_query_set(self):
        try:
            self.get_accessor_name()
            return HideDeletedQuerySet(self.model)
        except AttributeError:
            return QuerySet(self.model)
            


class Message(models.Model):
    """
    A private message from user to user
    """
    subject = models.CharField(_("Subject"), maxlength=120)
    body = models.TextField(_("Body"))
    sender = models.ForeignKey(User, related_name='sent_messages', verbose_name=_("Sender"))
    recipient = models.ForeignKey(User, related_name='received_messages', null=True, blank=True, verbose_name=_("Recipient"))
    parent_msg = models.ForeignKey('self', related_name='next_messages', null=True, blank=True, verbose_name=_("Parent message"))
    sent_at = models.DateTimeField(_("sent at"), null=True, blank=True)
    read_at = models.DateTimeField(_("read at"), null=True, blank=True)
    replied_at = models.DateTimeField(_("replied at"), null=True, blank=True)
    sender_deleted_at = models.DateTimeField(_("Sender deleted at"), null=True, blank=True)
    recipient_deleted_at = models.DateTimeField(_("Recipient deleted at"), null=True, blank=True)
    
    objects = MessageManager()
    trash = models.Manager() #TODO: write a real trash manager
    
    def new(self):
        """returns whether the recipient has read the message or not"""
        if self.read_at is not None:
            return False
        return True
        
    def replied(self):
        """returns whether the recipient has written a reply to this message"""
        if self.replied_at is not None:
            return True
        return False
    
    def __str__(self):
        return "%s: %s " % (self.sender, self.subject)
    
    def get_absolute_url(self):
        return "/messages/view/%s/" % self.id
    
    def save(self):
        '''
        workaround for django 0.96, if you use trunk delete the 1., 3. and last line
        in this save() method and uncomment the last line in this file to use djangos
        dispatcher framework for this.
        '''
        created = False
        if not self.id:
            created = True
            self.sent_at = datetime.datetime.now()
        super(Message, self).save() 
        new_message_email(self.__class__, self, signals.post_save, created=created)
        
    
    class Admin:
        pass
        
    class Meta:
        ordering = ['-sent_at']
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        
#dispatcher.connect(new_message_email, sender=Message, signal=signals.post_save) #only useable with trunk