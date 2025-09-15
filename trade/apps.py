from django.apps import AppConfig
from django.contrib import admin

class TradeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trade'

    def ready(self):

        from trade.models.managements import Management
        admin.site.register(Management)
