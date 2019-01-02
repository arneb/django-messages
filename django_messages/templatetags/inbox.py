from django.template import Library, Node, TemplateSyntaxError
from hashlib import md5
from urllib.parse import urlencode

register = Library()


class InboxOutput(Node):
    def __init__(self, varname=None):
        self.varname = varname

    def render(self, context):
        try:
            user = context['user']
            count = user.received_messages.filter(read_at__isnull=True, recipient_deleted_at__isnull=True).count()
        except (KeyError, AttributeError):
            count = ''
        if self.varname is not None:
            context[self.varname] = count
            return ""
        else:
            return "%s" % (count)


def do_print_inbox_count(parser, token):
    """
    A templatetag to show the unread-count for a logged in user.
    Returns the number of unread messages in the user's inbox.
    Usage::

        {% load inbox %}
        {% inbox_count %}

        {# or assign the value to a variable: #}

        {% inbox_count as my_var %}
        {{ my_var }}

    """
    bits = token.contents.split()
    if len(bits) > 1:
        if len(bits) != 3:
            raise TemplateSyntaxError("inbox_count tag takes either no arguments or exactly two arguments")
        if bits[1] != 'as':
            raise TemplateSyntaxError("first argument to inbox_count tag must be 'as'")
        return InboxOutput(bits[2])
    else:
        return InboxOutput()


@register.simple_tag
def get_gravatar(email, size=60, rating='g', default=None):
    """ Return url for a Gravatar. From Zinnia blog. """
    url = 'https://secure.gravatar.com/avatar/{0}.jpg'.format(
        md5(email.strip().lower().encode('utf-8')).hexdigest()
    )
    options = {'s': size, 'r': rating}
    if default:
        options['d'] = default

    url = '%s?%s' % (url, urlencode(options))
    return url.replace('&', '&amp;')


register.tag('inbox_count', do_print_inbox_count)
