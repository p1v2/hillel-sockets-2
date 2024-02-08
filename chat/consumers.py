from channels.generic.websocket import AsyncWebsocketConsumer
import json


class ChatConsumer(AsyncWebsocketConsumer):
    # List of all active groups
    active_groups = []
    # List of all connected users
    connected_users = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = None
        self.room_group_name = None

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Add the group to the list of active groups
        if self.room_group_name not in self.active_groups:
            self.active_groups.append(self.room_group_name)

        # Add the user to the list of connected users
        if self not in self.connected_users:
            self.connected_users.append(self)

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Remove the group from the list of active groups
        if self.room_group_name in self.active_groups:
            self.active_groups.remove(self.room_group_name)

        # Remove the user from the list of connected users
        if self in self.connected_users:
            self.connected_users.remove(self)

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            name = text_data_json['name']
            broadcast_flag = text_data_json['broadcast_flag']

            # If broadcast_flag is True, send the message to all users
            if broadcast_flag:
                for user in self.connected_users:
                    await user.send(text_data=json.dumps({
                        'message': message,
                        'name': name,
                        'broadcast_flag': broadcast_flag
                    }))
            # Otherwise, send the message to the current group
            else:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'name': name,
                        'broadcast_flag': broadcast_flag
                    }
                )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        name = event['name']
        broadcast_flag = event['broadcast_flag']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'name': name,
            'broadcast_flag': broadcast_flag
        }))