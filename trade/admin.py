from django.contrib import admin
from trade.models.customers import Customer
from trade.models.trade import Trade
from trade.models.accounts import Account
from trade.models.chats import Chat, Message



# Register your models here.
admin.site.register(Customer)
admin.site.register(Chat)

admin.site.register(Trade)
admin.site.register(Account)
admin.site.register(Message)