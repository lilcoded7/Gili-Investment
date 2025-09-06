from setup.basemodel import BaseModel
from trade.models.customers import Customer
from django.db import models


class Trade(BaseModel):
    ACTION = [("Buy", "Buy"), ("Sell", "Sell")]
    STATUS = [
        ("pending", "pending"),
        ("Lost", "Lost"),
        ("Win", "Win"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    action = models.CharField(max_length=100, choices=ACTION)
    status = models.CharField(max_length=100, choices=STATUS)
    leverage = models.IntegerField(default=1)
    stop_loss = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    take_profit = models.DecimalField(decimal_places=2, max_digits=11, default=0.00)

    def __str__(self):
        return self.customer.full_name
