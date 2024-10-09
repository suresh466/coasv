from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import LoanPaymentForm
from .models import InterestPayment, Loan, PrincipalPayment

# Create your views here.


def loans(request):
    loans = Loan.objects.all()
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print(loans)
    template = "loan_management/loans.html"
    context = {"loans": loans}
    return render(request, template, context)


def loan(request, id):
    template = "loan_management/loan.html"
    loan = Loan.objects.get(id=id)

    # Calculate necessary amounts
    payoff_interest, payoff_principal, payoff_total, _ = (
        loan.calculate_next_payment_amount(payoff=True)
    )
    _, _, next_payment_amount, _ = loan.calculate_next_payment_amount()

    # Get payment history
    interest_payments = InterestPayment.objects.filter(loan=loan).order_by(
        "-payment_date"
    )
    principal_payments = PrincipalPayment.objects.filter(loan=loan).order_by(
        "-payment_date"
    )

    # Combine and sort payments for history
    running_interest = Decimal("0.00")
    running_principal = Decimal("0.00")
    running_total = Decimal("0.00")
    payment_history = []

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

    # Generate repayment schedule
    repayment_schedule = loan.generate_amortization_schedule()

    if request.method == "POST":
        form = LoanPaymentForm(
            request.POST,
            loan=loan,
            next_payment_amount=next_payment_amount,
            payoff_amount=payoff_total,
        )
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            payment_type = form.cleaned_data["payment_type"]

            try:
                if payment_type == "payoff":
                    loan.process_payment(amount, payoff=True)
                else:
                    loan.process_payment(amount)
                messages.success(
                    request, f"Payment of ${amount} successfully processed"
                )
                return redirect("loan:loan", id=id)
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = LoanPaymentForm(
            loan=loan,
            next_payment_amount=next_payment_amount,
            payoff_amount=payoff_total,
        )

    context = {
        "loan": loan,
        "form": form,
        "payment_history": payment_history,
        "payoff_amount": {
            "interest": payoff_interest,
            "principal": payoff_principal,
            "total": payoff_total,
        },
        "next_payment_amount": next_payment_amount,
        "repayment_schedule": repayment_schedule,
        "total_paid": {
            "interest": running_interest,
            "principal": running_principal,
            "total": running_total,
        },
    }
    return render(request, template, context)
