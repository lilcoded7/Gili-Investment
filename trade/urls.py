from django.urls import path
from trade.views import *


urlpatterns = [
    path('', hero, name='hero'),
    path('about/', about, name='about'),
    path('customers/dashboard/', customer_dashboard, name='customer_dashboard')
]