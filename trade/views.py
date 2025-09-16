import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from trade.models.accounts import Account
from trade.models.customers import Customer
from django.contrib import messages
from django.db.models import Q, Sum

from trade.forms import *
from datetime import datetime
from trade.models.transactions import Transaction
from trade.models.managements import Management
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from trade.models.chats import *
from django.utils import timezone
from decimal import Decimal
import random
import json

trans = datetime.now().strftime("%Y%m%d%H%M%S")

management = Management.load()

User = get_user_model()


# Public pages
def hero(request):
    return render(request, "main/hero.html")


def about(request):
    return render(request, "main/about.html")


@login_required
def customer_dashboard(request):
    form = TradeForm(request.POST or None)
    open_trades = Trade.objects.filter(status='open')
    customer_account = Account.objects.filter(customer__user=request.user).first()

    if request.user.is_admin:
        return redirect("trade:prestige_wealth")

    context = {
        "form": form,
        "open_trades": open_trades,
        "customer": customer_account,
    }
    return render(request, "dash/customer_dashboard.html", context)


@login_required
def execute_trade(request):
    account = Account.objects.filter(customer__user=request.user).first()

    if request.method == "POST":
        form = TradeForm(request.POST, customer=account)
        if form.is_valid():
            trade = form.save(commit=False)
            trade.customer = account.customer
            account.balance -= trade.amount
            account.save()
            trade.save()
            messages.success(request, "Trade executed successfully!")
        else:
            [messages.error(request, f"{f}: {e[0]}") for f, e in form.errors.items()]

    return redirect("trade:customer_dashboard")


@login_required
def deposit_account(request):
    customer = get_object_or_404(Customer, user=request.user)
    deposits = Transaction.objects.filter(transaction_type="deposit", customer=customer)

    if request.method == "POST":
        form = DepositForm(request.POST)
        if form.is_valid():
            transaction = form.save()
            transaction.customer = customer
            transaction.transaction_id = f"{trans}{random.randint(000000, 99999)}"
            transaction.transaction_type = "deposit"
            transaction.save()
            messages.success(
                request,
                "Deposit request has been submitted successfully. "
                "Your account will be credited within 24 to 48 hours. "
                "If not, please contact support.",
            )
            return redirect("trade:deposit_account")
    else:
        form = DepositForm()

    return render(
        request,
        "dash/deposit.html",
        {"form": form, "deposits": deposits, "management": management},
    )


@login_required
def withdraw_fund(request):
    customer = get_object_or_404(Customer, user=request.user)
    withdrawals = Transaction.objects.filter(
        transaction_type="withdrawal", customer=customer
    )

    if request.method == "POST":
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            transaction = form.save()
            transaction.customer = customer
            transaction.transaction_id = f"{trans}{random.randint(000000, 99999)}"
            transaction.transaction_type = "withdrawal"
            transaction.save()
            messages.success(
                request,
                "Withdrawal request has been submitted successfully. "
                "Your account will be credited within 24 to 48 hours. "
                "If not, please contact support.",
            )
            return redirect("trade:withdraw_fund")
    else:
        form = WithdrawalForm()

    return render(
        request,
        "dash/withdraw.html",
        {"form": form, "withdrawals": withdrawals, "management": management},
    )


@login_required
def list_trade(request):
    customer = Customer.objects.filter(user=request.user).first()
    trades = Trade.objects.filter(customer=customer)

    context = {"trades": trades}
    return render(request, "dash/trade.html", context)


@login_required
def wallet_view(request):
    customer = get_object_or_404(Customer, user=request.user)
    transactions = Transaction.objects.filter(customer=customer).order_by("-created_at")
    account = Account.objects.filter(customer=customer).first()
    total_deposits = (
        Transaction.objects.filter(
            customer=customer, transaction_type="deposit", status="credited"
        ).aggregate(Sum("amount"))["amount__sum"]
        or 0
    )

    total_withdrawals = (
        Transaction.objects.filter(
            customer=customer, transaction_type="withdrawal", status="credited"
        ).aggregate(Sum("amount"))["amount__sum"]
        or 0
    )

    pending_transactions = Transaction.objects.filter(
        customer=customer, status="pending"
    ).count()

    total_transactions = transactions.count()

    if total_transactions > 0:
        deposit_count = transactions.filter(transaction_type="deposit").count()
        withdrawal_count = transactions.filter(transaction_type="withdrawal").count()

        deposit_percentage = round((deposit_count / total_transactions * 100))
        withdrawal_percentage = round((withdrawal_count / total_transactions * 100))

        completed_count = transactions.filter(status="credited").count()
        pending_count = transactions.filter(status="pending").count()
        failed_count = transactions.filter(status="failed").count()

        completed_percentage = round((completed_count / total_transactions * 100))
        pending_percentage = round((pending_count / total_transactions * 100))
    else:

        deposit_percentage = 50
        withdrawal_percentage = 50
        completed_percentage = 33
        pending_percentage = 33

    context = {
        "customer": customer,
        "account": account,
        "transactions": transactions,
        "total_deposits": total_deposits,
        "total_withdrawals": total_withdrawals,
        "pending_transactions": pending_transactions,
        "deposit_percentage": deposit_percentage,
        "withdrawal_percentage": withdrawal_percentage,
        "completed_percentage": completed_percentage,
        "pending_percentage": pending_percentage,
    }

    return render(request, "dash/wallet.html", context)


