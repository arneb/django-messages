import datetime
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.dispatch import dispatcher
from django.contrib.auth.decorators import login_required
from messages.models import Message
from messages.forms import ComposeForm
from messages.utils import format_quote


@login_required
def inbox(request, template_name='messages/inbox.html'):
    """
    Displays a list of received messages for the current user.
    Optional Arguments:
        ``template_name``: name of the template to use.
    """
    user = request.user
    message_list = user.received_messages.all()
    return render_to_response(template_name, {'message_list': message_list}, context_instance=RequestContext(request))

@login_required    
def outbox(request, template_name='messages/outbox.html'):
    """
    Displays a list of sent messages by the current user.
    Optional arguments:
        ``template_name``: name of the template to use.
    """
    user = request.user
    message_list = user.sent_messages.all()
    return render_to_response(template_name, {'message_list': message_list}, context_instance=RequestContext(request))

@login_required
def trash(request, template_name='messages/trash.html'):
    """
    Displays a list of deleted messages. 
    Optional arguments:
        ``template_name``: name of the template to use
    Hint: A Cron-Job coul periodicly clean up old messages, which are deleted by sender
    and recipient.
    """
    user = request.user
    message_list = Message.trash.filter(recipient=user, recipient_deleted_at__isnull=False)
    return render_to_response(template_name, {'message_list': message_list}, context_instance=RequestContext(request))

@login_required    
def compose(request, recipient=None, form_class=ComposeForm, template_name='messages/compose.html', success_url='/messages/inbox/'):
    """
    Displays and handles the ``form_class`` form to compose new messages.
    Required Arguments: None
    Optional Arguments:
        ``recipient``: username of a `django.contrib.auth` User, who should receive the message
        ``form_class``: the form-class to use
        ``template_name``: the template to use
        ``success_url``: where to redirect after successfull submission
    """
    if request.method == "POST":
        sender = request.user
        form = form_class(request.POST)
        if form.is_valid():
            recipient = User.objects.get(username=form.clean_data['recipient'])
            subject = form.clean_data['subject']
            body = form.clean_data['body']
            msg = Message(
                sender = sender,
                recipient = recipient,
                subject = subject,
                body = body,
            )
            msg.save()
            request.user.message_set.create(message="Message successfully sent.")
            #FIXME: for django trunk use named url patterns
            return HttpResponseRedirect(success_url)
    else:
        if recipient is not None:
            form = form_class({
                'body': " ",
                'subject': " ",
                'recipient': get_object_or_404(User, username=recipient)
            })
        else:
            form = form_class()
    return render_to_response(template_name, {'form': form}, context_instance=RequestContext(request))

@login_required
def reply(request, message_id, form_class=ComposeForm, template_name='messages/compose.html', success_url='/messages/inbox/'):
    """
    Prepares the ``form_class`` form for writing a reply to a given message
    (specified via ``message_id``). Uses the ``format_quote`` helper from
    ``messages.utils`` to pre-format the quote.
    """
    parent = get_object_or_404(Message, id=message_id)
    now = datetime.datetime.now()
    if request.method == "POST":
        sender = request.user
        form = form_class(request.POST)
        if form.is_valid():
            recipient = User.objects.get(username=form.clean_data['recipient'])
            subject = form.clean_data['subject']
            body = form.clean_data['body']
            msg = Message(
                sender = sender,
                recipient = recipient,
                subject = subject,
                body = body,
                parent_msg = parent
            )
            msg.save()
            parent.replied_at = now
            parent.save()
            request.user.message_set.create(message="Message successfully sent.")
            #FIXME: for django trunk use named url patterns
            return HttpResponseRedirect(success_url)
    else:
        form = form_class({
            'body': "%s wrote:\n%s" % (parent.sender, format_quote(parent.body)), 
            'subject': 'Re: %s' % parent.subject,
            'recipient': parent.sender
            })
    return render_to_response(template_name, {'form': form}, context_instance=RequestContext(request))

@login_required        
def delete(request, message_id, success_url='/messages/inbox/'):
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
    now = datetime.datetime.now()
    message = get_object_or_404(Message, id=message_id)
    deleted = False
    if request.GET.has_key('next'):
        success_url = request.GET['next']
    if message.sender == user:
        message.sender_deleted_at = now
        deleted = True
    if message.recipient == user:
        message.recipient_deleted_at = now
        deleted = True
    if deleted:
        message.save()
        user.message_set.create(message="Message successfully deleted.")
        return HttpResponseRedirect(success_url)
    raise Http404

@login_required
def undelete(request, message_id, success_url='/messages/inbox/'):
    """
    Recovers a message from trash. This is achieved by removing the
    ``(sender|recipient)_deleted_at`` from the model.
    """
    user = request.user
    message = get_object_or_404(Message, id=message_id)
    undeleted = False
    if request.GET.has_key('next'):
        success_url = request.GET['next']
    if message.sender == user:
        message.sender_deleted_at = None
        undeleted = True
    if message.recipient == user:
        message.recipient_deleted_at = None
        undeleted = True
    if undeleted:
        message.save()
        user.message_set.create(message="Message successfully recovered.")
        return HttpResponseRedirect(success_url)
    raise Http404
    
        
@login_required                
def view(request, message_id, template_name='messages/view.html'):
    """
    Shows a single message.``message_id`` argument is required.
    The user is only allowed to see the message, if he is either 
    the sender or the recipient. If the user is not allowed a 404
    is raised. 
    If the user is the recipient and the message is unread 
    ``read_at`` is set to the current datetime.
    """
    user = request.user
    now = datetime.datetime.now()
    message = get_object_or_404(Message, id=message_id)
    if (message.sender != user) and (message.recipient != user):
        raise Http404
    if message.read_at is None and message.recipient == user:
        message.read_at = now
        message.save()
    return render_to_response(template_name, {'message': message}, context_instance=RequestContext(request))