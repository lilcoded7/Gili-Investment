from setup.basemodel import BaseModel
from django.db import models
from django.contrib.auth import get_user_model 

User = get_user_model()


class Chat(BaseModel):
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_chats')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_chats')
    note = models.TextField(blank=True)

    class Meta:
        unique_together = ('staff', 'customer')

    def __str__(self):
        return f"{self.customer} ↔ {self.staff}"
    

class Message(BaseModel):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(null=True, blank=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message {self.id} in Chat {self.chat.id}"