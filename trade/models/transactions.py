from setup.basemodel import BaseModel
from trade.models.customers import Customer
from django.db import models


class Transaction(BaseModel):
    SYMBOL_CHOICES = [
        ('BTC/USD', 'BTC/USD'),
        ('ETH/USD', 'ETH/USD'),
        
    ]
    STATUS = [
        ('pending', 'pending'),
        ('credited', 'credited'),
        ('approved', 'approved'),
        ('failed', 'failed'),
    ]
    TYPE = [
        ('withdrawal', 'withdrawal'),
        ('deposit', 'deposit'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=100, choices=SYMBOL_CHOICES)
    transaction_type = models.CharField(max_length=100, choices=TYPE, null=True, blank=True)
    wallet_address = models.CharField(max_length=225, null=True, blank=True)
    status = models.CharField(max_length=100, choices=STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    response = models.JSONField(null=True, blank=True)

    is_canceled = models.BooleanField(default=False)

    def __str__(self):
        return f"Customer: {self.customer.full_name} Amount: {self.amount} Status: {self.status}"