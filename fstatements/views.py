from django.shortcuts import render

from fstatements.utils import (
    calculate_balance_sheet,
    calculate_income_statement,
    calculate_trial_balance,
)


def trial_balance(request):
    template = "fs/trial_balance.html"

    cr_acs_with_bal, dr_acs_with_bal, total_sum = calculate_trial_balance()

    context = {
        "cr_acs": cr_acs_with_bal,
        "dr_acs": dr_acs_with_bal,
        "total_sum": total_sum,
    }

    return render(request, template, context)


def balance_sheet(request):
    template = "fs/balance_sheet.html"

    as_acs_with_bal, li_acs_with_bal, as_total_bal, li_total_bal = (
        calculate_balance_sheet()
    )

    context = {
        "li_acs": li_acs_with_bal,
        "as_acs": as_acs_with_bal,
        "li_total_bal": li_total_bal,
        "as_total_bal": as_total_bal,
    }
    return render(request, template, context)


def income_statement(request):
    template = "fs/income_statement.html"

    ex_ac_with_bal, in_ac_with_bal = calculate_income_statement()

    context = {
        "ex_ac": ex_ac_with_bal,
        "in_ac": in_ac_with_bal,
    }

    return render(request, template, context)
