import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    GROUP_ALL = "ALL"

    def connect(self):
        print("New client connected")
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_" + self.room_name

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        async_to_sync(self.channel_layer.group_add)(
            self.GROUP_ALL,
            self.channel_name
        )

        self.accept()

    def disconnect(self, code):
        print("Client disconnected")
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

    def receive(self, text_data=None, bytes_data=None):
        print("Received message: ", text_data)

        data = text_data or bytes_data

        json_data = json.loads(data)

        group_name = self.GROUP_ALL if json_data.get("room") == self.GROUP_ALL else self.room_group_name

        async_to_sync(self.channel_layer.group_send)(
            group_name,
            {
                'type': 'chat_message',
                'message': json_data["message"],
                'name': json_data["name"],
            }
        )

    def chat_message(self, event):
        message = event['message']
        name = event['name']

        self.send(text_data=json.dumps({"message": message, "name": name}))
