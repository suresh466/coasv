from datetime import timedelta
from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import LoanPaymentForm
from .models import InterestPayment, Loan, PrincipalPayment

# Create your views here.


def loans(request):
    loans = Loan.objects.all()
    template = "loan_management/loans.html"
    context = {"loans": loans}
    return render(request, template, context)


def loan(request, id):
    loan = Loan.objects.get(id=id)
    if loan.status in (Loan.FULLYPAID, Loan.DEFAULTED):
        return closed_loan(request, loan)
    else:
        return active_loan(request, loan)


def active_loan(request, loan):
    template = "loan_management/loan.html"

    total = period_start = period_end = days = leap_year = None

    if loan.status == loan.ACTIVE:
        total, period_start, period_end, days, leap_year = loan.calculate_interest()
    payment_history, running_interest, running_principal, running_total = (
        loan.generate_payment_history()
    )

    form = LoanPaymentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        interest = form.cleaned_data["interest"]
        principal = form.cleaned_data["principal"]

        try:
            loan.process_payment(interest, principal)
            messages.success(
                request,
                f"Payment of Interest: ${interest} Principal: ${principal} successfully processed",
            )
            return redirect("loan:loan", id=loan.id)
        except Exception as e:
            print(e)
            messages.error(request, str(e))
            raise e

    context = {
        "loan": loan,
        "form": form,
        "payment_history": payment_history,
        "total_paid": {
            "interest": running_interest,
            "principal": running_principal,
            "total": running_total,
        },
        "interest": {
            "amount": total,
            "period_start": period_start,
            "period_end": period_end,
            "days": days,
            "leap_year": leap_year,
        },
    }
    return render(request, template, context)


def closed_loan(request, loan):
    template = "loan_management/closed_loan.html"

    # Get payment history
    interest_payments = InterestPayment.objects.filter(loan=loan).order_by(
        "-payment_date"
    )
    principal_payments = PrincipalPayment.objects.filter(loan=loan).order_by(
        "-payment_date"
    )
    running_interest = Decimal("0.00")
    running_principal = Decimal("0.00")
    running_total = Decimal("0.00")
    payment_history = []

    # Combine and sort payments for history
    for ip in interest_payments:
        end_time = ip.payment_date + timedelta(seconds=2)
        pp = principal_payments.filter(
            payment_date__gte=ip.payment_date, payment_date__lte=end_time
        ).first()
        if pp:
            running_interest += ip.amount
            running_principal += pp.amount
            running_total = running_interest + running_principal

            payment_history.append(
                {
                    "date": ip.payment_date,
                    "interest": ip.amount,
                    "principal": pp.amount,
                    "total": ip.amount + pp.amount,
                    "running_interest": running_interest,
                    "running_principal": running_principal,
                    "running_total": running_total,
                }
            )
        else:
            running_interest += ip.amount
            running_total = running_interest + running_principal

            payment_history.append(
                {
                    "date": ip.payment_date,
                    "interest": ip.amount,
                    "principal": 0,
                    "total": ip.amount + 0,
                    "running_interest": running_interest,
                    "running_principal": running_principal,
                    "running_total": running_total,
                }
            )

    context = {
        "loan": loan,
        "payment_history": payment_history,
        "total_paid": {
            "interest": running_interest,
            "principal": running_principal,
            "total": running_total,
        },
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
