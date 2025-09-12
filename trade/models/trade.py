from setup.basemodel import BaseModel
from trade.models.customers import Customer
from trade.models.accounts import Account
from django.db import models


class Trade(BaseModel):
    TRADE_TYPE_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]

    SYMBOL_CHOICES = [
        ('BTC/USD', 'BTC/USD'),
        ('ETH/USD', 'ETH/USD'),
        ('XRP/USD', 'XRP/USD'),
        ('LTC/USD', 'LTC/USD'),
        ('ADA/USD', 'ADA/USD'),
    ]

    LEVERAGE_CHOICES = [
        ('1x', '1x'),
        ('5x', '5x'),
        ('10x', '10x'),
        ('25x', '25x'),
        ('50x', '50x'),
    ]

    STATUS = [
        ('open', 'open'),
        ('closed', 'closed'),
    ]

    trade_type = models.CharField(max_length=4, choices=TRADE_TYPE_CHOICES, default='BUY')
    symbol = models.CharField(max_length=10, choices=SYMBOL_CHOICES, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=100, null=True, blank=True, choices=STATUS, default='open')
    leverage = models.CharField(max_length=3, choices=LEVERAGE_CHOICES, default='1x')
    stop_loss = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    take_profit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    customer_profit = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    profit_loss = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)

    close_trade = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.trade_type} {self.symbol} (${self.amount})"

