from django.urls import path

from . import consumers
from .import consumernotify
from .utils import UserChatConverter


websocket_urlpatterns = [
    path('ws/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
    path('ws/userchat/<userchat:usernames>/', consumers.ChatConsumer.as_asgi()),
    path('ws/notify/<str:username>/', consumernotify.NotificationConsumer.as_asgi()),
]