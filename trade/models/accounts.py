from setup.basemodel import BaseModel
from trade.models.customers import Customer
from django.db import models
import random, datetime


def gen_account():
    return f"PW{datetime.datetime.now().year} {random.randint(000000, 999999)}"


class Account(BaseModel):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='customer_accounts')
    balance = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    account_number = models.CharField(max_length=20, editable=False,unique=True, default=gen_account())

    def __str__(self):
        return f"Customer: {self.customer.full_name} Blance: {self.balance} Account No. {self.account_number}"