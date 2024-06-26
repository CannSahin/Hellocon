import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from .models import Message, Room, UserMessages
from .utils import send_notification

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs'].get('room_name')
        self.usernames = self.scope['url_route']['kwargs'].get('usernames')

        if self.room_name:
            self.room_group_name = f'chat_{self.room_name}'
        elif self.usernames:
            self.room_group_name = f'chat_{self.usernames[0]}_{self.usernames[1]}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        json_data = json.loads(text_data)
        username = json_data.get("username")
        self.room_name = self.scope['url_route']['kwargs'].get('room_name')
        self.usernames = self.scope['url_route']['kwargs'].get('usernames')
        room = json_data.get("room")
        message = json_data.get("message")
        receiver = json_data.get("receiver")

        if self.room_name:
            
            await self.save_room_message(username, room, message)
            await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'username': username,
                'room': room,
                'message': message
            }
        )
        else:
            await self.save_user_message(username, receiver, message)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'username': username,
                    'room': room,
                    'message': message
                }
            )           

    async def chat_message(self, event):
        username = event.get("username")
        room = event.get("room")
        message = event.get("message")

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'room': room,
        }))

    @sync_to_async
    def save_room_message(self, username, room, message):
        user = User.objects.get(username=username)
        room = Room.objects.get(slug=room)
        Message.objects.create(user=user, room=room, message_text=message)

    @sync_to_async
    def save_user_message(self, sender_username, receiver_username, message):
        sender = User.objects.get(username=sender_username)
        receiver = User.objects.get(username=receiver_username)
        UserMessages.objects.create(sender_name=sender, receiver_name=receiver, description=message)
        send_notification(receiver)
