from django.shortcuts import render, get_object_or_404, redirect
from accounts.forms import *
from django.contrib import messages
from accounts.utils import EmailSender
from django.contrib.auth import get_user_model
from trade.models.customers import Customer
from django.contrib.auth import authenticate, login as auth_login
import random

# Create your views here.

User = get_user_model()

sender = EmailSender()


def register(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                email=data.get("email"), password=data.get("password")
            )
            user.set_password(data.get("password"))
            user.code = f"{random.randint(0, 9999):04}"
            user.save()

            customer = Customer.objects.create(
                user=user,
                full_name=data.get("full_name"),
                country_code=data.get("country_code"),
                phone_number=data.get("phone_number"),
            )
            user.username = data.get("username")
            user.save()
            try:
                sender.send_verify_account_code(user)
            except:
                pass
            messages.success(
                request,
                "An activation code has been sent to your email address. Please check and verify your account.",
            )
            return redirect("activate_account", customer.id)

    context = {
        "form": form,
    }
    return render(request, "auth/register.html", context)


def login(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        auth_login(request, form.user)
        return redirect('dashboard')
    return render(request, "auth/login.html", {'form':form})


def activate_account(request, customer_id):
    form = ActivateAccounForm()
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == "POST":
        form = ActivateAccounForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            customer.user.is_active = True
            customer.user.save()
            messages.success(request, "Account Activation Successfully")
            return redirect("login")

    try:
        sender.send_verify_account_code(customer.user)
     
    except:
        pass

    return render(request, "auth/account_activation.html", {"customer": customer, 'form':form})
