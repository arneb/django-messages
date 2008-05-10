import datetime
import django.newforms as forms
from django.utils.translation import gettext as _
from django.contrib.auth.models import User

from messages.models import Message

class ComposeForm(forms.Form):
    """
    A simple default form for private messages.
    """
    recipient = forms.CharField(label=_(u"Recipient"))
    subject = forms.CharField(label=_(u"Subject"))
    body = forms.CharField(label=_(u"Body"), widget=forms.Textarea(attrs={'rows': '12', 'cols':'55'}))
    
    def clean_recipient(self):
        try:
            User.objects.get(username__exact=self.clean_data['recipient'])
        except User.DoesNotExist:
            raise forms.ValidationError(_("There is no user with this username."))
        return self.clean_data['recipient']
        
    def save(self, sender, parent_msg=None):
        recipient = User.objects.get(username=self.clean_data['recipient'])
        subject = self.clean_data['subject']
        body = self.clean_data['body']
        msg = Message(
            sender = sender,
            recipient = recipient,
            subject = subject,
            body = body,
        )
        if parent_msg is not None:
            msg.parent_msg = parent_msg
            parent_msg.replied_at = datetime.datetime.now()
            parent_msg.save()
        msg.save()
        return msg
        