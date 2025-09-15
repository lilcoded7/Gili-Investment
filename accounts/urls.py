from django.urls import path
from accounts.views import *

app_name = 'accounts'

urlpatterns = [
    path('register/', register, name='register'),
    path('logout/view/', logout_view, name='logout_view'),
    path('login/', login, name='login'),
    path('activate/account/<uuid:customer_id>', activate_account, name='activate_account')
]