from django import forms
from django.contrib.auth import get_user_model, authenticate
import re

User = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={
            "class": "form-control", 
            "placeholder": "enter your email"
            }
        ),
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
            "class": "form-control", 
            "type": "password"
            }
        ),
    )
    def clean(self):
        validated_data = super().clean()
        email = validated_data.get('email')
        password = validated_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise forms.ValidationError("Invalid email or password")  # ✅ fixed
            self.user = user
        return validated_data


class RegisterForm(forms.Form):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
            "class": "form-control",
            "placeholder": "enter your username"
            }
        ),
    )
    full_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
            "class": "form-control", 
            "placeholder": "enter your full name"
            }
        ),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={
            "class": "form-control", "placeholder": 
            "enter your email"
            }
        ),
    )
    country_code = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
            "class": "form-control", 
            "placeholder": "enter country code"
            }
        ),
    )
    phone_number = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
            "class": "form-control", 
            "placeholder": "000 000 000"
            }
        ),
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
            "class": "form-control", 
            "placeholder": "enter your password"
            }
        ),
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
            "class": "form-control", 
            "placeholder": "confirm your password"
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match")

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("email already exist")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")

        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", password):
            raise forms.ValidationError(
                "Password must contain at least one uppercase letter."
            )
        if not re.search(r"[a-z]", password):
            raise forms.ValidationError(
                "Password must contain at least one lowercase letter."
            )
        if not re.search(r"\d", password):
            raise forms.ValidationError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise forms.ValidationError(
                "Password must contain at least one special character."
            )

        return password


class ActivateAccounForm(forms.Form):
    code = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter code to activate your account",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get("code")

        if not User.objects.filter(code=code).exists():
            raise forms.ValidationError(
                "Verification code does not exist, enter a valid code"
            )

        return cleaned_data
