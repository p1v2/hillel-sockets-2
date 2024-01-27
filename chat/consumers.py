import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        print("New client connected")
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_" + self.room_name
        self.generalroom = 'chat_general'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        #add to the general group to be able to receive general messages
        async_to_sync(self.channel_layer.group_add)(
            self.generalroom,
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
        data = text_data or bytes_data

        json_data = json.loads(data)

        message = json_data["message"]
        name = json_data["name"]
        receiverroom = json_data['room']

        # checks if the given 'room' value is 'all', if True sends the message to the general group
        if receiverroom != 'all':
            print(f'Received message: {text_data} in {self.room_group_name}')
            
            async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'name': name,
            }
        )

        else:
            print(f'Received message: {text_data} in all chats')
            
            async_to_sync(self.channel_layer.group_send)(
            self.generalroom,
            {
                'type': 'chat_message',
                'message': message,
                'name': name,
                })



    def chat_message(self, event):
        message = event['message']
        name = event['name']

        self.send(text_data=json.dumps({"message": message, "name": name}))
