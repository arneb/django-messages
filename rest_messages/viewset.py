from django.contrib import messages
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, decorators, status, generics
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _

from .models import Message
from .serializers import ComposeSerializer, ReadMessageSerializer
from .utils import get_user_model, get_username_field


User = get_user_model()
if "pinax.notifications" in settings.INSTALLED_APPS and getattr(settings, 'DJANGO_MESSAGES_NOTIFY', True):
    from pinax.notifications import models as notification
else:
    notification = None


class MessageViewSet(viewsets.GenericViewSet):
    queryset = Message.objects.all()
    serializer_class = ComposeSerializer

    @decorators.action(methods=['get'], detail=False)
    def inbox(self, request):
        """
        Displays a list of received messages for the current user.
        """
        message_list = Message.objects.inbox_for(request.user)
        serialized_messages = self.serialized_messages(message_list)

        return Response({
            'message_list': serialized_messages,
        }, status=status.HTTP_200_OK)

    @decorators.action(methods=['get'], detail=False)
    def outbox(self, request):
        """
        Displays a list of sent messages by the current user.
        """
        message_list = Message.objects.outbox_for(request.user)
        serialized_messages = self.serialized_messages(message_list)

        return Response({
            'message_list': serialized_messages,
        }, status=status.HTTP_200_OK)

    @decorators.action(methods=['get'], detail=False)
    def trash(self, request):
        """
        Displays a list of deleted messages.
        Hint: A Cron-Job could periodically clean up old messages, which are deleted
        by sender and recipient.
        """
        message_list = Message.objects.trash_for(request.user)
        serialized_messages = self.serialized_messages(message_list)
        serialized_messages = self.serialized_messages(serialized_messages)
        return Response({
            'message_list': serialized_messages,
        })

    @decorators.action(methods=['post', 'get'], detail=False)
    def compose(self, request):
        """
        Displays and handles the ``form_class`` form to compose new messages.
        Required Arguments: None
        Optional Arguments:
            ``recipient``: username of a django auth model, who should
                           receive the message, optionally multiple usernames
                           could be separated by a '+'
        """
        recipient = request.data.get('recipient', None)
        recipient_filter = request.data.get('recipient_filter', None)
        if request.method == "POST":
            serializer = ComposeSerializer(data=request.data, recipient_filter=recipient_filter)
            if serializer.is_valid(raise_exception=True):
                serializer.save(sender=request.user)
                messages.info(request, _("Message successfully sent."))
                return Response({
                    'message': serializer.data
                }, status=status.HTTP_201_CREATED)
        else:
            serializer = ComposeSerializer()
            if recipient is not None:
                recipients = [u for u in User.objects.filter(**{'%s__in' % get_username_field(): [r.strip() for r in recipient.split('+')]})]
                serializer.fields['recipient'].initial = recipients
        return Response({
            'serializer': serializer,
        })

    @decorators.action(methods=['post'], detail=True)
    def reply(self, request, pk):
        """
        Prepares the ``serializer_class`` for writing a reply to a given message
        (specified via ``message_id``).
        """
        subject_template: str = _("Re: %(subject)s")

        parent = get_object_or_404(Message, pk=pk)
        if parent.sender != request.user and parent.recipient != request.user:
            raise Http404

        if request.method == "POST":
            serializer = ComposeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(sender=request.user, parent_msg=parent)
                return Response({
                    _("Message successfully sent.")
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = ComposeSerializer(initial={
                'sender': parent.sender,
                'body': parent.body,
                'subject': subject_template % {'subject': parent.subject},
                'recipient': [parent.sender, ]
            })
        return Response({
            'serializer': serializer,
        })

    @decorators.action(methods=['put'], detail=True)
    def delete(self, request, pk):
        """
        Marks a message as deleted by sender or recipient. The message is not
        really removed from the database, because two users must delete a message
        before it's save to remove it completely.
        A cron-job should prune the database and remove old messages which are
        deleted by both users.
        As a side effect, this makes it easy to implement a trash with undelete.
        """
        user = request.user
        now = timezone.now()
        message = get_object_or_404(Message, pk=pk)

        deleted = False
        if message.sender == user:
            message.sender_deleted_at = now
            deleted = True
        if message.recipient == user:
            message.recipient_deleted_at = now
            deleted = True
        if deleted:
            message.save()
            # if notification:
            #     notification.send([user], "messages_deleted", {'message': message, })
            return Response({
                _("Message successfully deleted.")
            }, status=status.HTTP_204_NO_CONTENT)
        raise Http404

    @decorators.action(methods=['put'], detail=True)
    def undelete(self, request, pk):
        """
        Recovers a message from trash. This is achieved by removing the
        ``(sender|recipient)_deleted_at`` from the model.
        """
        user = request.user
        message = get_object_or_404(Message, pk=pk)
        undeleted = False

        if message.sender == user:
            message.sender_deleted_at = None
            undeleted = True
        if message.recipient == user:
            message.recipient_deleted_at = None
            undeleted = True
        if undeleted:
            message.save()
            if notification:
                notification.send([user], "messages_recovered", {'message': message, })
            return Response({_(u"Message successfully recovered.")}, status=status.HTTP_200_OK)
        raise Http404

    @decorators.action(methods=['get'], detail=True)
    def view(self, request, pk):
        """
        Shows a single message.``message_id`` argument is required.
        The user is only allowed to see the message, if he is either
        the sender or the recipient. If the user is not allowed a 404
        is raised.
        If the user is the recipient and the message is unread
        ``read_at`` is set to the current datetime.
        """
        user = request.user
        now = timezone.now()
        message = get_object_or_404(Message, pk=pk)

        if (message.sender != user) and (message.recipient != user):
            raise Http404
        if message.read_at is None and message.recipient == user:
            message.read_at = now
            message.save()

        return Response({
            'message': ReadMessageSerializer(message).data
        })

    def serialized_messages(self, messages_list):
        serialized_messages_list = []
        for msg in messages_list:
            ser_message = ReadMessageSerializer(msg)
            serialized_messages_list.append(ser_message.data)
        return serialized_messages_list
