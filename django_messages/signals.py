
from django.dispatch import Signal

message_deleted = Signal(providing_args=["message", "user"])
message_sent = Signal(providing_args=["message", "user"])
message_repled = Signal(providing_args=["message", "user"])
mesage_recovered = Signal(providing_args=["message", "user"])
message_marked_as_unread = Signal(providing_args=["message", "user"])
message_purge = Signal(providing_args=["message", "user"])
