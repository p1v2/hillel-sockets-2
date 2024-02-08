from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path, re_path
from chat import consumers


websocket_urlpatterns = [
    re_path(r'chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': URLRouter([
        path('chat/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
    ]),
})