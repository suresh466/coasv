from django.shortcuts import render, redirect, reverse

from coasc.models import ImpersonalAccount

from ledgers.utils import (
        generate_table, generate_parent_headers,
        generate_parent_footers, get_parent_txs,
        generate_parent_rows)
from ledgers.utils import (
        generate_simple_headers, generate_simple_footers,
        get_simple_txs, generate_simple_rows,
        load_rows_bal, generate_grand_total)


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
    parent_total = parent.current_balance()

    total_col = []
    total = 0
    for row in rows:
        for data in row:
            total += data['dr_sum']
        total_col.append(total)

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
    parent_total = parent.current_balance()

    total_col = []
    total = 0
    for row in rows:
        for data in row:
            total += data['cr_sum']
        total_col.append(total)

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


def assets_ledger(request):
    template = 'ledgers/assets_ledger.html'
    acs = ImpersonalAccount.objects.filter(type_ac='AS')
    if not acs:
        # Later do something that makes sense
        return redirect(reverse('ledgers:general_ledger'))

    headers = generate_simple_headers(acs)
    footers = generate_simple_footers(acs)
    txs = get_simple_txs(acs)
    rows = generate_simple_rows(txs, acs)
    bal_loaded_rows = load_rows_bal(rows)
    grand_total = generate_grand_total(bal_loaded_rows)

    loaded_rows = list(zip(txs, rows, grand_total))
    total = ImpersonalAccount.total_current_balance(type_ac='AS')

    table = {
            'headers': headers,
            'footers': footers,
            'loaded_rows': loaded_rows,
            'total': total,
    }
    context = {
            'table': table,
    }
    return render(request, template, context)


def liabilities_ledger(request):
    template = 'ledgers/liabilities_ledger.html'
    acs = ImpersonalAccount.objects.filter(type_ac='LI')
    if not acs:
        # Later do something that makes sense
        return redirect(reverse('ledgers:general_ledger'))

    headers = generate_simple_headers(acs)
    footers = generate_simple_footers(acs)
    txs = get_simple_txs(acs)
    rows = generate_simple_rows(txs, acs)
    bal_loaded_rows = load_rows_bal(rows)
    grand_total = generate_grand_total(bal_loaded_rows)

    loaded_rows = list(zip(txs, rows, grand_total))
    total = ImpersonalAccount.total_current_balance(type_ac='LI')

    table = {
            'headers': headers,
            'footers': footers,
            'loaded_rows': loaded_rows,
            'total': total,
    }
    context = {
            'table': table,
    }
    return render(request, template, context)
