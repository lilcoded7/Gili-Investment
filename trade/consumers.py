import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from .models import Chat, Message

User = get_user_model()


def group_name(chat_id: int) -> str:
    return f"chat_{chat_id}"


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.group = group_name(self.chat_id)

        self.chat = await sync_to_async(Chat.objects.filter(pk=self.chat_id).first)()
        user = self.scope["user"]

        if not (user.is_authenticated and self.chat and (self.chat.staff_id == user.id or self.chat.customer_id == user.id)):
            await self.close()
            return

        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data.get("message", "").strip()
        file_url = data.get("file")  
        user = self.scope["user"]

        # save message
        msg = await sync_to_async(Message.objects.create)(
            chat=self.chat,
            sender=user,
            content=content,
            file=file_url if file_url else None,
        )

        payload = {
            "id": msg.id,
            "chat": self.chat.id,
            "sender": user.id,
            "content": msg.content,
            "file": msg.file.url if msg.file else None,
            "is_read": msg.is_read,
            "created_at": msg.created_at.isoformat(),
        }

        await self.channel_layer.group_send(
            self.group,
            {
                "type": "chat.message",
                "message": payload,
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))
