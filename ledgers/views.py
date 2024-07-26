from coasc.models import Ac, Split
from django.db.models import Prefetch, Q
from django.http import Http404
from django.shortcuts import render

from ledgers.utils import (
    generate_grand_total,
    generate_parent_footers,
    generate_parent_headers,
    generate_parent_rows,
    generate_simple_footers,
    generate_simple_headers,
    generate_simple_rows,
    generate_table,
    get_parent_txs,
    get_simple_txs,
    load_rows_bal,
)


def general_ledger(request):
    template = "ledgers/general_ledger.html"

    # get all the accounts and related splits and transactions in two database hits
    operating_accounts = Ac.objects.filter(~Q(ac__isnull=False)).order_by("code")
    # prefetch related splits and transactions; TODO: order by tx_date or id?
    splits = Split.objects.select_related("tx").order_by("tx__id")

    operating_accounts = operating_accounts.prefetch_related(
        Prefetch("split_set", queryset=splits, to_attr="prefetched_splits")
    )

    ledger_data = []
    for account in operating_accounts:
        transactions_data = []
        running_balance = 0

        # group splits by transaction
        splits_by_tx = {}
        for split in account.prefetched_splits:
            if split.tx_id not in splits_by_tx:
                splits_by_tx[split.tx_id] = []
            splits_by_tx[split.tx_id].append(split)

        for tx_id, tx_splits in splits_by_tx.items():
            debit = sum(s.am for s in tx_splits if s.t_sp == "dr")
            credit = sum(s.am for s in tx_splits if s.t_sp == "cr")

            # Update running balance based on account category
            cat = account.p_ac.cat if account.is_child else account.cat
            if cat in [Ac.ASSET, Ac.EXPENSES]:
                running_balance += debit - credit
            elif cat in [Ac.LIABILITY, Ac.INCOME]:
                running_balance += credit - debit

            transaction_data = {
                "date": tx_splits[0].tx.tx_date,
                "description": tx_splits[0].tx.desc,
                "debit": debit,
                "credit": credit,
                "running_balance": running_balance,
            }
            transactions_data.append(transaction_data)

        data = {
            "account": account,
            "transactions": transactions_data,
            "balance": account.bal(),
        }
        ledger_data.append(data)

    context = {"operating_accounts": ledger_data}

    return render(request, template, context)


def ledger(request, code):
    template = "ledgers/ledger.html"

    try:
        account = Ac.objects.get(code=code)
    except Ac.DoesNotExist:
        raise Http404("Account does not exist")

    table = generate_table(account)

    context = {
        "table": table,
    }
    return render(request, template, context)


def purchase_ledger(request):
    template = "ledgers/purchase_ledger.html"

    # parent = Ac.objects.get(code=150)
    parent = Ac.objects.get(cat="EX")

    headers = generate_parent_headers(parent)
    footers = generate_parent_footers(parent)

    txs = get_parent_txs(parent)
    rows = generate_parent_rows(txs, parent)
    parent_total = parent.bal()

    total_col = []
    total = 0
    for row in rows:
        for data in row:
            total += data["dr_sum"]

        total_col.append(total)

    loaded_rows = zip(txs, rows, total_col)

    table = {
        "headers": headers,
        "footers": footers,
        "loaded_rows": loaded_rows,
        "parent_total": parent_total,
    }

    context = {
        "table": table,
    }

    return render(request, template, context)


def sales_ledger(request):
    template = "ledgers/sales_ledger.html"

    # parent = Ac.objects.get(code="150")
    parent = Ac.objects.get(cat="IN")

    headers = generate_parent_headers(parent)
    footers = generate_parent_footers(parent)

    txs = get_parent_txs(parent)
    rows = generate_parent_rows(txs, parent)
    parent_total = parent.bal()

    total_col = []
    total = 0
    for row in rows:
        for data in row:
            total += data["cr_sum"]

        total_col.append(total)

    loaded_rows = zip(txs, rows, total_col)

    table = {
        "headers": headers,
        "footers": footers,
        "loaded_rows": loaded_rows,
        "parent_total": parent_total,
    }

    context = {
        "table": table,
    }

    return render(request, template, context)


def assets_ledger(request):
    template = "ledgers/assets_ledger.html"

    acs = Ac.objects.filter(cat="AS")

    headers = generate_simple_headers(acs)
    footers = generate_simple_footers(acs)

    txs = get_simple_txs(acs)
    rows = generate_simple_rows(txs, acs)
    bal_loaded_rows = load_rows_bal(rows)

    grand_total = generate_grand_total(bal_loaded_rows)
    total = Ac.total_bal(cat="AS")

    loaded_rows = list(zip(txs, rows, grand_total))

    table = {
        "headers": headers,
        "footers": footers,
        "loaded_rows": loaded_rows,
        "total": total,
    }

    context = {
        "table": table,
    }

    return render(request, template, context)


def liabilities_ledger(request):
    template = "ledgers/liabilities_ledger.html"

    acs = Ac.objects.filter(cat="LI")
    headers = generate_simple_headers(acs)
    footers = generate_simple_footers(acs)

    txs = get_simple_txs(acs)
    rows = generate_simple_rows(txs, acs)
    bal_loaded_rows = load_rows_bal(rows)

    grand_total = generate_grand_total(bal_loaded_rows)
    total = Ac.total_bal(cat="LI")

    loaded_rows = list(zip(txs, rows, grand_total))

    table = {
        "headers": headers,
        "footers": footers,
        "loaded_rows": loaded_rows,
        "total": total,
    }

    context = {
        "table": table,
    }

    return render(request, template, context)
