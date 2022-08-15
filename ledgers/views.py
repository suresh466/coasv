from django.shortcuts import render, redirect, reverse

from coasc.models import ImpersonalAccount

from ledgers.utils import (
        generate_table, generate_parent_headers,
        generate_parent_footers, get_parent_txs,
        generate_parent_rows, generate_grand_column)


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


def purchase_ledger(request):
    template = 'ledgers/purchase_ledger.html'
    try:
        parent = ImpersonalAccount.objects.get(code=150)
    except ImpersonalAccount.DoesNotExist:
        # Later do something that makes sense
        return redirect(reverse('ledgers:general_ledger'))

    headers = generate_parent_headers(parent)
    footers = generate_parent_footers(parent)
    txs = get_parent_txs(parent)
    rows = generate_parent_rows(txs, parent)
    grand_col = generate_grand_column(rows)
    parent_total = parent.current_balance()

    total_col = []
    col_data = 0
    for data in grand_col:
        col_data += data['total_dr_sum']
        total_col.append(col_data)

    loaded_rows = zip(txs,  rows, total_col)
    table = {
            'headers': headers,
            'footers': footers,
            'loaded_rows': loaded_rows,
            'parent_total': parent_total}

    context = {
            'table': table,
    }
    return render(request, template, context)


def sales_ledger(request):
    template = 'ledgers/sales_ledger.html'
    try:
        parent = ImpersonalAccount.objects.get(code=160)
    except ImpersonalAccount.DoesNotExist:
        # Later do something that makes sense
        return redirect(reverse('ledgers:general_ledger'))

    headers = generate_parent_headers(parent)
    footers = generate_parent_footers(parent)
    txs = get_parent_txs(parent)
    rows = generate_parent_rows(txs, parent)
    grand_col = generate_grand_column(rows)
    parent_total = parent.current_balance()

    total_col = []
    col_data = 0
    for data in grand_col:
        col_data += data['total_cr_sum']
        total_col.append(col_data)

    loaded_rows = zip(txs,  rows, total_col)
    table = {
            'headers': headers,
            'footers': footers,
            'loaded_rows': loaded_rows,
            'parent_total': parent_total}

    context = {
            'table': table,
    }
    return render(request, template, context)
