from django.contrib import admin
from accounts.models import User, ReferralCode
# Register your models here.


admin.site.register(User)
admin.site.register(ReferralCode)