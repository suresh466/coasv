from decimal import Decimal

from django.shortcuts import render, redirect, reverse

from coasc.models import ImpersonalAccount


def general_ledger(request):
    template = 'ledgers/general_ledger.html'

    tables = []
    for account in ImpersonalAccount.objects.all():
        if account.who_am_i()['parent']:
            continue
        table = generate_table(account)
        tables.append(table)

    context = {
            'tables': tables,
    }
    return render(request, template, context)


def ledger(request, code=None):
    template = 'ledgers/ledger.html'
    if code is None:
        return redirect(reverse('ledgers:general_ledger'))
    try:
        account = ImpersonalAccount.objects.get(code=code)
    except ImpersonalAccount.DoesNotExist:
        return redirect(reverse('ledgers:general_ledger'))

    table = generate_table(account)
    context = {
            'table': table,
    }
    return render(request, template, context)
