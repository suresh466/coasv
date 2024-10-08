from datetime import timedelta

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
    payment_history = []
    for ip in interest_payments:
        upper_bound = ip.payment_date + timedelta(seconds=2)
        pp = principal_payments.filter(
            payment_date__gte=ip.payment_date, payment_date__lt=upper_bound
        ).first()
        if pp:
            payment_history.append(
                {
                    "date": ip.payment_date,
                    "interest": ip.amount,
                    "principal": pp.amount,
                    "total": ip.amount + pp.amount,
                }
            )
        else:
            payment_history.append(
                {
                    "date": ip.payment_date,
                    "interest": ip.amount,
                    "principal": 0,
                    "total": ip.amount,
                }
            )

    payment_history_sums = {
        "interest": sum([x["interest"] for x in payment_history]),
        "principal": sum([x["principal"] for x in payment_history]),
        "total": sum([x["total"] for x in payment_history]),
    }
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
        "payment_history_sums": payment_history_sums,
    }
    return render(request, template, context)
