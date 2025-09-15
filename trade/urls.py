# urls.py
from django.urls import path
from trade.views import *

app_name = "trade"

urlpatterns = [
    path("", hero, name="hero"),
    path("about/", about, name="about"),
    path("customers/dashboard/", customer_dashboard, name="customer_dashboard"),
    path("trade/", execute_trade, name="execute_trade"),
    path("deposit/account/", deposit_account, name="deposit_account"),
    path("withdraw/fund/", withdraw_fund, name="withdraw_fund"),
    path("list/trade/", list_trade, name="list_trade"),
    path("wallet/", wallet_view, name="wallet"),
    path("profile/view/", profile_view, name="profile_view"),
    path("prestige/wealth/", prestige_wealth, name="prestige_wealth"),
    path("customers/", customers, name="customers"),
    path("customers/<uuid:customer_id>/", customer_detail, name="customer_detail"),
    path("customer/trade/", customer_trade, name="customer_trade"),
    path("transactions/", transactions, name="transactions"),
    path("trades/", customer_trade, name="customer_trade"),
    path("trade/<uuid:trade_id>/edit/", edit_trade, name="edit_trade"),
    path("dash/support/", support_chat_dashboard, name="support_chat"),
    path(
        "support/conversation/<uuid:customer_id>/",
        get_conversation,
        name="get_conversation",
    ),
    path("support/send_message/", send_message, name="send_message"),
    path(
        "support/close_conversation/<uuid:conversation_id>/",
        close_conversation,
        name="close_conversation",
    ),
    path("send-chat/", send_customer_message, name="send_chat"),
]
