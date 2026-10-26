from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.views import not_admin
from .models import Transaction


@login_required
def wallet(request):
    me = request.user
    transactions = me.transactions.all()
    selected_type = request.GET.get("type", "")
    if selected_type:
        transactions = transactions.filter(type=selected_type)

    context = {
        "transactions": transactions,
        "selected_type": selected_type,
        "type_choices": Transaction.TYPE_CHOICES,
        "locked": me.locked_credits(),
        "earned": me.earned_credits(),
    }
    return render(request, "wallets/wallet.html", context)


@login_required
def admin_transactions(request):
    if not_admin(request):
        return redirect("dashboard")

    transactions = Transaction.objects.all()
    selected_type = request.GET.get("type", "")
    if selected_type:
        transactions = transactions.filter(type=selected_type)
    context = {
        "transactions": transactions,
        "selected_type": selected_type,
        "type_choices": Transaction.TYPE_CHOICES,
    }
    return render(request, "wallets/admin_transactions.html", context)
