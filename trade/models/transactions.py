from setup.basemodel import BaseModel
from trade.models.customers import Customer
from trade.models.accounts import Account
from django.db import models

class Transaction(BaseModel):
    TRANSACTION_TYPES = [
        ("TRANSFER", "Bank Transfer"),
        ("MOBILE_MONEY", "Mobile Money"),
        ("DEPOSIT", "Deposit"),
        ("WITHDRAWAL", "Withdrawal"),
        ("BILL_PAYMENT", "Bill Payment"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=True, blank=True
    )
    transaction_id = models.CharField(
        max_length=30, unique=True, null=True, blank=True
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default="GHS")

    sender_account = models.ForeignKey(
        Account, on_delete=models.PROTECT,
        related_name="sent_transactions",
        null=True, blank=True
    )
    recipient_account = models.ForeignKey(
        Account, on_delete=models.PROTECT,
        related_name="received_transactions",
        null=True, blank=True,
    )

    # Mobile Money
    recipient_number = models.CharField(max_length=20, null=True, blank=True)
    network = models.CharField(max_length=50, null=True, blank=True)

    # Bill Payment
    bill_type = models.CharField(max_length=100, null=True, blank=True)
    recipient_account_number = models.CharField(max_length=50, null=True, blank=True)

    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="COMPLETED")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} {self.currency}"
