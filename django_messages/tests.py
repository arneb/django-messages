from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils import timezone
from django_messages.models import Message
from django_messages.utils import format_subject, format_quote

from .utils import get_user_model

User = get_user_model()


class SendTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            'user1', 'user1@example.com', '123456')
        self.user2 = User.objects.create_user(
            'user2', 'user2@example.com', '123456')
        self.msg1 = Message(sender=self.user1, recipient=self.user2,
                            subject='Subject Text', body='Body Text')
        self.msg1.save()

    def testBasic(self):
        self.assertEqual(self.msg1.sender, self.user1)
        self.assertEqual(self.msg1.recipient, self.user2)
        self.assertEqual(self.msg1.subject, 'Subject Text')
        self.assertEqual(self.msg1.body, 'Body Text')
        self.assertEqual(self.user1.sent_messages.count(), 1)
        self.assertEqual(self.user1.received_messages.count(), 0)
        self.assertEqual(self.user2.received_messages.count(), 1)
        self.assertEqual(self.user2.sent_messages.count(), 0)


class DeleteTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            'user3', 'user3@example.com', '123456')
        self.user2 = User.objects.create_user(
            'user4', 'user4@example.com', '123456')
        self.msg1 = Message(sender=self.user1, recipient=self.user2,
                            subject='Subject Text 1', body='Body Text 1')
        self.msg2 = Message(sender=self.user1, recipient=self.user2,
                            subject='Subject Text 2', body='Body Text 2')
        self.msg1.sender_deleted_at = timezone.now()
        self.msg2.recipient_deleted_at = timezone.now()
        self.msg1.save()
        self.msg2.save()

    def testBasic(self):
        self.assertEqual(Message.objects.outbox_for(self.user1).count(), 1)
        self.assertEqual(
            Message.objects.outbox_for(self.user1)[0].subject,
            'Subject Text 2'
        )
        self.assertEqual(Message.objects.inbox_for(self.user2).count(), 1)
        self.assertEqual(
            Message.objects.inbox_for(self.user2)[0].subject,
            'Subject Text 1'
        )
        #undelete
        self.msg1.sender_deleted_at = None
        self.msg2.recipient_deleted_at = None
        self.msg1.save()
        self.msg2.save()
        self.assertEqual(Message.objects.outbox_for(self.user1).count(), 2)
        self.assertEqual(Message.objects.inbox_for(self.user2).count(), 2)


class IntegrationTestCase(TestCase):
    """
    Test the app from a user perpective using Django's Test-Client.
    """

    T_USER_DATA = [{'username': 'user_1', 'password': '123456',
                    'email': 'user_1@example.com'},
                   {'username': 'user_2', 'password': '123456',
                    'email': 'user_2@example.com'}]
    T_MESSAGE_DATA = [{'subject': 'Test Subject 1',
                       'body': 'Lorem ipsum\ndolor sit amet\n\nconsectur.'}]

    def setUp(self):
        """ create 2 users and a test-client logged in as user_1 """
        self.user_1 = User.objects.create_user(**self.T_USER_DATA[0])
        self.user_2 = User.objects.create_user(**self.T_USER_DATA[1])
        self.c = Client()
        self.c.login(username=self.T_USER_DATA[0]['username'],
                     password=self.T_USER_DATA[0]['password'])

    def testInboxEmpty(self):
        """ request the empty inbox """
        response = self.c.get(reverse('messages_inbox'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name,
                         'django_messages/inbox.html')
        self.assertEqual(len(response.context['message_list']), 0)

    def testOutboxEmpty(self):
        """ request the empty outbox """
        response = self.c.get(reverse('messages_outbox'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name,
                         'django_messages/outbox.html')
        self.assertEqual(len(response.context['message_list']), 0)

    def testTrashEmpty(self):
        """ request the empty trash """
        response = self.c.get(reverse('messages_trash'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name,
                         'django_messages/trash.html')
        self.assertEqual(len(response.context['message_list']), 0)

    def testCompose(self):
        """ compose a message step by step """
        response = self.c.get(reverse('messages_compose'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name,
                         'django_messages/compose.html')
        response = self.c.post(
            reverse('messages_compose'),
            {
                'recipient': self.T_USER_DATA[1]['username'],
                'subject': self.T_MESSAGE_DATA[0]['subject'],
                'body': self.T_MESSAGE_DATA[0]['body']
            })
        # successfull sending should redirect to inbox
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'],
                         "http://testserver%s" % reverse('messages_inbox'))

        # make sure the message exists in the outbox after sending
        response = self.c.get(reverse('messages_outbox'))
        self.assertEqual(len(response.context['message_list']), 1)

    def testReply(self):
        """ test that user_2 can reply """
        # create a message for this test
        Message.objects.create(sender=self.user_1,
                               recipient=self.user_2,
                               subject=self.T_MESSAGE_DATA[0]['subject'],
                               body=self.T_MESSAGE_DATA[0]['body'])
        # log the user_2 in and check the inbox
        self.c.login(username=self.T_USER_DATA[1]['username'],
                     password=self.T_USER_DATA[1]['password'])
        response = self.c.get(reverse('messages_inbox'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name,
                         'django_messages/inbox.html')
        self.assertEqual(len(response.context['message_list']), 1)
        pk = getattr(response.context['message_list'][0], 'pk')
        # reply to the first message
        response = self.c.get(reverse('messages_reply',
                              kwargs={'message_id': pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name,
                         'django_messages/compose.html')
        self.assertEqual(
            response.context['form'].initial['body'],
            format_quote(self.user_1, self.T_MESSAGE_DATA[0]['body'])
        )
        self.assertEqual(
            response.context['form'].initial['subject'],
            u"Re: %(subject)s" % {'subject': self.T_MESSAGE_DATA[0]['subject']}
        )


class FormatTestCase(TestCase):
    """ some tests for helper functions """
    def testSubject(self):
        """ test that reply counting works as expected """
        self.assertEqual(format_subject(u"foo bar"), u"Re: foo bar")
        self.assertEqual(format_subject(u"Re: foo bar"), u"Re[2]: foo bar")
        self.assertEqual(format_subject(u"Re[2]: foo bar"), u"Re[3]: foo bar")
        self.assertEqual(format_subject(u"Re[10]: foo bar"),
                         u"Re[11]: foo bar")
