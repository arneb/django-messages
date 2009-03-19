from django.template import Library, Node

class InboxOutput(Node):
    def render(self, context):
        user = context['user']
        count = user.received_messages.filter(messagerecipient__read_at__isnull=True, messagerecipient__deleted_at__isnull=True).count()
        print user.received_messages.filter(messagerecipient__read_at__isnull=True, messagerecipient__deleted_at__isnull=True)
        return "%s" % (count)        
        
def do_print_inbox_count(parser, token):
    """
    A templatetag to show the unread-count for a logged in user.
    Prints the number of unread messages in the user's inbox.
    Usage::
        {% load inbox %}
        {% inbox_count %}
     
    """
    return InboxOutput()

register = Library()     
register.tag('inbox_count', do_print_inbox_count)