from django.shortcuts import render


# Create your views here.
def chat_view(request, room_name):
    return render(request, 'messages/chat.html', {"room_name": room_name})
