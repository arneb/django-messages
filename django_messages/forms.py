from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django_messages.models import Message
from django_messages.fields import CommaSeparatedUserField
from django_messages import signals


class ComposeForm(forms.Form):

    """
    A simple default form for private messages.
    """
    recipient = CommaSeparatedUserField(label=_(u"Recipient"))
    subject = forms.CharField(label=_(u"Subject"), max_length=120)
    body = forms.CharField(label=_(u"Body"),
                           widget=forms.Textarea(attrs={'rows': '12', 'cols': '55'}))

    def __init__(self, *args, **kwargs):
        recipient_filter = kwargs.pop('recipient_filter', None)
        super(ComposeForm, self).__init__(*args, **kwargs)
        if recipient_filter is not None:
            self.fields['recipient']._recipient_filter = recipient_filter

    def save(self, sender, parent_msg=None):
        recipients = self.cleaned_data['recipient']
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']
        message_list = []
        for r in recipients:
            msg = Message(
                sender=sender,
                recipient=r,
                subject=subject,
                body=body,
            )
            if parent_msg is not None:
                msg.parent_msg = parent_msg
                parent_msg.replied_at = timezone.now()
                parent_msg.save()
                signals.message_repled.send(sender=ComposeForm, message=msg, user=sender)
            msg.save()

            if parent_msg is None:
                signals.message_sent.send(sender=ComposeForm, message=msg, user=sender)

            message_list.append(msg)
        return message_list
