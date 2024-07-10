from django.shortcuts import render

from fstatements.forms import DateFilterForm
from fstatements.utils import (
    calculate_balance_sheet,
    calculate_income_statement,
    calculate_trial_balance,
)


def trial_balance(request):
    template = "fs/trial_balance.html"

    date_filter_form = DateFilterForm(request.GET or None)

    if date_filter_form.is_valid():
        start_date = date_filter_form.cleaned_data.get("start_date")
        end_date = date_filter_form.cleaned_data.get("end_date")

        cr_acs_with_bal, dr_acs_with_bal, total_sum = calculate_trial_balance(
            start_date, end_date
        )
    else:
        cr_acs_with_bal, dr_acs_with_bal, total_sum = calculate_trial_balance()

    context = {
        "cr_acs": cr_acs_with_bal,
        "dr_acs": dr_acs_with_bal,
        "total_sum": total_sum,
        "form": date_filter_form,
    }

    return render(request, template, context)


def balance_sheet(request):
    template = "fs/balance_sheet.html"

    date_filter_form = DateFilterForm(request.GET or None)

    if date_filter_form.is_valid():
        start_date = date_filter_form.cleaned_data.get("start_date")
        end_date = date_filter_form.cleaned_data.get("end_date")

        as_acs_with_bal, li_acs_with_bal, as_total_bal, li_total_bal = (
            calculate_balance_sheet(start_date, end_date)
        )
    else:
        as_acs_with_bal, li_acs_with_bal, as_total_bal, li_total_bal = (
            calculate_balance_sheet()
        )

    context = {
        "li_acs": li_acs_with_bal,
        "as_acs": as_acs_with_bal,
        "li_total_bal": li_total_bal,
        "as_total_bal": as_total_bal,
        "form": date_filter_form,
    }
    return render(request, template, context)


def income_statement(request):
    template = "fs/income_statement.html"

    date_filter_form = DateFilterForm(request.GET or None)

    if date_filter_form.is_valid():
        start_date = date_filter_form.cleaned_data.get("start_date")
        end_date = date_filter_form.cleaned_data.get("end_date")

        ex_ac_with_bal, in_ac_with_bal = calculate_income_statement(
            start_date, end_date
        )
    else:
        ex_ac_with_bal, in_ac_with_bal = calculate_income_statement()

    context = {
        "ex_ac": ex_ac_with_bal,
        "in_ac": in_ac_with_bal,
        "form": date_filter_form,
    }

    return render(request, template, context)