@login_required
def profile_view(request):
    form = CustomerForm()
    customer = get_object_or_404(Customer, user=request.user)
    account = Account.objects.filter(customer=customer).first()
    transactions = Transaction.objects.filter(customer=customer)

    total_transactions = transactions.count()
    verified_status = "Yes" if customer.is_active else "No"

    context = {
        "customer": customer,
        "account": account,
        "total_transactions": total_transactions,
        "verified_status": verified_status,
        "form": form,
    }

    return render(request, "dash/customer_profile.html", context)


@login_required
def prestige_wealth(request):

    if not request.user.is_admin:
        return redirect('trade:customer_dashboard')

    trades = Trade.objects.filter(status="open")
    deposits = Transaction.objects.filter(transaction_type="deposit", status="pending")
    withdrawals = Transaction.objects.filter(
        transaction_type="withdrawal", status="pending"
    )
    customers = Customer.objects.count()

    total_users = customers
    total_revenue = (
        deposits.filter(status="credited").aggregate(total=Sum("amount"))["total"] or 0
    )
    total_trades = Trade.objects.count()
    pending_withdrawals = withdrawals.filter(status="pending").count()

    recent_deposits = deposits.order_by("-created_at")[:5]
    recent_withdrawals = withdrawals.filter(status="pending").order_by("-created_at")[
        :5
    ]
    recent_trades = trades.order_by("-created_at")[:5]

    context = {
        "trades": recent_trades,
        "deposits": recent_deposits,
        "withdrawals": recent_withdrawals,
        "customers": total_users,
        "total_revenue": total_revenue,
        "total_trades": total_trades,
        "pending_withdrawals": pending_withdrawals,
    }
    return render(request, "agent/dash.html", context)


@login_required
def customers(request):
    customers = Customer.objects.select_related("user").all()
    accounts = Account.objects.select_related("customer").all()

    customer_data = []
    for c in customers:
        account = accounts.filter(customer=c).first()
        customer_data.append(
            {
                "id": c.id,
                "username": c.user.username,
                "email": c.user.email,
                "full_name": c.full_name,
                "phone": c.phone_number,
                "joined": c.created_at,
                "balance": account.balance if account else 0.00,
                "account_number": account.account_number if account else None,
                "is_active": c.is_active,
            }
        )

    context = {
        "customers": customer_data,
    }
    return render(request, "agent/customers.html", context)


def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    account = Account.objects.filter(customer=customer).first()

    if request.method == "POST":
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, "Account balance updated successfully.")
            return redirect("trade:customer_detail", customer.id)
        else:
            messages.error(request, "Failed to update account balance. Please check the value.")
    else:
        form = AccountForm(instance=account)

    context = {
        "customer": customer,
        "account": account,
        "form": form,
    }
    return render(request, "agent/customer_details.html", context)

@login_required
def customer_trade(request):
    trades = Trade.objects.select_related("customer").all()

    total_users = Customer.objects.count()
    total_revenue = Account.objects.aggregate(total=Sum("balance"))["total"] or 0
    total_trades = trades.count()
    pending_requests = trades.filter(status="open").count()

    context = {
        "trades": trades,
        "total_users": total_users,
        "total_revenue": total_revenue,
        "total_trades": total_trades,
        "pending_requests": pending_requests,
    }
    return render(request, "agent/trades.html", context)


@login_required
def edit_trade(request, trade_id):
    trade = get_object_or_404(Trade, id=trade_id)

    if request.method == "POST":
        form = EditTradeForm(request.POST, instance=trade)
        if form.is_valid():
            form.save()
            messages.success(request, "Trade Edited successfully")
            return redirect("trade:edit_trade", trade.id)
    else:
        form = EditTradeForm(instance=trade)

    return render(
        request,
        "agent/edit_trade.html",
        {"form": form, "trade": trade},
    )


