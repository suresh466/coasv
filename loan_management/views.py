from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import LoanDisbursementForm, LoanPaymentForm
from .models import InterestPayment, Loan, PrincipalPayment

# Create your views here.


def loans(request):
    loans = Loan.objects.all()
    template = "loan_management/loans.html"
    context = {"loans": loans}
    return render(request, template, context)


def loan(request, id):
    loan = Loan.objects.get(id=id)
    if loan.status == Loan.ACTIVE:
        return active_loan(request, loan)
    elif loan.status in (Loan.FULLYPAID, Loan.DEFAULTED):
        return closed_loan(request, loan)
    elif loan.status in (Loan.PENDING, Loan.APPROVED):
        return disburse_loan(request, id)
    else:
        messages.error(request, "Loan status not recognized")
        return redirect("loan:loans")


def active_loan(request, loan):
    template = "loan_management/loan.html"

    # Calculate necessary amounts
    payoff_interest, payoff_principal, payoff_total, _ = (
        loan.calculate_next_payment_amount(payoff=True)
    )
    _, _, next_payment_amount, _ = loan.calculate_next_payment_amount()
    # Generate repayment schedule
    repayment_schedule = loan.generate_amortization_schedule()

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

    form = LoanPaymentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        payment_type = form.cleaned_data["payment_type"]

        if payment_type == "payoff":
            amount = payoff_total
            is_payoff = True
        elif payment_type == "regular":
            amount = next_payment_amount
            is_payoff = False
        else:
            amount = form.cleaned_data["amount"]
            is_payoff = False

        try:
            loan.process_payment(amount, payoff=is_payoff)
            messages.success(request, f"Payment of ${amount} successfully processed")
            return redirect("loan:loan", id=loan.id)
        except Exception as e:
            print(e)
            messages.error(request, str(e))
            raise e

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
        "pending_disbursement": loan.amount - loan.disbursed_amount,
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


def disburse_loan(request, id):
    template = "loan_management/pending_loan.html"
    loan = Loan.objects.get(id=id)
    pending_disbursement = loan.amount - loan.disbursed_amount

    form = LoanDisbursementForm(request.POST or None)
    if request.method == "POST":
        if loan.status == Loan.PENDING:
            messages.warning(request, "Loan is still pending approval, cannot disburse")
            return redirect("loan:loan", id=loan.id)

        if form.is_valid():
            amount = form.cleaned_data["amount"]
            if amount > pending_disbursement:
                messages.warning(request, "Cannot disburse more than loan amount")
                return redirect("loan:loan", id=loan.id)

            loan.disburse(amount)
            messages.success(
                request, f"Loan disbursement of ${amount} successfully processed"
            )
            return redirect("loan:loan", id=loan.id)

    context = {
        "loan": loan,
        "pending_disbursement": pending_disbursement,
        "form": form,
    }
    return render(request, template, context)
