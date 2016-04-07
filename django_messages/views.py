# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.conf import settings

from django_messages.models import Message
from django_messages.forms import ComposeForm
from django_messages.utils import format_quote, get_user_model, get_username_field

from profiles.models import ProfileProfileConnection, UserOnBoardNotification

User = get_user_model()

if "notification" in settings.INSTALLED_APPS and getattr(settings, 'DJANGO_MESSAGES_NOTIFY', True):
    from notification import models as notification
else:
    notification = None


@login_required
def inbox(request, template_name='django_messages/inbox.html'):
    """
    Displays a list of received messages for the current user.
    Optional Arguments:
        ``template_name``: name of the template to use.
    """
    page_menu_id = 1
    message_list = Message.objects.inbox_for(request.user)
    return render_to_response(template_name, {
        'message_list': message_list,
        'page_menu_id': page_menu_id,
    }, context_instance=RequestContext(request))


@login_required
def outbox(request, template_name='django_messages/outbox.html'):
    """
    Displays a list of sent messages by the current user.
    Optional arguments:
        ``template_name``: name of the template to use.
    """

    page_menu_id = 2
    message_list = Message.objects.outbox_for(request.user)
    return render_to_response(template_name, {
        'message_list': message_list,
        'page_menu_id': page_menu_id,
    }, context_instance=RequestContext(request))


@login_required
def trash(request, template_name='django_messages/trash.html'):
    """
    Displays a list of deleted messages.
    Optional arguments:
        ``template_name``: name of the template to use
    Hint: A Cron-Job could periodicly clean up old messages, which are deleted
    by sender and recipient.
    """
    page_menu_id = 3
    message_list = Message.objects.trash_for(request.user)
    return render_to_response(template_name, {
        'message_list': message_list,
        'page_menu_id': page_menu_id,
    }, context_instance=RequestContext(request))


@login_required
def compose(request, recipient=None, form_class=ComposeForm,
            template_name='django_messages/compose.html', success_url=None, recipient_filter=None):
    """
    Displays and handles the ``form_class`` form to compose new messages.
    Required Arguments: None
    Optional Arguments:
        ``recipient``: username of a `django.contrib.auth` User, who should
                       receive the message, optionally multiple usernames
                       could be separated by a '+'
        ``form_class``: the form-class to use
        ``template_name``: the template to use
        ``success_url``: where to redirect after successfull submission
    """
    profile_list = []
    profiles_one = ProfileProfileConnection.objects.filter(sec_profile__username=request.user.username,
                                                           rejected_connection=False,
                                                           connected=True)
    for profile in profiles_one:
        profile_user = ProfileProfileConnection.objects.get(pk=str(profile)).first_profile.username
        variable = User.objects.get(username=profile_user)
        profile_list.append(variable)

    profiles_two = ProfileProfileConnection.objects.filter(first_profile__username=request.user.username,
                                                           rejected_connection=False,
                                                           connected=True)
    for profile in profiles_two:
        profile_user = ProfileProfileConnection.objects.get(pk=str(profile)).sec_profile.username
        variable = User.objects.get(username=profile_user)
        profile_list.append(variable)

    if request.method == "POST":
        sender = request.user
        form = form_class(request.POST, recipient_filter=recipient_filter)
        if form.is_valid():
            form.save(sender=request.user)
            messages.info(request, _(u"Message successfully sent."))
            UserOnBoardNotification.objects.create(
                user=request.user, title="Nachricht", notify_typ="info",
                notify_message="Nachricht erfolgreich versendet!")
            if success_url is None:
                success_url = reverse('messages_inbox')
            if 'next' in request.GET:
                success_url = request.GET['next']
            return HttpResponseRedirect(success_url)
    else:
        form = form_class()
        if recipient is not None:
            recipients = [u for u in User.objects.filter(
                **{'%s__in' % get_username_field(): [r.strip() for r in recipient.split('+')]})]
            form.fields['recipient'].initial = recipients
    return render_to_response(template_name, {
        'form': form,
        'profile_list': profile_list,
    }, context_instance=RequestContext(request))


