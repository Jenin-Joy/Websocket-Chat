from django.urls import re_path
from Chatapp.consumers import individualchat

websocket_urlpatterns = [
    re_path(r'individual/chat/$', individualchat.as_asgi()),
]