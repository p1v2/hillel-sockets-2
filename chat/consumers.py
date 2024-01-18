import json
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        print("New client connected")
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_" + self.room_name

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, code):
        print("Client disconnected")
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

    async def receive(self,text_data=None, bytes_data=None):
        data = text_data or bytes_data
        data = json.loads(data)
        message = data['message']
        room = data['room']
        send_all = data.get('send_all', False)  # По умолчанию False, если ключ не существует

        # Отправить сообщение всем подключенным пользователям в комнате
        await self.send(text_data=json.dumps({
            'message': message,
            'name': self.scope['user'].username,
        }), room=room)

        # Если установлен флаг "Отправить все", отправить сообщение всем подключенным пользователям в других комнатах
        if send_all:
            await self.channel_layer.group_add(room, self.channel_name)
            await self.channel_layer.group_discard(room, self.channel_name)
            await self.send(text_data=json.dumps({
                'message': f'Send all: {message}',
                'name': {self.scope['user'].username},  # Имя отправителя
            }))
    def chat_message(self, event):
        message = event['message']
        name = event['name']

        self.send(text_data=json.dumps({"message": message, "name": name}))
