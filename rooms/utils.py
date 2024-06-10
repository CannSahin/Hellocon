from django.urls import register_converter
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import UserMessages
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class UserChatConverter:
    regex = '[^/]+-[^/]+'

    def to_python(self, value):
        user1, user2 = value.split('-')
        return sorted([user1, user2])

    def to_url(self, value):
        user1, user2 = sorted(value)
        return f'{user1}-{user2}'

register_converter(UserChatConverter, 'userchat')


def send_notification(username):

    unseen_message_count = UserMessages.objects.filter(receiver_name=username, seen=False).count()
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{username}',
        {
            'type': 'send_notification',
            'notification_count': unseen_message_count
        }
    )