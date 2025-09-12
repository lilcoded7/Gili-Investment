import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from trade.models.accounts import Account
from django.contrib import messages
from django.db.models import Q

from trade.models.chats import Chat, Message
from trade.forms import *

# Public pages
def hero(request):
    return render(request, "main/hero.html")


def about(request):
    return render(request, "main/about.html")


def customer_dashboard(request):
    form = TradeForm(request.POST)
    open_trades = Trade.objects.filter()
    customer_account = Account.objects.filter(customer__user=request.user).first()

    context = {
        'form':form,
        'open_trades':open_trades,
        'customer':customer_account
    }
    return render(request, "dash/customer_dashboard.html", context)


# Chat views
@login_required
def chat_list(request):
    form = TradeForm(request.POST)
    
    chats = Chat.objects.filter(Q(customer=request.user) | Q(staff=request.user))

    context = {
        'form':form,
        'chats':chats
    }
    return render(request, "chat/chat_list.html", context)


def execute_trade(request):
    account = Account.objects.filter(customer__user=request.user).first()
    if request.method == "POST":
        form = TradeForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']

            if not account.balance >=amount:
                messages.error(request, 'Insuffcient balance')
                return redirect('trade:customer_dashboard')

            account.balance-=amount
            account.save()
            form.save()
            return redirect('trade:customer_dashboard') 
    else:
        form = TradeForm()
    return render(request, 'trade_form.html', {'form': form})


@login_required
def chat_view(request, chat_id):
    chat = get_object_or_404(
        Chat.objects.filter(Q(customer=request.user) | Q(staff=request.user)),
        id=chat_id
    )
    messages = chat.messages.select_related("sender").order_by("created_at")
    return render(request, "chat/chat.html", {
        "chat": chat,
        "messages": messages,
        "user": request.user,
    })


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
            content=request.POST.get("message", "")
        )

        return JsonResponse({
            "file_url": file_url,
            "message": msg.content,
            "sender": request.user.id,
            "timestamp": msg.created_at.strftime("%H:%M"),
        })

    return JsonResponse({"error": "Invalid request"}, status=400)
