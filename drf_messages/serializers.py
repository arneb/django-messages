from rest_framework import serializers
from django.utils import timezone

from .models import Message


class ComposeSerializer(serializers.ModelSerializer):
    """
    A simple default serializer for private messages.
    """
    subject = serializers.CharField(required=True)
    body = serializers.CharField(required=True)
    recipient = serializers.ListField(required=True)

    class Meta:
        model = Message
        fields = ('id', 'subject', 'body', 'sender', 'recipient', 'sent_at', 'read_at', 'replied_at',
                  'sender_deleted_at', 'recipient_deleted_at', 'parent_msg')

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
        return message_list


class ReadMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ('id', 'subject', 'body', 'sender', 'recipient', 'sent_at', 'read_at', 'replied_at',
                  'sender_deleted_at', 'recipient_deleted_at', 'parent_msg')
