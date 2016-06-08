from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.models import Group

from django_messages.utils import get_user_model
User = get_user_model()

if "notification" in settings.INSTALLED_APPS and getattr(settings, 'DJANGO_MESSAGES_NOTIFY', True):
    from notification import models as notification
else:
    notification = None

from django_messages.models import Message

class MessageAdminForm(forms.ModelForm):
    """
    Custom AdminForm to enable messages to groups and all users.
    """
    group = forms.ChoiceField(label=_('group'), required=False,
        help_text=_('Creates the message optionally for all users or a group of users.'))

    def __init__(self, *args, **kwargs):
        super(MessageAdminForm, self).__init__(*args, **kwargs)
        self.fields['group'].choices = self._get_group_choices()
        self.fields['recipient'].required = True

    def _get_group_choices(self):
        return [('', u'---------'), ('all', _('All users'))] + \
            [(group.pk, group.name) for group in Group.objects.all()]

    class Meta:
        model = Message
        fields = ('sender', 'recipient', 'group', 'parent_msg', 'subject',
                'body', 'sent_at', 'read_at', 'replied_at', 'sender_deleted_at',
                'recipient_deleted_at')

class MessageAdmin(admin.ModelAdmin):
    form = MessageAdminForm
    fieldsets = (
        (None, {
            'fields': (
                'sender',
                ('recipient', 'group'),
            ),
        }),
        (_('Message'), {
            'fields': (
                'parent_msg',
                'subject', 'body',
            ),
            'classes': ('monospace' ),
        }),
        (_('Date/time'), {
            'fields': (
                'sent_at', 'read_at', 'replied_at',
                'sender_deleted_at', 'recipient_deleted_at',
            ),
            'classes': ('collapse', 'wide'),
        }),
    )
    list_display = ('subject', 'sender', 'recipient', 'sent_at', 'read_at')
    list_filter = ('sent_at', 'sender', 'recipient')
    search_fields = ('subject', 'body')
    raw_id_fields = ('sender', 'recipient', 'parent_msg')

    def save_model(self, request, obj, form, change):
        """
        Saves the message for the recipient and looks in the form instance
        for other possible recipients. Prevents duplication by excludin the
        original recipient from the list of optional recipients.

        When changing an existing message and choosing optional recipients,
        the message is effectively resent to those users.
        """
        obj.save()

        if notification:
            # Getting the appropriate notice labels for the sender and recipients.
            if obj.parent_msg is None:
                sender_label = 'messages_sent'
                recipients_label = 'messages_received'
            else:
                sender_label = 'messages_replied'
                recipients_label = 'messages_reply_received'

            # Notification for the sender.
            notification.send([obj.sender], sender_label, {'message': obj,})

        if form.cleaned_data['group'] == 'all':
            # send to all users
            recipients = User.objects.exclude(pk=obj.recipient.pk)
        else:
            # send to a group of users
            recipients = []
            group = form.cleaned_data['group']
            if group:
                group = Group.objects.get(pk=group)
                recipients.extend(
                    list(group.user_set.exclude(pk=obj.recipient.pk)))
        # create messages for all found recipients
        for user in recipients:
            obj.pk = None
            obj.recipient = user
            obj.save()

            if notification:
                # Notification for the recipient.
                notification.send([user], recipients_label, {'message' : obj,})

admin.site.register(Message, MessageAdmin)
