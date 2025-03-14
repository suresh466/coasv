from django.shortcuts import render

from fstatements.forms import DateFilterForm
from fstatements.utils import (
    generate_balance_sheet,
    generate_income_statement,
    generate_trial_balance,
)


def trial_balance(request):
    template = "fs/trial_balance.html"

    date_filter_form = DateFilterForm(request.GET or None)

    if date_filter_form.is_valid():
        start_date = date_filter_form.cleaned_data.get("start_date")
        end_date = date_filter_form.cleaned_data.get("end_date")

        trial_balance_data = generate_trial_balance(start_date, end_date)
    else:
        trial_balance_data = generate_trial_balance()

    context = {
        "trial_balance": trial_balance_data,
        "form": date_filter_form,
    }

    return render(request, template, context)


def balance_sheet(request):
    template = "fs/balance_sheet.html"

    date_filter_form = DateFilterForm(request.GET or None)

    if date_filter_form.is_valid():
        start_date = date_filter_form.cleaned_data.get("start_date")
        end_date = date_filter_form.cleaned_data.get("end_date")

        balance_sheet_data = generate_balance_sheet(start_date, end_date)
    else:
        balance_sheet_data = generate_balance_sheet()

    context = {
        "balance_sheet": balance_sheet_data,
        "form": date_filter_form,
    }
    return render(request, template, context)


def income_statement(request):
    template = "fs/income_statement.html"

    date_filter_form = DateFilterForm(request.GET or None)

    if date_filter_form.is_valid():
        start_date = date_filter_form.cleaned_data.get("start_date")
        end_date = date_filter_form.cleaned_data.get("end_date")

        income_statement_data = generate_income_statement(start_date, end_date)
    else:
        income_statement_data = generate_income_statement()

    context = {
        "income_statement": income_statement_data,
        "form": date_filter_form,
    }

    return render(request, template, context)
