from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class MyAccountManager(BaseUserManager):
    def create_superuser(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address.")
        if "@" not in email and ".com" not in email:
            raise ValueError("Invalid email input")
        if len(password) < 8:
            raise ValueError("Password must contain at least 8 characters")

        user = self.model(email=self.normalize_email(email))
        user.is_superuser = True
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password):
        if not email:
            raise ValueError("Users must have an email address.")
        if "@" not in email and ".com" not in email:
            raise ValueError("Invalid email input")
        if len(password) < 8:
            raise ValueError("Password must contain at least 8 characters")

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    username=models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)

    code = models.CharField(max_length=100, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last joined", auto_now=True)
    
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    pws = models.CharField(max_length=100, null=True, blank=True)

    objects = MyAccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name_plural = "Users"
        ordering = ["-id"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
    
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    
    def get_full_name(self):
        return self.full_name if self.full_name else self.email.split('@')[0]
    
class ReferralCode(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return self.code 