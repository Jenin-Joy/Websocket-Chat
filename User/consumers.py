import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from User.models import tbl_chatold
from Guest.models import tbl_user
from django.db.models import Q 
from channels.layers import get_channel_layer
from datetime import datetime


class SimpleChatConsumer(AsyncWebsocketConsumer):
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
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'message')
        
        if message_type == 'typing':
            # Handle typing status
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_status",
                    "sender": text_data_json.get('sender'),
                    "is_typing": text_data_json.get('is_typing')
                }
            )
        elif message_type == 'clear_chat':
            # Handle clear chat request
            sender = text_data_json.get('sender')
            reciver = text_data_json.get('reciver')
            
            # Clear messages from database
            await self.clear_chat_messages(sender, reciver)
            
            # Notify all users in the chat
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.cleared",
                    "sender": sender,
                    "reciver": reciver
                }
            )
        elif message_type == 'delete_message':
            # Handle message deletion
            message_id = text_data_json.get('message_id')
            sender = text_data_json.get('sender')
            reciver = text_data_json.get('reciver')
            
            # Delete message from database
            await self.delete_message(message_id)
            
            # Get all messages for this conversation
            messages = await self.get_messages(reciver, sender)
            
            # Broadcast updated messages to the group
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
            # Handle regular message
            message = text_data_json.get('message')
            reciver = text_data_json.get('reciver')
            sender = text_data_json.get('sender')

            # Save message to database
            await self.save_message_to_db(reciver, message, sender)

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

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    async def typing_status(self, event):
        # Send typing status to WebSocket
        await self.send(text_data=json.dumps({
            "type": "typing",
            "sender": event["sender"],
            "is_typing": event["is_typing"]
        }))

    async def chat_cleared(self, event):
        # Send clear chat notification to WebSocket
        await self.send(text_data=json.dumps({
            "type": "chat_cleared",
            "sender": event["sender"],
            "reciver": event["reciver"]
        }))

    @sync_to_async
    def save_message_to_db(self, reciver, message, sender):
        tbl_chatold.objects.create(
            message=message,
            reciver=tbl_user.objects.get(id=reciver),
            sender=tbl_user.objects.get(id=sender)
        )

    @sync_to_async
    def save_file_to_db(self, reciver, file_data, file_name, file_type, sender):
        # Decode base64 file data
        file_content = base64.b64decode(file_data.split(',')[1])
        
        # Create chat message with file data
        tbl_chatold.objects.create(
            message=f"Sent a {file_type}",
            reciver=tbl_user.objects.get(id=reciver),
            sender=tbl_user.objects.get(id=sender),
            file_data=file_content,
            file_name=file_name,
            file_type=file_type,
            file_size=len(file_content)
        )

    @sync_to_async
    def get_messages(self, reciver, sender):
        messages = tbl_chatold.objects.filter(
            (Q(reciver=reciver) | Q(reciver=sender)) & 
            (Q(sender=reciver) | Q(sender=sender))
        ).order_by('datetime')
        
        message_list = []
        for msg in messages:
            message_data = {
                'id': msg.id,
                'message': msg.message,
                'sender': str(msg.sender.id),
                'sender_name': msg.sender.user_name,
                'reciver': str(msg.reciver.id),
                'reciver_name': msg.reciver.user_name,
                'datetime': msg.datetime.strftime('%Y-%m-%d %H:%M:%S'),
                'timestamp': msg.datetime.timestamp(),
                'file_name': msg.file_name,
                'file_type': msg.file_type,
                'file_size': msg.file_size
            }
            
            # Handle file data if present
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
        tbl_chatold.objects.filter(
            (Q(reciver=reciver) | Q(reciver=sender)) & 
            (Q(sender=reciver) | Q(sender=sender))
        ).delete()

    @sync_to_async
    def delete_message(self, message_id):
        # Delete the message from database
        tbl_chatold.objects.filter(id=message_id).delete()