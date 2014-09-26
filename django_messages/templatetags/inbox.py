from django.template import Library, Node, TemplateSyntaxError


class InboxOutput(Node):

    INBOX = 'inbox'
    OUTBOX = 'outbox'
    TRASH = 'trash'

    def __init__(self, varname=None, box=INBOX, only_new=True, include_deleted=False):
        """
        @param varname: If provided, will assign the result into varname variable in template context
        @param box: name of the message box to count
        @param only_new: If set to True, will only count the new messages
        @param include_deleted: if set to True, will count deleted messages in the box too
        """
        self.varname = varname
        self.only_new = only_new
        self.include_deleted = include_deleted
        self.box = box

    def render(self, context):
        try:
            user = context['user']
            messages = {
                'inbox': user.received_messages.inbox_for(user),
                'outbox': user.sent_messages.outbox_for(user),
                'trash': user.received_messages.trash_for(user) | user.sent_messages.trash_for(user),
            }.get(self.box, 'inbox')

            if self.only_new:
                messages = messages.filter(read_at__isnull=True)

            if not self.include_deleted:
                messages = messages.filter(recipient_deleted_at__isnull=True)

            count = messages.count()
        except (KeyError, AttributeError):
            count = ''
        if self.varname is not None:
            context[self.varname] = count
            return ""
        else:
            return "%s" % (count)


def get_box_count(box=InboxOutput.INBOX, include_deleted=False, only_new=True):
    """
    Creates and returns a templatetag callable.
    @param box: the box name to retreive the objects from
    @type box: str
    @param include_deleted: if set to True will include deleted messages
    @type include_deleted: bool
    @param only_new: if set to True will only return the new un-read messages
    @type include_deleted: bool
    @rtype callable
    """
    def do_print_inbox_count(parser, token):
        """
        A templatetag to show the message count for a logged in user.
        Returns the number of messages in the user's message box.
        Usage:

            {% load inbox %}
            {% new_inbox_count %}

            {# or assign the value to a variable: #}

            {% new_inbox_count as my_var %}
            {{ my_var }}

        Tags:
            {% new_inbox_count %} {# count of new messages in INBOX #}
            {% inbox_count %} {# count of all INBOX #}
            {% new_outbox_count %}
            {% outbox_count %}
            {% trash_count %}

        @type token: django.template.base.Token
        """
        bits = token.contents.split()
        if len(bits) > 1:
            if len(bits) != 3:
                raise TemplateSyntaxError("inbox_count tag takes either no arguments or exactly two arguments")
            if bits[1] != 'as':
                raise TemplateSyntaxError("first argument to inbox_count tag must be 'as'")
            return InboxOutput(varname=bits[2], box=box, include_deleted=include_deleted, only_new=only_new)
        else:
            return InboxOutput(box=box, include_deleted=include_deleted, only_new=only_new)

    return do_print_inbox_count

register = Library()

setup = {
    'new_inbox_count': {
        'box': InboxOutput.INBOX,
        'include_deleted': False,
    },
    'inbox_count': {
        'box': InboxOutput.INBOX,
        'only_new': False,
    },
    'new_outbox_count': {
        'box': InboxOutput.OUTBOX
    },
    'outbox_count': {
        'box': InboxOutput.OUTBOX,
        'only_new': False,
    },
    'trash_count': {
        'box': InboxOutput.TRASH,
        'include_deleted': True,
        'only_new': False,
    },
}

for tagname, defaults in setup.items():
    register.tag(tagname, get_box_count(**defaults))
