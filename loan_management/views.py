from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Loan

# Create your views here.


def loans(request):
    loans = Loan.objects.all()
    template = "loan_management/loans.html"
    context = {"loans": loans}
    return render(request, template, context)


def loan(request, id):
    loan = Loan.objects.get(id=id)
    template = "loan_management/loan.html"

    payment_history = loan.generate_payment_history()

    context = {
        "loan": loan,
        "payment_history": payment_history,
    }
    return render(request, template, context)


def payment(request, id):
    loan = Loan.objects.get(id=id)
    template = "loan_management/payment.html"
    payment_history = loan.generate_payment_history()
    selected_payment = request.GET.get("payment_type")

    if selected_payment is None or selected_payment == "interest":
        total, period_start, period_end, days, leap_year = loan.calculate_interest()
        calculated_interest = {
            "total": int(total),
            "period_start": period_start,
            "period_end": period_end,
            "days": days,
            "leap_year": leap_year,
        }
    elif selected_payment == "principal":
        pass
    elif selected_payment == "to-date":
        pass

    context = {
        "calculated_interest": locals().get("calculated_interest", None),
        "loan": loan,
        "payment_history": payment_history,
    }

    return render(request, template, context)


@require_POST
def disburse(request, id):
    loan = get_object_or_404(Loan, id=id)
    try:
        loan.disburse()
        messages.success(request, f"Loan #{loan.id} successfully disbursed!")
    except ValueError as e:
        messages.error(request, str(e))
    return redirect("loan:loan", id=id)


@require_POST
def pay_interest(request, id):
    loan = get_object_or_404(Loan, id=id)
    action = request.POST.get("action")

    total, period_start, period_end, _, _ = loan.calculate_interest(
        period_end=date.today() if action == "to_date" else None
    )
    if action == "to_date":
        total, period_start, period_end, _, _ = loan.calculate_interest(
            period_end=date.today()
        )
    elif action == "custom":
        amount = Decimal(request.POST.get("amount"))
        _, period_end = loan.calculate_days(amount)
        total, period_start, period_end, _, _ = loan.calculate_interest(
            period_end=period_end
        )
    else:
        total, period_start, period_end, _, _ = loan.calculate_interest()

    loan.process_interest(total, period_start, period_end)

    messages.success(request, f"Interest paid for Loan #{loan.id} successfully!")
    return redirect("loan:loan", id=id)
