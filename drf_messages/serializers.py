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

    def create(self, validated_data):
        recipients = validated_data['recipient']
        sender = validated_data['sender']
        subject = validated_data['subject']
        body = validated_data['body']
        parent_msg = validated_data.get('parent_msg')
        now = timezone.now()
        serialized_message_instances = []
        for r in recipients:
            message = Message(
                sender_id=sender.id,
                recipient_id=r,
                subject=subject,
                body=body,
                sent_at=now
            )
            if parent_msg is not None:
                message.parent_msg = parent_msg
                parent_msg.replied_at = now
                parent_msg.save()
            message.save()
            serialized_message = ReadMessageSerializer(message).data
            serialized_message_instances.append(serialized_message)
        return serialized_message_instances


class ReadMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ('id', 'subject', 'body', 'sender', 'recipient', 'sent_at', 'read_at', 'replied_at',
                  'sender_deleted_at', 'recipient_deleted_at', 'parent_msg')
