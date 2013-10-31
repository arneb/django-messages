from django.dispatch import Signal

# User sends a message
message_sent    = Signal(providing_args=["msg_list", "request"])
message_reply   = Signal(providing_args=["msg_list", "request"])
message_read    = Signal(providing_args=["message", "request"])
message_deleted = Signal(providing_args=["message", "request"])
