from django.urls import re_path
from User.consumers import SimpleChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/$', SimpleChatConsumer.as_asgi()),
]