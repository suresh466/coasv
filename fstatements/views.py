from coasc.models import Ac
from django.shortcuts import redirect, render, reverse

from fstatements.utils import (
    calculate_balance_sheet,
    calculate_income_statement,
    calculate_trial_balance,
)


def trial_balance(request):
    template = "fs/trial_balance.html"

    acs = Ac.objects.exclude(cat="")
    if not acs:
        # later do something that makes sense
        return redirect(reverse("ledgers:general_ledger"))

    cr_acs_with_bal, dr_acs_with_bal, total_sum = calculate_trial_balance(acs)

    context = {
        "cr_acs": cr_acs_with_bal,
        "dr_acs": dr_acs_with_bal,
        "total_sum": total_sum,
    }

    return render(request, template, context)


def balance_sheet(request):
    template = "fs/balance_sheet.html"

    as_acs = Ac.objects.filter(cat="AS")
    li_acs = Ac.objects.filter(cat="LI")

    if not li_acs and not as_acs:
        return redirect(reverse("ledgers:general_ledger"))

    as_acs_with_bal, li_acs_with_bal = calculate_balance_sheet(li_acs, as_acs)

    as_total_bal = Ac.total_bal(cat="AS")
    li_total_bal = Ac.total_bal(cat="LI")

    context = {
        "li_acs": li_acs_with_bal,
        "as_acs": as_acs_with_bal,
        "li_total_bal": li_total_bal,
        "as_total_bal": as_total_bal,
    }
    return render(request, template, context)


def income_statement(request):
    template = "fs/income_statement.html"

    try:
        # in_ac = Ac.objects.get(code=160)
        # ex_ac = Ac.objects.get(code=150)
        in_ac = Ac.objects.get(cat="IN")
        ex_ac = Ac.objects.get(cat="EX")
    except Ac.DoesNotExist:
        return redirect(reverse("ledgers:general_ledger"))

    ex_ac_with_bal, in_ac_with_bal = calculate_income_statement(in_ac, ex_ac)

    context = {
        "ex_ac": ex_ac_with_bal,
        "in_ac": in_ac_with_bal,
    }

    return render(request, template, context)
