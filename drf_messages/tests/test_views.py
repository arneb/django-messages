from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from model_mommy import mommy
from drf_messages.models import Message


class TestMessages(APITestCase):
    def setUp(self) -> None:
        self.url = '/messages'
        self.sender = self._get_new_user()
        self.recipient = self._get_new_user()

        self._login(self.sender)

    # Compose Messages (Inbox, Outbox)
    def test_composed_message_sent_to_one_recipient_appears_once_in_the_recipient_inbox(self):
        message_compose_data = self._get_composed_message()
        response = self.client.post(self.url+'/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        self._login(self.recipient)
        response = self.client.get(self.url+'/inbox/')
        self.assertEquals(len(response.data.get('messages_list')), 1)

    def test_composed_message_sent_to_one_recipient_appears_once_in_the_sender_outbox(self):
        message_compose_data = self._get_composed_message()
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.url + '/outbox/')
        self.assertEquals(len(response.data.get('messages_list')), 1)

    def test_one_composed_message_sent_to_three_recipients_appears_thrice_in_the_sender_outbox(self):
        message_compose_data = self._get_composed_message()
        recipient_two = mommy.make(User)
        recipient_three = mommy.make(User)
        message_compose_data['recipient'] = [self.recipient.id, recipient_two.id, recipient_three.id]

        # sender is sending a message to three recipients
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, 201)

        # sender is listing her outbox
        response = self.client.get(self.url + '/outbox/')
        self.assertEquals(len(response.data.get('messages_list')), 3)

    def test_one_composed_message_sent_to_three_recipient_appears_once_in_the_every_recipient_inbox(self):
        message_compose_data = self._get_composed_message()
        recipient_two = self._get_new_user()
        recipient_three = self._get_new_user()
        message_compose_data['recipient'] = [self.recipient.id, recipient_two.id, recipient_three.id]

        # sender is sending a message to three recipients
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, 201)    # Message successfully sent
        self.assertEquals(len(response.data.get('messages_list')), 3)    # Message sent to three recipients

        self._login(self.recipient)
        # self recipient is listing her inbox
        response = self.client.get(self.url + '/inbox/')
        self.assertEquals(len(response.data.get('messages_list')), 1)    # Inbox contains exactly one message

        self._login(recipient_two)
        # recipient_one is listing her inbox
        response = self.client.get(self.url + '/inbox/')
        self.assertEquals(len(response.data.get('messages_list')), 1)    # Inbox contains exactly one message

        self._login(recipient_three)
        # recipient_two is listing her inbox
        response = self.client.get(self.url + '/inbox/')
        self.assertEquals(len(response.data.get('messages_list')), 1)    # Inbox contains exactly one message

    # View Messages
    def test_sender_can_view_the_message(self):
        message_compose_data = self._get_composed_message()
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        message_id = response.data.get('messages_list')[0]['id']

        response = self.client.get(self.url + '/' + message_id + '/view/')  # Sender is viewing the message
        self.assertEquals(message_id, response.data.get('message')['id'])   # Sender successfully viewd the message

    def test_recipient_can_view_the_message(self):
        message_compose_data = self._get_composed_message()
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        message_id = response.data.get('messages_list')[0]['id']

        self._login(self.recipient)
        response = self.client.get(self.url + '/' + message_id + '/view/')  # Recipient is viewing the message
        self.assertEquals(message_id, response.data.get('message')['id'])   # Recipient successfully viewd the message

    def test_users_other_than_sender_and_recipient_can_not_view_the_message(self):
        message_compose_data = self._get_composed_message()
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        message_id = response.data.get('messages_list')[0]['id']

        self._login(user=self._get_new_user())
        response = self.client.get(self.url + '/' + message_id + '/view/')  # user other than sender and recipient is viewing the message
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)  # user other than sender and recipient could not viewd the message

    def test_read_at_populated_when_recipient_viewed_the_message_first_time(self):
        message_compose_data = self._get_composed_message()
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        message = response.data.get('messages_list')[0]
        message_id = response.data.get('messages_list')[0]['id']

        self.assertIsNone(message['read_at'])   # Message has not been read

        self._login(self.recipient)
        response = self.client.get(self.url + '/' + message_id + '/view/')  # recipient is viewing/reading the message
        self.assertIsNotNone(response.data.get('message')['read_at'])   # message has been read by the recipient

    def test_read_at_is_not_populated_when_sender_views_the_messages(self):
        message_compose_data = self._get_composed_message()
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        message = response.data.get('messages_list')[0]
        message_id = response.data.get('messages_list')[0]['id']

        self.assertIsNone(message['read_at'])   # Message has not been read

        response = self.client.get(self.url + '/' + message_id + '/view/')  # sender is viewing/reading the message
        self.assertIsNone(response.data.get('message')['read_at'])  # message has not been marked as read

    # # Delete Messages
    def test_sender_can_delete_the_message_only_for_herself(self):
        message_compose_data = self._get_composed_message()
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        message = response.data.get('messages_list')[0]
        message_id = response.data.get('messages_list')[0]['id']

        self.assertIsNone(message['sender_deleted_at'])  # message has not been deleted for sender

        response = self.client.put(self.url + '/' + message_id + '/delete/')    # sender is deleting the message
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)     # message has been deleted successfully for the sender

        self._login(self.recipient)
        response = self.client.get(self.url + '/' + message_id + '/view/')  # recipient is viewing the message
        self.assertIsNotNone(response.data.get('message')['sender_deleted_at'])  # message has been deleted for sender
        self.assertIsNone(response.data.get('message')['recipient_deleted_at'])  # message has not been deleted for recipient

    def test_recipient_can_delete_the_message_only_for_herself(self):
        message_compose_data = self._get_composed_message()
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        message = response.data.get('messages_list')[0]
        message_id = response.data.get('messages_list')[0]['id']

        self.assertIsNone(message['recipient_deleted_at'])  # message has not been deleted for recipient

        self._login(self.recipient)
        response = self.client.put(self.url + '/' + message_id + '/delete/')    # recipient is deleting the message
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)     # message has been deleted successfully for the recipient

        self._login(self.sender)
        response = self.client.get(self.url + '/' + message_id + '/view/')  # sender is viewing the message
        self.assertIsNone(response.data.get('message')['sender_deleted_at'])    # message has not been deleted for sender
        self.assertIsNotNone(response.data.get('message')['recipient_deleted_at'])  # message has been deleted for recipient

    def test_users_other_than_sender_and_recipient_can_not_delete_the_message(self):
        message_compose_data = self._get_composed_message()
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        message_id = response.data.get('messages_list')[0]['id']

        other_user = self._get_new_user()
        self._login(other_user)
        response = self.client.put(self.url + '/' + message_id + '/delete/')    # user other than sender/recipient is trying to delete the message
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)  # user other than sender/recipient could not delete the message

    # # Delete + View
    def test_message_deleted_by_sender_can_be_viewed_by_recipient_but_can_not_be_viewed_by_sender(self):
        message_compose_data = self._get_composed_message()
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        message_id = response.data.get('messages_list')[0]['id']

        response = self.client.put(self.url + '/' + message_id + '/delete/')    # sender is deleting the message
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)     # message has been deleted successfully for the sender

        response = self.client.get(self.url + '/' + message_id + '/view/')  # sender is trying to view the message
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)  # sender could not view the deleted message

        self._login(self.recipient)
        response = self.client.get(self.url + '/' + message_id + '/view/')  # recipient is trying to view the message
        self.assertEquals(response.data.get('message')['id'], message_id)   # recipient has successfully viewed the message deleted for the sender

    def test_message_deleted_by_recipient_can_be_viewed_by_sender_but_can_not_be_viewed_by_recipient(self):
        message_compose_data = self._get_composed_message()
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        message_id = response.data.get('messages_list')[0]['id']

        self._login(self.recipient)
        response = self.client.put(self.url + '/' + message_id + '/delete/')    # recipient is deleting the message
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)     # message has been deleted successfully for the recipient

        response = self.client.get(self.url + '/' + message_id + '/view/')  # recipient is trying to view the message
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)  # recipient could not view the deleted message

        self._login(self.sender)
        response = self.client.get(self.url + '/' + message_id + '/view/')  # sender is trying to view the message
        self.assertEquals(response.data.get('message')['id'], message_id)   # sender has successfully viewed the message deleted for the sender

    def test_message_deleted_by_both_sender_and_recipient_can_not_be_viewed_by_both(self):
        message_compose_data = self._get_composed_message()
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, 201)
        message_id = response.data.get('messages_list')[0]['id']

        # Sender is deleting the message
        response = self.client.put(self.url + '/' + message_id + '/delete/')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

        # sender is viewing the message
        response = self.client.get(self.url + '/' + message_id + '/view/')
        # Sender can not view the message
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

        self._login(self.recipient)
        # Recipient is deleting the message
        response = self.client.put(self.url + '/' + message_id + '/delete/')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.url + '/' + message_id + '/view/')
        # Recipient can not view the message
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    # # Delete + Trash + Inbox + Outbox
    def test_message_deleted_by_sender_appears_in_her_trash(self):
        message_compose_data = self._get_composed_message()
        # Sender is posting a message to recipient
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, 201)
        message_id = response.data.get('messages_list')[0]['id']

        # Before delete a message there is no message in Trash
        response = self.client.get(self.url + '/trash/')
        self.assertEquals(len(response.data.get('messages_list')), 0)

        # Sender is deleting the message
        response = self.client.put(self.url + '/' + message_id + '/delete/')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

        # sender is listing trash message
        response = self.client.get(self.url + '/trash/')
        self.assertEquals(len(response.data.get('messages_list')), 1)

    def test_message_deleted_by_recipient_appears_in_her_trash(self):
        message_compose_data = self._get_composed_message()
        # Sender is posting a message to recipient
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, 201)
        message_id = response.data.get('messages_list')[0]['id']

        self._login(self.recipient)
        # Before delete a message there is no message in Trash
        response = self.client.get(self.url + '/trash/')
        self.assertEquals(len(response.data.get('messages_list')), 0)

        # Recipient is deleting the message
        response = self.client.put(self.url + '/' + message_id + '/delete/')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

        # recipient is listing trash message
        response = self.client.get(self.url + '/trash/')
        self.assertEquals(len(response.data.get('messages_list')), 1)

    def test_message_deleted_by_sender_appears_in_recipient_inbox(self):
        message_compose_data = self._get_composed_message()
        # Sender is posting a message to recipient
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, 201)
        message_id = response.data.get('messages_list')[0]['id']

        # Sender is deleting the message
        response = self.client.put(self.url + '/' + message_id + '/delete/')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

        self._login(self.recipient)
        # recipient is listing inbox message
        response = self.client.get(self.url + '/inbox/')
        self.assertEquals(len(response.data.get('messages_list')), 1)

    def test_message_deleted_by_recipient_appears_in_sender_outbox(self):
        message_compose_data = self._get_composed_message()
        # Sender is posting a message to recipient
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, 201)
        message_id = response.data.get('messages_list')[0]['id']

        self._login(self.recipient)
        # Recipient is deleting the message
        response = self.client.put(self.url + '/' + message_id + '/delete/')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

        self._login(self.sender)
        # sender is listing outbox message
        response = self.client.get(self.url + '/outbox/')
        self.assertEquals(len(response.data.get('messages_list')), 1)

    # Recover Deleted Message
    def test_sender_can_recover_her_deleted_message(self):
        message_compose_data = self._get_composed_message()
        # Sender is posting a message to recipient
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, 201)
        message_id = response.data.get('messages_list')[0]['id']

        # Sender is deleting the message
        response = self.client.put(self.url + '/' + message_id + '/delete/')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

        # sender is listing outbox message
        response = self.client.get(self.url + '/outbox/')
        self.assertEquals(len(response.data.get('messages_list')), 0)

        # sender is recovering the deleted message
        response = self.client.put(self.url + '/' + message_id + '/undelete/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # sender is listing outbox message
        response = self.client.get(self.url + '/outbox/')
        self.assertEquals(len(response.data.get('messages_list')), 1)

    def test_recipient_can_recover_her_deleted_message(self):
        message_compose_data = self._get_composed_message()
        # Sender is posting a message to recipient
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, 201)
        message_id = response.data.get('messages_list')[0]['id']

        self._login(self.recipient)
        # Recipient is deleting the message
        response = self.client.put(self.url + '/' + message_id + '/delete/')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

        # recipient is listing inbox message
        response = self.client.get(self.url + '/inbox/')
        self.assertEquals(len(response.data.get('messages_list')), 0)

        response = self.client.put(self.url + '/' + message_id + '/undelete/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # recipient is listing inbox message
        response = self.client.get(self.url + '/inbox/')
        self.assertEquals(len(response.data.get('messages_list')), 1)

    def test_recovered_message_appears_in_outbox_of_sender(self):
        message_compose_data = self._get_composed_message()
        # Sender is posting a message to recipient
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, 201)
        message_id = response.data.get('messages_list')[0]['id']

        # Sender is deleting the message
        response = self.client.put(self.url + '/' + message_id + '/delete/')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

        # sender is listing outbox message
        response = self.client.get(self.url + '/outbox/')
        self.assertEquals(len(response.data.get('messages_list')), 0)

        # sender is recovering the deleted message
        response = self.client.put(self.url + '/' + message_id + '/undelete/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # sender is listing outbox message
        response = self.client.get(self.url + '/outbox/')
        self.assertEquals(len(response.data.get('messages_list')), 1)

    def test_recovered_message_does_not_appear_in_trash_of_sender(self):
        message_compose_data = self._get_composed_message()
        # Sender is posting a message to recipient
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, 201)
        message_id = response.data.get('messages_list')[0]['id']

        # Sender is deleting the message
        response = self.client.put(self.url + '/' + message_id + '/delete/')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

        # sender is listing trash message
        response = self.client.get(self.url + '/trash/')
        self.assertEquals(len(response.data.get('messages_list')), 1)

        # sender is recovering the deleted message
        response = self.client.put(self.url + '/' + message_id + '/undelete/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # sender is listing trash message
        response = self.client.get(self.url + '/trash/')
        self.assertEquals(len(response.data.get('messages_list')), 0)

    def test_recovered_message_appears_in_inbox_of_recipient(self):
        message_compose_data = self._get_composed_message()
        # Sender is posting a message to recipient
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, 201)
        message_id = response.data.get('messages_list')[0]['id']

        self._login(self.recipient)
        # Recipient is deleting the message
        response = self.client.put(self.url + '/' + message_id + '/delete/')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

        # recipient is listing inbox message
        response = self.client.get(self.url + '/inbox/')
        self.assertEquals(len(response.data.get('messages_list')), 0)

        response = self.client.put(self.url + '/' + message_id + '/undelete/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # recipient is listing inbox message
        response = self.client.get(self.url + '/inbox/')
        self.assertEquals(len(response.data.get('messages_list')), 1)

    def test_recovered_message_does_not_appear_in_trash_of_recipient(self):
        message_compose_data = self._get_composed_message()
        # Sender is posting a message to recipient
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, 201)
        message_id = response.data.get('messages_list')[0]['id']

        self._login(self.recipient)
        # Recipient is deleting the message
        response = self.client.put(self.url + '/' + message_id + '/delete/')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

        # recipient is listing inbox message
        response = self.client.get(self.url + '/trash/')
        self.assertEquals(len(response.data.get('messages_list')), 1)

        response = self.client.put(self.url + '/' + message_id + '/undelete/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # recipient is listing inbox message
        response = self.client.get(self.url + '/trash/')
        self.assertEquals(len(response.data.get('messages_list')), 0)

    def test_users_other_than_sender_recipient_can_not_recover_message(self):
        message_compose_data = self._get_composed_message()
        # Sender is posting a message to recipient
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, 201)
        message_id = response.data.get('messages_list')[0]['id']

        # Recipient is deleting the message
        response = self.client.put(self.url + '/' + message_id + '/delete/')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

        other_user = self._get_new_user()
        self._login(other_user)
        response = self.client.put(self.url + '/' + message_id + '/undelete/')
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    # # Reply to Message
    def test_recipient_can_reply_to_sender(self):
        message_compose_data = self._get_composed_message()
        # Sender is posting a message to recipient
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, 201)
        message_id = response.data.get('messages_list')[0]['id']

        self._login(self.recipient)
        # Recipient is replying to sender
        reply_message_data = self._get_reply_message()
        response = self.client.post(self.url + '/' + message_id + '/reply/', data=reply_message_data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_no_user_other_than_recipient_can_reply_to_sender(self):
        message_compose_data = self._get_composed_message()
        # Sender is posting a message to recipient
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, 201)
        message_id = response.data.get('messages_list')[0]['id']

        other_user = self._get_new_user()
        self._login(other_user)
        # Recipient is replying to sender
        reply_message_data = self._get_reply_message()
        response = self.client.post(self.url + '/' + message_id + '/reply/', data=reply_message_data)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_recipient_reply_to_sender_appears_in_recipient_outbox(self):
        message_compose_data = self._get_composed_message()
        # Sender is posting a message to recipient
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, 201)
        message_id = response.data.get('messages_list')[0]['id']

        self._login(self.recipient)
        # Recipient is replying to sender
        reply_message_data = self._get_reply_message()
        response = self.client.post(self.url + '/' + message_id + '/reply/', data=reply_message_data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.url + '/outbox/')
        self.assertEquals(len(response.data.get('messages_list')), 1)

    def test_recipient_reply_to_sender_appears_in_sender_inbox(self):
        message_compose_data = self._get_composed_message()
        # Sender is posting a message to recipient
        response = self.client.post(self.url + '/compose/', data=message_compose_data)
        self.assertEquals(response.status_code, 201)
        message_id = response.data.get('messages_list')[0]['id']

        self._login(self.recipient)
        # Recipient is replying to sender
        reply_message_data = self._get_reply_message()
        response = self.client.post(self.url + '/' + message_id + '/reply/', data=reply_message_data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        self._login(self.sender)
        response = self.client.get(self.url + '/inbox/')
        self.assertEquals(len(response.data.get('messages_list')), 1)

    def _login(self, user):
        sender_response = self.client.post('/api/token/', data={'username': user.username, 'password': 'secret'})
        token = sender_response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    @staticmethod
    def _get_new_user():
        user = mommy.make(User)
        user.set_password('secret')
        user.save()
        return user

    def _get_composed_message(self):
        return dict(
            subject='A Message for Recipient',
            body='This is the body of the message for recipient',
            sent_at='2019-04-23T17:11',
            sender=self.sender.id,
            recipient=[self.recipient.id]
        )

    def _get_reply_message(self):
        return dict(
            subject='A Reply to Sender for her Message',
            body='This is the body of the reply message for sender',
            sent_at='2019-04-23T17:11',
            sender=self.sender.id,
            recipient=[self.sender.id]
        )
