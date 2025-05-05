import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from Chatapp.models import tbl_chat
from Guest.models import tbl_user
from django.db.models import Q 
from channels.layers import get_channel_layer
from datetime import datetime

class individualchat(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the sender and receiver IDs from the query string
        query_string = self.scope['query_string'].decode()
        params = dict(param.split('=') for param in query_string.split('&'))
        self.sender = params.get('sender')
        self.reciver = params.get('reciver')
        
        # Create a unique group name for this chat
        self.room_group_name = f"chat_{min(int(self.sender), int(self.reciver))}_{max(int(self.sender), int(self.reciver))}"
        
        # Join the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        messages = await self.get_messages(params.get('reciver'), params.get('sender'))
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "messages": messages
            }
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'typing':
            # Handle typing status
            sender = text_data_json.get('sender')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_status",
                    "sender": sender
                }
            )
        elif message_type == 'clear':
            reciver = text_data_json.get('reciver')
            sender = text_data_json.get('sender')
            await self.clear_chat_messages(sender, reciver)
            messages = await self.get_messages(reciver, sender)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "messages": messages
                }
            )
        elif message_type == 'file':
            # Handle file message
            file_data = text_data_json.get('file_data')
            file_name = text_data_json.get('file_name')
            file_type = text_data_json.get('file_type')
            sender = text_data_json.get('sender')
            reciver = text_data_json.get('reciver')
            
            # Save file to database
            await self.save_file_to_db(reciver, file_data, file_name, file_type, sender)
            
            # Get all messages for this conversation
            messages = await self.get_messages(reciver, sender)
            
            # Broadcast message to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "messages": messages
                }
            )
        else:
            message = text_data_json.get('message')
            reciver = text_data_json.get('reciverid')
            sender = text_data_json.get('senderid')
            
            # Save message to database
            await self.save_message_to_db(reciver, message, sender)

            # Get all messages for this conversation
            messages = await self.get_messages(reciver, sender)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "messages": messages
                }
            )
     
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    async def typing_status(self, event):
        # Send typing status to WebSocket
        await self.send(text_data=json.dumps({
            "type": "typing",
            "sender": event["sender"]
        }))

    @sync_to_async
    def save_message_to_db(self, reciver, message, sender):
        tbl_chat.objects.create(
            message=message,
            reciver=tbl_user.objects.get(id=reciver),
            sender=tbl_user.objects.get(id=sender),
            datetime=datetime.now()
        )

    @sync_to_async
    def save_file_to_db(self, reciver, file_data, file_name, file_type, sender):
        # Decode base64 file data
        file_content = base64.b64decode(file_data.split(',')[1])
        
        # Create chat message with file data
        tbl_chat.objects.create(
            reciver=tbl_user.objects.get(id=reciver),
            sender=tbl_user.objects.get(id=sender),
            file_data=file_content,
            file_name=file_name,
            file_type=file_type,
            file_size=len(file_content),
            datetime=datetime.now()
        )

    @sync_to_async
    def get_messages(self, reciver, sender):
        messages = tbl_chat.objects.filter(
            (Q(reciver=reciver) | Q(reciver=sender)) & 
            (Q(sender=reciver) | Q(sender=sender))
        ).order_by('datetime')

        message_list = []

        for msg in messages:
            message_data = {
                'id': msg.id,
                'message': msg.message,
                'sender': str(msg.sender.id),
                'reciver': str(msg.reciver.id),
                'datetime': msg.datetime.strftime('%I:%M %p'),
                'timestamp': msg.datetime.timestamp(),
                'date':msg.datetime.strftime('%B %d, %Y'),
                'file_name': msg.file_name,
                'file_type': msg.file_type,
                'file_size': msg.file_size
            }

            if msg.file_data:
                try:
                    # Convert file data to base64 string
                    file_data = base64.b64encode(msg.file_data).decode('utf-8')
                    message_data['file_data'] = file_data
                except Exception as e:
                    print(f"Error encoding file data: {e}")
                    message_data['file_data'] = None
            else:
                message_data['file_data'] = None
            
            message_list.append(message_data)

        return sorted(message_list, key=lambda x: x['timestamp'])           

    @sync_to_async
    def clear_chat_messages(self, sender, reciver):
        # Delete all messages between these users
        tbl_chat.objects.filter(
            (Q(reciver=reciver) | Q(reciver=sender)) & 
            (Q(sender=reciver) | Q(sender=sender))
        ).delete()