@login_required
def transactions(request):
    txns = Transaction.objects.select_related("customer").all().order_by("-created_at")
    return render(request, "agent/transactions.html", {"transactions": txns})


@login_required
def support_chat_dashboard(request):
    support_agent, _ = SupportAgent.objects.get_or_create(
        user=request.user, defaults={"is_available": True}
    )

    customers = Customer.objects.filter(conversation__is_active=True).distinct()

    return render(
        request,
        "agent/support_chats.html",
        {
            "support_agent": support_agent,
            "customers": customers,
        },
    )


@login_required
def get_conversation(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    support_agent = get_object_or_404(SupportAgent, user=request.user)

    conversation, created = Conversation.objects.get_or_create(
        customer=customer, is_active=True, defaults={"support_agent": support_agent}
    )

    if not created and not conversation.is_active:
        conversation.is_active = True
        conversation.support_agent = support_agent
        conversation.save()

    messages = conversation.messages.all().order_by("timestamp")

    # Mark all customer messages as read
    conversation.messages.filter(sender_type="customer").update(is_read=True)

    messages_data = []
    for msg in messages:
        message_data = {
            "id": msg.id,
            "sender_type": msg.sender_type,
            "message_type": msg.message_type,
            "content": msg.content,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M"),
            "is_read": msg.is_read,
        }
        if msg.message_type == "file" and msg.msg_file:
            message_data["file_url"] = msg.msg_file.url
            message_data["filename"] = msg.msg_file.name.split("/")[-1]
        messages_data.append(message_data)

    return JsonResponse(
        {
            "conversation_id": conversation.id,
            "customer_name": customer.full_name,
            "customer_email": customer.user.email,
            "messages": messages_data,
        }
    )


@csrf_exempt
@login_required
def send_message(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"})

    conversation_id = request.POST.get("conversation_id")
    content = request.POST.get("content")

    if not conversation_id:
        return JsonResponse({"success": False, "error": "Missing conversation ID"})

    conversation = get_object_or_404(Conversation, id=conversation_id)

    message = Message.objects.create(
        conversation=conversation,
        sender_type="support",
        message_type="text",
        content=content,
        timestamp=timezone.now(),
    )

    if request.FILES.get("file"):
        file = request.FILES["file"]
        fs = FileSystemStorage()
        filename = fs.save(f"messages/{conversation.customer.id}/{file.name}", file)
        message.message_type = "file"
        message.msg_file = filename
        message.content = f"Sent a file: {file.name}"
        message.save()

    conversation.updated_at = timezone.now()
    conversation.save()

    response_data = {
        "success": True,
        "message_id": message.id,
        "content": message.content,
        "message_type": message.message_type,
        "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M"),
    }

    if message.message_type == "file" and message.msg_file:
        response_data["file_url"] = message.msg_file.url
        response_data["filename"] = message.msg_file.name.split("/")[-1]

    return JsonResponse(response_data)


@login_required
def close_conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    conversation.is_active = False
    conversation.save()
    return JsonResponse({"success": True})


@login_required
@csrf_exempt
def send_customer_message(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

    customer = Customer.objects.filter(user=request.user).first()
    if not customer or not customer.agent:
        return JsonResponse(
            {"success": False, "error": "No assigned agent"}, status=400
        )

    support_agent = SupportAgent.objects.filter(user=customer.agent).first()

    conversation, _ = Conversation.objects.get_or_create(
        customer=customer, support_agent=support_agent
    )

    content = request.POST.get("message", "")
    uploaded_file = request.FILES.get("file")

    if not content and not uploaded_file:
        return JsonResponse({"success": False, "error": "Empty message"}, status=400)

    msg_type = "file" if uploaded_file else "text"

    msg = Message.objects.create(
        conversation=conversation,
        sender_type="customer",
        content=content if msg_type == "text" else "",
        message_type=msg_type,
        timestamp=timezone.now(),
    )

    if uploaded_file:
        msg.file.save(uploaded_file.name, uploaded_file, save=True)

    return JsonResponse(
        {
            "success": True,
            "message_id": msg.id,
            "timestamp": msg.timestamp.strftime("%H:%M"),
            "file_url": msg.file.url if msg_type == "file" else None,
            "content": msg.content,
        }
    )


@login_required
def get_customer_conversation(request):
    customer = get_object_or_404(Customer, user=request.user)

    if not customer.agent:
        return JsonResponse({"success": False, "error": "No assigned support agent"}, status=400)

    support_agent = SupportAgent.objects.filter(user=customer.agent).first()
    if not support_agent:
        return JsonResponse({"success": False, "error": "Support agent not found"}, status=400)

    conversation, _ = Conversation.objects.get_or_create(
        customer=customer, support_agent=support_agent, is_active=True
    )

    messages = conversation.messages.all().order_by("timestamp")

    messages_data = []
    for msg in messages:
        message_data = {
            "id": msg.id,
            "sender_type": msg.sender_type,
            "message_type": msg.message_type,
            "content": msg.content,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M"),
            "is_read": msg.is_read,
        }
        if msg.message_type == "file" and msg.msg_file:
            message_data["file_url"] = msg.msg_file.url
            message_data["filename"] = msg.msg_file.name.split("/")[-1]
        messages_data.append(message_data)

    return JsonResponse({"success": True, "messages": messages_data})


def credit_customer_account(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    if transaction.status != "pending":
        messages.error(request, "Pending Transaction only")
        return redirect("trade:prestige_wealth")
    account = transaction.customer.customer_accounts
    account.balance += Decimal(transaction.amount)
    account.save()
    transaction.status = "credited"
    transaction.save()
    return redirect("trade:prestige_wealth")


def cancel_customer_account(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    if transaction.status != "pending":
        messages.error(request, "Pending Transaction only")
        return redirect("trade:prestige_wealth")
    transaction.status = "failed"
    transaction.is_canceled = True
    transaction.save()
    return redirect("trade:prestige_wealth")


def approved_customer_withdrawal(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    if transaction.status != "pending":
        messages.error(request, "Pending Transaction only")
        return redirect("trade:prestige_wealth")
    account = transaction.customer.customer_accounts
    account.balance -= Decimal(transaction.amount)
    account.save()
    transaction.status = "approved"
    transaction.save()
    return redirect("trade:prestige_wealth")


def update_customer_profile(request, user_id):
    customer = get_object_or_404(Customer, user=user_id)

    account = Account.objects.filter(customer=customer).first()
    transactions = Transaction.objects.filter(customer=customer)

    total_transactions = transactions.count()
    verified_status = "Yes" if customer.is_active else "No"

    if request.method == "POST":
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer profile updated successfully.")
            return redirect("update_customer_profile", customer_id=customer.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomerForm(instance=customer)

    context = {
        "customer": customer,
        "account": account,
        "total_transactions": total_transactions,
        "verified_status": verified_status,
        "form": form,
    }

    return render(request, "dash/customer_profile.html", context)


@login_required
def cancel_trade(request, trade_id):
    trade = Trade.objects.filter(id=trade_id).first()

    if not trade:
        messages.error(request, "Trade not found")
        return redirect("trade:customer_trade")

    if trade.status != "open":
        messages.error(request, "Trade already closed")
        return redirect("trade:customer_trade")

    trade.status = "closed"
    trade.close_trade = True
    trade.save()

    customer_account = trade.customer.customer_accounts
    customer_account.balance += trade.profit_loss
    customer_account.save()

    if trade.profit_loss >= 0:
        messages.success(
            request, f"Trade closed successfully. Profit of ${trade.profit_loss} added."
        )
    else:
        messages.warning(
            request, f"Trade closed. Loss of ${abs(trade.profit_loss)} deducted."
        )

    return redirect("trade:customer_trade")


def customer_close_trade(request, trade_id):
    trade = Trade.objects.filter(id=trade_id).first()

    if not trade:
        messages.error(request, "Trade not found")
        return redirect("trade:customer_dashboard")
    
    if not trade.allow_close_trade:
        messages.error(request, 'something occured check your internet')
        return redirect('trade:customer_dashboard')

    if trade.status != "open":
        messages.error(request, "Trade already closed")
        return redirect("trade:customer_dashboard")

    trade.status = "closed"
    trade.close_trade = True
    trade.save()

    customer_account = trade.customer.customer_accounts
    customer_account.balance += trade.profit_loss
    customer_account.save()

    if trade.profit_loss >= 0:
        messages.success(
            request, f"Trade closed successfully. Profit of ${trade.profit_loss} added."
        )
    else:
        messages.warning(
            request, f"Trade closed. Loss of ${abs(trade.profit_loss)} deducted."
        )

    return redirect("trade:customer_dashboard")
