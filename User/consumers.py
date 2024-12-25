import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from User.models import tbl_chat
from Guest.models import tbl_user
from django.db.models import Q 


class SimpleChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        reciver = data.get('reciver')
        sender = data.get('sender')

        await self.save_message_to_db(reciver, message, sender)

        messages = await self.get_messages(reciver, sender)
        
        # Echo the message back to the sender
        await self.send(text_data=json.dumps({
            'message': message,
            'reciver': reciver,
            'messages': messages
        }))

    @sync_to_async
    def save_message_to_db(self, reciver, message, sender):
        # print(message)
        tbl_chat.objects.create(message=message, reciver=tbl_user.objects.get(id=reciver), sender=tbl_user.objects.get(id=sender))

    @sync_to_async
    def get_messages(self, reciver, sender):
        message = tbl_chat.objects.filter((Q(reciver=reciver) | Q(reciver=sender)) & (Q(sender=reciver) | Q(sender=sender)))
        return [{'message': msg.message} for msg in message]