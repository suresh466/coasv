from decimal import Decimal

from django.shortcuts import render

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


def generate_tables(accounts):
    tables = []
    for account in accounts:
        table = {
                'name': account.name, 'code': account.code,
                'rows': generate_rows(account.split_set.all()),
                'balances': account.current_balance(),
        }
        tables.append(table)
    return tables


def general_ledger(request):
    template = 'ledgers/general_ledger.html'

    accounts = ImpersonalAccount.objects.all()
    tables = generate_tables(accounts)

    context = {
            'tables': tables,
    }
    return render(request, template, context)
