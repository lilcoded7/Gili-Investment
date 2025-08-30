from django.db import models
from setup.basemodel import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()

class Customer(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True)
    full_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=20, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    referial_code = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Name: {self.full_name}"