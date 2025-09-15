from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from trade.models.customers import Customer
from setup.basemodel import BaseModel

User = get_user_model()


class SupportAgent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    is_available = models.BooleanField(default=True)

    # def __str__(self):
    #     return self.user.username


class Conversation(BaseModel):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=True, blank=True
    )
    support_agent = models.ForeignKey(
        SupportAgent, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-updated_at"]

    # def __str__(self):
    #     return f"Conversation with "


class Message(models.Model):
    MESSAGE_TYPES = (
        ("text", "Text"),
        ("file", "File"),
    )
    SENDER_TYPES = (
        ("customer", "Customer"),
        ("support", "Support Agent"),
    )

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
        blank=True,
    )
    sender_type = models.CharField(
        max_length=10, choices=SENDER_TYPES, default="customer"
    )
    message_type = models.CharField(
        max_length=10, choices=MESSAGE_TYPES, default="text"
    )
    content = models.TextField(blank=True, null=True)
    msg_file = models.FileField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"Message"