@login_required
def reply(request, message_id, form_class=ComposeForm,
          template_name='django_messages/compose.html', success_url=None,
          recipient_filter=None, quote_helper=format_quote,
          subject_template=_(u"Re: %(subject)s"), ):
    """
    Prepares the ``form_class`` form for writing a reply to a given message
    (specified via ``message_id``). Uses the ``format_quote`` helper from
    ``messages.utils`` to pre-format the quote. To change the quote format
    assign a different ``quote_helper`` kwarg in your url-conf.
    :param recipient_filter:

    """
    parent = get_object_or_404(Message, id=message_id)
    replying = True
    if parent.sender != request.user and parent.recipient != request.user:
        raise Http404

    if request.method == "POST":
        sender = request.user
        form = form_class(request.POST, recipient_filter=recipient_filter)
        if form.is_valid():
            form.save(sender=request.user, parent_msg=parent)
            messages.info(request, _(u"Message successfully sent."))
            UserOnBoardNotification.objects.create(
                user=request.user, title="Nachricht", notify_typ="info",
                notify_message="Nachricht erfolgreich versendet!")
            if success_url is None:
                success_url = reverse('messages_inbox')
            return HttpResponseRedirect(success_url)
    else:
        form = form_class(initial={
            'body': quote_helper(parent.sender, parent.body),
            'subject': subject_template % {'subject': parent.subject},
            'recipient': [parent.sender, ]
        })
    return render_to_response(template_name, {
        'form': form,
        'replying': replying,
    }, context_instance=RequestContext(request))


@login_required
def delete(request, message_id, success_url=None):
    """
    Marks a message as deleted by sender or recipient. The message is not
    really removed from the database, because two users must delete a message
    before it's save to remove it completely.
    A cron-job should prune the database and remove old messages which are
    deleted by both users.
    As a side effect, this makes it easy to implement a trash with undelete.

    You can pass ?next=/foo/bar/ via the url to redirect the user to a different
    page (e.g. `/foo/bar/`) than ``success_url`` after deletion of the message.
    """
    user = request.user
    now = timezone.now()
    message = get_object_or_404(Message, id=message_id)
    deleted = False
    if success_url is None:
        success_url = reverse('messages_inbox')
    if 'next' in request.GET:
        success_url = request.GET['next']
    if message.sender == user:
        message.sender_deleted_at = now
        deleted = True
    if message.recipient == user:
        message.recipient_deleted_at = now
        deleted = True
    if deleted:
        message.save()
        messages.info(request, _(u"Message successfully deleted."))
        UserOnBoardNotification.objects.create(user=user, title="Nachricht", notify_typ="info",
                                               notify_message="Nachricht gel&ouml;scht!")
        if notification:
            notification.send([user], "messages_deleted", {'message': message,})
        return HttpResponseRedirect(success_url)
    raise Http404


@login_required
def undelete(request, message_id, success_url=None):
    """
    Recovers a message from trash. This is achieved by removing the
    ``(sender|recipient)_deleted_at`` from the model.
    """
    user = request.user
    message = get_object_or_404(Message, id=message_id)
    undeleted = False
    if success_url is None:
        success_url = reverse('messages_inbox')
    if 'next' in request.GET:
        success_url = request.GET['next']
    if message.sender == user:
        message.sender_deleted_at = None
        undeleted = True
    if message.recipient == user:
        message.recipient_deleted_at = None
        undeleted = True
    if undeleted:
        message.save()
        messages.info(request, _(u"Message successfully recovered."))
        UserOnBoardNotification.objects.create(user=user, title="Nachricht", notify_typ="info",
                                               notify_message="Nachricht wurde wiederhergestellt!")
        if notification:
            notification.send([user], "messages_recovered", {'message': message,})
        return HttpResponseRedirect(success_url)
    raise Http404


@login_required
def view(request, message_id, form_class=ComposeForm, quote_helper=format_quote,
         subject_template=_(u"Re: %(subject)s"),
         template_name='django_messages/view.html'):
    """
    Shows a single message.``message_id`` argument is required.
    The user is only allowed to see the message, if he is either
    the sender or the recipient. If the user is not allowed a 404
    is raised.
    If the user is the recipient and the message is unread
    ``read_at`` is set to the current datetime.
    If the user is the recipient a reply form will be added to the
    tenplate context, otherwise 'reply_form' will be None.
    :param subject_template:
    """
    message_list = Message.objects.inbox_for(request.user)
    user = request.user
    now = timezone.now()
    mid = int(message_id)
    message = get_object_or_404(Message, id=message_id)
    if (message.sender != user) and (message.recipient != user):
        raise Http404
    if message.read_at is None and message.recipient == user:
        message.read_at = now
        UserOnBoardNotification.objects.create(
            user=message.sender, title="Nachricht", notify_typ="info",
            notify_message=" " + str(message.recipient) + " hat deine Nachricht gelesen gelesen!")
        message.save()

    context = {'message': message, 'mid': mid, 'message_list': message_list, 'reply_form': None}
    if message.recipient == user:
        form = form_class(initial={
            'body': quote_helper(message.sender, message.body),
            'subject': subject_template % {'subject': message.subject},
            'recipient': [message.sender, ]
        })
        context['reply_form'] = form
    return render_to_response(template_name, context,
                              context_instance=RequestContext(request))
