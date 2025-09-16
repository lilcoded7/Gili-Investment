# urls.py
from django.urls import path
from trade.views import *

app_name = "trade"
urlpatterns = [
    path("", hero, name="hero"),
    path("about/", about, name="about"),
    path("customers/dashboard/", customer_dashboard, name="customer_dashboard"),
    path("create/trade/", execute_trade, name="execute_trade"),
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
    path("edit/trade/<uuid:trade_id>/edit/", edit_trade, name="edit_trade"),
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
    path(
        "customer/conversation/",
        get_customer_conversation,
        name="get_customer_conversation",
    ),
    path(
        "credit/customer/account/<uuid:transaction_id>",
        credit_customer_account,
        name="credit_customer_account",
    ),
    path(
        "cancel/customer/account/<uuid:transaction_id>",
        cancel_customer_account,
        name="cancel_customer_account",
    ),
    path(
        "approved/customer/withdrawal/<uuid:transaction_id>",
        approved_customer_withdrawal,
        name="approved_customer_withdrawal",
    ),
    path(
        "update/customer/profile/<int:user_id>",
        update_customer_profile,
        name="update_customer_profile",
    ),
    path("cancle/trade/<uuid:trade_id>", cancel_trade, name="cancel_trade"),
    path("customer/close/trade/<uuid:trade_id>", customer_close_trade, name="customer_close_trade"),
]
