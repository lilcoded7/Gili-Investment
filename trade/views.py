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
    open_trades = Trade.objects.filter()
    customer_account = Account.objects.filter(customer__user=request.user).first()
    sessions = ChatSession.objects.filter(
        status="open", customer__user=request.user
    ).order_by("-started_at")

    active_session = sessions.first()
    chat_messages = []
    if active_session:
        chat_messages = Message.objects.filter(chat=active_session).order_by(
            "timestamp"
        )

    context = {
        "form": form,
        "open_trades": open_trades,
        "customer": customer_account,
        "sessions": sessions,
        "chat_messages": chat_messages,
    }
    return render(request, "dash/customer_dashboard.html", context)


@login_required
def execute_trade(request):
    account = Account.objects.filter(customer__user=request.user).first()
    if request.method == "POST":
        form = TradeForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]

            if not account.balance >= amount:
                messages.error(request, "Insuffcient balance")
                return redirect("trade:customer_dashboard")

            account.balance -= amount
            account.save()
            form.save()
            return redirect("trade:customer_dashboard")
        else:
            form = TradeForm()

    return redirect("trade:customer_dashboard")


@login_required
def upload_file(request, chat_id):
    """
    Handle file uploads for chat messages.
    """
    if request.method == "POST" and request.FILES.get("file"):
        chat = get_object_or_404(
            Chat.objects.filter(Q(customer=request.use | Q(staff=request.user))),
            id=chat_id,
        )

        f = request.FILES["file"]
        saved_name = default_storage.save(f"chat_files/{uuid.uuid4()}_{f.name}", f)
        file_url = default_storage.url(saved_name)

        msg = Message.objects.create(
            chat=chat,
            sender=request.user,
            file=saved_name,
            content=request.POST.get("message", ""),
        )

        return JsonResponse(
            {
                "file_url": file_url,
                "message": msg.content,
                "sender": request.user.id,
                "timestamp": msg.created_at.strftime("%H:%M"),
            }
        )

    return JsonResponse({"error": "Invalid request"}, status=400)


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
    trades = Trade.objects.all()

    context = {"trades": trades}
    return render(request, "dash/trade.html", context)


@login_required
def wallet_view(request):
    customer = get_object_or_404(Customer, user=request.user)
    transactions = Transaction.objects.filter(customer=customer).order_by("-created_at")

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
    }

    return render(request, "dash/customer_profile.html", context)


@login_required
def update_profile(request):
    if request.method == "POST":
        customer = get_object_or_404(Customer, user=request.user)

        customer.full_name = request.POST.get("full_name", "")
        customer.phone = request.POST.get("phone", "")
        customer.country = request.POST.get("country", "")
        customer.address = request.POST.get("address", "")
        customer.save()

        user = request.user
        user.email = request.POST.get("email", "")
        user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    return redirect("profile")


@csrf_exempt
def send_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=403)

    customer = Customer.objects.filter(user=request.user).first()
    if not customer:
        return JsonResponse({"error": "Customer not found"}, status=404)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    message_text = data.get("message")
    if not message_text:
        return JsonResponse({"error": "Message is required"}, status=400)

    # Find or create a chat session
    chat, created = ChatSession.objects.get_or_create(
        customer=customer,
        agent=customer.agent,
        status="open",
        defaults={"started_at": now()},
    )

    # Save customer's message
    customer_msg = Message.objects.create(
        chat=chat,
        sender="customer",
        content=message_text,
    )

    # Optional: fetch latest agent reply if exists
    support_msg = Message.objects.filter(chat=chat, sender="agent").last()

    return JsonResponse(
        {
            "success": True,
            "chat_id": chat.id,
            "customer_message": {
                "id": customer_msg.id,
                "content": customer_msg.content,
                "sender": customer_msg.sender,
                "timestamp": customer_msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "support_message": (
                {
                    "id": support_msg.id,
                    "content": support_msg.content,
                    "sender": support_msg.sender,
                    "timestamp": support_msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                }
                if support_msg
                else None
            ),
        }
    )


@login_required
def customer_support(request):
    customer = get_object_or_404(Customer, user=request.user)

    sessions = ChatSession.objects.filter(customer=customer).order_by("-started_at")

    session_and_chat_conversation = [
        {
            "chat": chat_session,
            "messages": Message.objects.filter(chat=chat_session).order_by("timestamp"),
        }
        for chat_session in sessions
    ]

    context = {
        "sessions": session_and_chat_conversation,
        "customer": customer,
    }
    return render(request, "dash/chat.html", context)


@login_required
def dash_admin_support(request):

    trades = Trade.objects.filter(status="open")
    deposits = Transaction.objects.filter(transaction_type="deposit")
    withdrawals = Transaction.objects.filter(transaction_type="withdrawal")
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
    return render(request, "dash_admin/dash.html", context)


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
    return render(request, "dash_admin/customers.html", context)


@login_required
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    account = Account.objects.filter(customer=customer).first()
    context = {
        "customer": customer,
        "account": account,
    }
    return render(request, "dash_admin/customer_details.html", context)


@login_required
def customer_trade(request):

    return render(request, "dash_admin/trades.html")


@login_required
def edit_trade(request, trade_id):
    trade = get_object_or_404(Trade, id=trade_id)
    if request.method == "POST":
        form = TradeForm(request.POST, instance=trade)
        if form.is_valid():
            form.save()
            return redirect("customer_trade")  #
    else:
        form = TradeForm(instance=trade)

    return render(request, "dash_admin/edit_trade.html", {"form": form, "trade": trade})


@login_required
def transactions(request):
    txns = Transaction.objects.select_related("customer").all().order_by("-created_at")
    return render(request, "dash_admin/transactions.html", {"transactions": txns})





@login_required
def support_chat_dashboard(request):
    support_agent, _ = SupportAgent.objects.get_or_create(
        user=request.user,
        defaults={'is_available': True}
    )

    customers = Customer.objects.filter(
        conversation__is_active=True
    ).distinct()

    return render(request, "dash_admin/support_chats.html", {
        "support_agent": support_agent,
        "customers": customers,
    })


@login_required
def get_conversation(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    support_agent = get_object_or_404(SupportAgent, user=request.user)

    conversation, created = Conversation.objects.get_or_create(
        customer=customer,
        is_active=True,
        defaults={"support_agent": support_agent}
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

    return JsonResponse({
        "conversation_id": conversation.id,
        "customer_name": customer.full_name,
        "customer_email": customer.user.email,
        "messages": messages_data,
    })


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
