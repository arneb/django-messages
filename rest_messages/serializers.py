from rest_framework import serializers
from django.conf import settings
from django.utils import timezone

from .models import Message
from .utils import get_user_model, get_username_field
from .fields import CommaSeparatedUserField

from django.utils.translation import ugettext_lazy as _
if "pinax.notifications" in settings.INSTALLED_APPS and getattr(settings, 'DJANGO_MESSAGES_NOTIFY', True):
    from pinax.notifications import models as notification
else:
    notification = None

User = get_user_model()


class ComposeSerializer(serializers.ModelSerializer):
    """
    A simple default serializer for private messages.
    """
    subject = serializers.CharField()
    body = serializers.CharField()
    recipient = serializers.ListField()

    # def __init__(self, *args, **kwargs):
    #     recipient_filter = kwargs.pop('recipient_filter', None)
    #     super(ComposeSerializer, self).__init__(*args, **kwargs)
    #     if recipient_filter is not None:
    #         self.fields['recipient']._recipient_filter = recipient_filter

    class Meta:
        model = Message
        fields = '__all__'

    # def validate_recipient(self, value):
    #     if not value:
    #         return []
    #     if not isinstance(value, (list, tuple)):
    #         return serializers.ValidationError({'recipients': 'Invalid recipients.'})
    #
    #     users = User.objects.filter(id__in=value)
    #     return users

    def save(self, sender, parent_msg=None):
        recipients = self.validated_data['recipient']
        subject = self.validated_data['subject']
        body = self.validated_data['body']
        message_list = []
        for r in recipients:
            msg = Message(
                sender=sender,
                recipient_id=r,
                subject=subject,
                body=body,
            )
            if parent_msg is not None:
                msg.parent_msg = parent_msg
                parent_msg.replied_at = timezone.now()
                parent_msg.save()
            msg.save()
            message_list.append(msg)
            # if notification:
            #     if parent_msg is not None:
            #         notification.send([sender], "messages_replied", {'message': msg,})
            #         notification.send([r], "messages_reply_received", {'message': msg,})
            #     else:
            #         notification.send([sender], "messages_sent", {'message': msg,})
            #         notification.send([r], "messages_received", {'message': msg,})
        return message_list


class ReadMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'
