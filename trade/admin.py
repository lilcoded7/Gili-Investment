from django.contrib import admin
from trade.models.customers import Customer
from trade.models.trade import Trade
from trade.models.accounts import Account
from trade.models.chats import *
from trade.models.transactions import Transaction
from trade.models.managements import Management


# Register your models here.
admin.site.register(Customer)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(SupportAgent)

admin.site.register(Trade)
admin.site.register(Account)
admin.site.register(Transaction)
