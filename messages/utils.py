from django.utils.text import wrap
from django.contrib.sites.models import Site
from django.template import Context, loader
from django.conf import settings


def format_quote(text):
    """
    Wraps text at 55 chars and prepends each
    line with `> `.
    Used for quoting messages in replies.
    """
    lines = wrap(text, 55).split('\n')
    for i, line in enumerate(lines):
        lines[i] = "> %s" % line
    return '\n'.join(lines)
    
def new_message_email(sender, instance, signal, subject_prefix='Neue Nachricht:', template_name="mails/new_message.txt", *args, **kwargs):
    """
    This function sends an email and is called via django's dispatcher framework.
    Optional arguments:
        ``template_name``: the template to use
        ``subject_prefix``: prefix for the email subject.
    """
    if 'created' in kwargs and kwargs['created']: #only works with django-trunk
        try:
            from django.core.mail import send_mail
            current_domain = Site.objects.get_current().domain
            subject = "%s %s" % (subject_prefix, instance.subject)
            message_template = loader.get_template(template_name)
            message_context = Context({ 'site_url': 'http://%s/' % current_domain,
                                        'message': instance })
            message = message_template.render(message_context)
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.recipient.email,])
        except:
            raise
    