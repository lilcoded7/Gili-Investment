from django.urls import path
from trade.views import *

app_name = "trade"

urlpatterns = [
    path("", hero, name="hero"),
    path("about/", about, name="about"),
    path("customers/dashboard/", customer_dashboard, name="customer_dashboard"),
    path("chats/", chat_list, name="chat_list"),
    path("chat/<uuid:chat_id>/", chat_view, name="chat_view"),
    path("chat/upload/<uuid:chat_id>/", upload_file, name="upload_file"),
    path('trade/', execute_trade, name='execute_trade'),
]


