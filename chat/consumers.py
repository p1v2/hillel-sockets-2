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
        
        async_to_sync(self.channel_layer.group_add)(
            "chat_broadcast", 
            self.channel_name
        )

        self.accept()

    def disconnect(self, code):
        print("Client disconnected")
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )
    
    def send_all_message(self, event):
        message = event['message']
        name = event['name']
        
        if self.channel_name != event["sender_channel"]:
            self.send(text_data=json.dumps({"message": message, "name": name}))

    def receive(self, text_data=None, bytes_data=None):
        print("Received message: ", text_data)

        data = text_data or bytes_data

        json_data = json.loads(data)

        message = json_data["message"]
        name = json_data["name"]
        
        action = json_data.get("action", None)
        if action == "send_message":
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "name": name,
                }
            )
        elif action == "send_all":
            async_to_sync(self.channel_layer.group_send)(
                "chat_broadcast",
                {
                    "type": "chat_message",
                    "message": message,
                    "name": name,
                }
            )

        
        
    def chat_message(self, event):
        message = event['message']
        name = event['name']

        self.send(text_data=json.dumps({"message": message, "name": name}))
