from decimal import Decimal

from django.shortcuts import render, redirect, reverse

from coasc.models import ImpersonalAccount

# Create your views here.


def generate_rows(splits):
    if not splits:
        return []

    rows = []
    difference = Decimal(0)
    for split in splits:
        if split.type_split == 'dr':
            difference += split.amount
            row = {
                    'debit': split.amount, 'credit': Decimal(0),
                    'difference': difference,
                    'description': split.transaction.description}
        else:
            difference -= split.amount
            row = {'debit': Decimal(0), 'credit': split.amount,
                   'difference': difference,
                   'description': split.transaction.description}
        rows.append(row)
    return rows


def generate_table(account):
    table = {
            'name': account.name, 'code': account.code,
            'rows': generate_rows(account.split_set.all()),
            'balances': account.current_balance(),
    }
    return table


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
