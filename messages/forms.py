import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_noop

from django.contrib.auth.models import User

try:
    from notification import models as notification
except ImportError:
    notification = None

from messages.models import Message
from messages.fields import CommaSeparatedUserField

class ComposeForm(forms.Form):
    """
    A simple default form for private messages.
    """
    recipient = CommaSeparatedUserField(label=_(u"Recipient"))
    subject = forms.CharField(label=_(u"Subject"))
    body = forms.CharField(label=_(u"Body"),
        widget=forms.Textarea(attrs={'rows': '12', 'cols':'55'}))
    
    #def clean_recipient(self):
    #    try:
    #        User.objects.get(username__exact=self.cleaned_data['recipient'])
    #    except User.DoesNotExist:
    #        raise forms.ValidationError(_("There is no user with this username."))
    #    return self.cleaned_data['recipient']
        
    def save(self, sender, parent_msg=None):
        recipients = self.cleaned_data['recipient']
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']
        message_list = []
        for r in recipients:
            msg = Message(
                sender = sender,
                recipient = r,
                subject = subject,
                body = body,
            )
            if parent_msg is not None:
                msg.parent_msg = parent_msg
                parent_msg.replied_at = datetime.datetime.now()
                parent_msg.save()
            msg.save()
            message_list.append(msg)
            if notification:
                if parent_msg is not None:
                    notification.send([sender], "messages_replied", {'message': msg,})
                    notification.send([recipient], "messages_reply_received", {'message': msg,})
                else:
                    notification.send([sender], "messages_sent", {'message': msg,})
                    notification.send([recipient], "messages_received", {'message': msg,})
        return message_list
