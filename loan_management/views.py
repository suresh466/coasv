from decimal import Decimal

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from common.decorators.superuser_required import (
    superuser_required,
)

from .models import BillingCycle, Loan


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
    if loan.status != loan.ACTIVE:
        return redirect("loan:loan", id=id)

    template = "loan_management/payment.html"
    payment_history = loan.generate_payment_history()
    payment_type = request.GET.get("payment_type")

    if loan.is_overdue and payment_type != "overdue":
        # do not display the message on the first load
        if payment_type is not None:
            messages.warning(
                request,
                "Please pay the overdue amounts before proceeding with other payments.",
            )
        return redirect(f"{reverse('loan:payment', args=[id])}?payment_type=overdue")

    calculated_interest = []
    if payment_type is None or payment_type == "interest":
        total, period_start, period_end, days, _ = loan.calculate_interest()
        calculated_interest.append(
            {
                "total": int(total),
                "period_start": period_start,
                "period_end": period_end,
                "days": days,
            }
        )
    elif payment_type == "overdue":
        overdue_cycles = loan.overdue_cycles().order_by("period_start")
        for idx, overdue in enumerate(overdue_cycles):
            calculated_interest.append(
                {
                    "id": overdue.id,
                    "total": overdue.amount,
                    "period_start": overdue.period_start,
                    "period_end": overdue.period_end,
                    "days": (overdue.period_end - overdue.period_start).days + 1,
                    "is_payable": idx == 0,
                }
            )

    context = {
        "calculated_interest": calculated_interest,
        "loan": loan,
        "payment_history": payment_history,
    }

    return render(request, template, context)


@require_POST
@superuser_required
def approve(request, id):
    loan = get_object_or_404(Loan, id=id)
    try:
        loan.approve()
        messages.success(request, f"Loan #{loan.id} successfully approved!")
    except ValueError as e:
        messages.error(request, str(e))
    return redirect("loan:loan", id=id)


@require_POST
@superuser_required
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
    interest_type = request.POST.get("interest-type")

    if interest_type == "custom":
        amount = request.POST.get("amount")
        if amount:
            amount = Decimal(amount)

            _, period_end = loan.calculate_days(amount)
            total, period_start, period_end, _, _ = loan.calculate_interest(
                period_end=period_end
            )
            loan.process_interest(total, period_start, period_end)
    elif interest_type == "overdue":
        overdue_id = request.POST.get("overdue_id")
        fees_included = "fees" in request.POST
        bc = BillingCycle.objects.get(id=overdue_id)
        bc.status = bc.PAID
        if fees_included:
            loan.process_fee(loan.calculate_fee(), bc)
        bc.save()
    else:
        to_date = True if interest_type == "to-date" else False
        total, period_start, period_end, _, _ = loan.calculate_interest(to_date=to_date)
        loan.process_interest(total, period_start, period_end)

    messages.success(request, f"Interest paid for Loan #{loan.id} successfully!")
    return redirect("loan:payment", id=id)


def calculate_interest(request, id):
    loan = get_object_or_404(Loan, id=id)
    interest_type = request.GET.get("interest-type")

    calculated_interest = {}
    if interest_type == "custom":
        input_amount = request.GET.get("amount")
        if input_amount:
            amount = Decimal(input_amount)
            _, period_end = loan.calculate_days(amount)
            total, period_start, period_end, days, leap_year = loan.calculate_interest(
                period_end=period_end
            )

            calculated_interest = {
                "total": int(total),
                "period_start": period_start,
                "period_end": period_end,
                "days": days,
                "leap_year": leap_year,
            }
    else:
        to_date = True if interest_type == "to-date" else False
        total, period_start, period_end, days, leap_year = loan.calculate_interest(
            to_date=to_date
        )
        calculated_interest = {
            "total": int(total),
            "period_start": period_start,
            "period_end": period_end,
            "days": days,
            "leap_year": leap_year,
        }

    return JsonResponse(calculated_interest)


@require_POST
def pay_principal(request, id):
    loan = get_object_or_404(Loan, id=id)

    amount = request.POST.get("principal-amount")
    loan.process_principal(Decimal(amount))

    messages.success(request, f"Principal paid for Loan #{loan.id} successfully!")
    return redirect("loan:payment", id=id)
