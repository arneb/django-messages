import datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from ...models import Message
from django_messages.conf import settings


class Command(BaseCommand):
    args = '<minimum age in days (e.g. 30)>'
    help = (
        'Deletes messages that have been marked as deleted by both the sender '
        'and recipient. Minimum age in days is pulled from settings or given as an argument.'
    )

    def handle(self, *args, **options):
        if len(args) == 0:
            args = [settings.MESSAGES_DELETED_MAX_AGE]
        elif len(args) > 1:
            raise CommandError(
                'This management command accepts only one argument.'
            )

        try:
            age_in_days = int(args[0])
        except ValueError:
            raise CommandError('"%s" is not an integer.' % args[0])

        the_date = timezone.now() - datetime.timedelta(days=age_in_days)

        Message.objects.filter(
            recipient_deleted_at__lte=the_date,
            sender_deleted_at__lte=the_date,
        ).delete()
