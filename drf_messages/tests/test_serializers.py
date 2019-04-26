from model_mommy import mommy
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from rest_framework_simplejwt.state import User

from drf_messages.models import Message
from drf_messages.serializers import ComposeSerializer


class TestMessageSerializers(APITestCase):

    def test_message_subject_is_required(self):
        data = dict(
            body='The body of the message',
            sent_at='2019-04-23T17:11',
            sender='1',
            recipient=['1', '2']
        )
        serializer = ComposeSerializer(data=data)
        serializer.is_valid()
        self.assertListEqual(
            serializer.errors.get('subject'),
            [ErrorDetail(string='This field is required.', code='required')]
        )

    def test_message_body_is_required(self):
        data = dict(
            subject='A Message to Recipient',
            sent_at='2019-04-23T17:11',
            sender='1',
            recipient=['1', '2']
        )
        serializer = ComposeSerializer(data=data)
        serializer.is_valid()
        self.assertListEqual(
            serializer.errors.get('body'),
            [ErrorDetail(string='This field is required.', code='required')]
        )

    def test_message_recipient_is_required(self):
        data = dict(
            subject='A Message to Recipient',
            body='The body of the message',
            sent_at='2019-04-23T17:11',
            sender='1',
        )
        serializer = ComposeSerializer(data=data)
        serializer.is_valid()
        self.assertListEqual(
            serializer.errors.get('recipient'),
            [ErrorDetail(string='This field is required.', code='required')]
        )

    def test_message_recipient_should_be_iterable(self):
        data = dict(
            subject='A Message to Recipient',
            body='The body of the message',
            sent_at='2019-04-23T17:11',
            sender='1',
            recipient='1'
        )
        serializer = ComposeSerializer(data=data)
        serializer.is_valid()
        self.assertListEqual(
            serializer.errors.get('recipient'),
            [ErrorDetail(string='Expected a list of items but got type "str".', code='not_a_list')]
        )

    def test_message_recipient_should_exist_in_db(self):
        data = dict(
            subject='A Message to Recipient',
            body='The body of the message',
            sent_at='2019-04-23T17:11',
            sender='1',
            recipient='1'
        )
        serializer = ComposeSerializer(data=data)
        serializer.is_valid()
        self.assertListEqual(
            serializer.errors.get('recipient'),
            [ErrorDetail(string='Expected a list of items but got type "str".', code='not_a_list')]
        )

    def test_create_method_with_sender(self):
        sender = mommy.make(User)
        recipient = mommy.make(User)
        data = dict(
            subject='A Message to Recipient',
            body='The body of the message',
            sent_at='2019-04-23T17:11',
            sender='1',
            recipient=[recipient.id]
        )
        serializer = ComposeSerializer(data=data)
        serializer.is_valid()
        message_instance = serializer.save(sender=sender)[0]
        self.assertEqual(message_instance.get('subject'), data.get('subject'))
        self.assertIsNone(message_instance.get('parent_msg'))

    def test_create_method_with_parent_message(self):
        parent_message = mommy.make(Message)
        sender = mommy.make(User)
        recipient = mommy.make(User)
        data = dict(
            subject='A Message to Recipient',
            body='The body of the message',
            sent_at='2019-04-23T17:11',
            sender='1',
            recipient=[recipient.id]
        )
        serializer = ComposeSerializer(data=data)
        serializer.is_valid()
        message_instance = serializer.save(sender=sender, parent_msg=parent_message)[0]
        self.assertEqual(message_instance.get('subject'), data.get('subject'))
        self.assertEquals(message_instance.get('parent_msg'), parent_message.id)
