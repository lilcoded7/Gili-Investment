from setup.basemodel import BaseModel
from django.db import models


class SingletonManager(models.Manager):
    def get_singleton(self):
        """Get or create the singleton instance"""
        obj, created = self.get_or_create(pk=1)
        return obj

class Management(BaseModel):
    objects = SingletonManager()
    
    btc_wallet_address = models.CharField(max_length=255, blank=True)
    eth_wallet_address = models.CharField(max_length=255, blank=True)

    @classmethod
    def load(cls):
        """Get the singleton instance, create if it doesn't exist"""
        return cls.objects.get_singleton()