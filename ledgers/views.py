from coasc.models import Ac, Split
from django.db.models import Prefetch, Q
from django.http import Http404
from django.shortcuts import render

from ledgers.utils import (
    generate_parent_footers,
    generate_parent_headers,
    generate_parent_rows,
    generate_table,
    get_parent_txs,
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

    # get expense accounts with balances (parent and child)
    accounts_balances = Ac.get_hierarchical_balances("EX")

    # get all expenses child accounts (it is specific to the predefined accounts hierarchy in scripts/insert-accounts.py)
    splits = Split.objects.select_related("tx")
    operating_accounts = Ac.objects.filter(p_ac__cat="EX").prefetch_related(
        Prefetch("split_set", queryset=splits, to_attr="prefetched_splits")
    )
    running_balances = {account.id: 0 for account in operating_accounts}

    # get all involved transactions
    transactions = set()
    for account in operating_accounts:
        transactions.update(s.tx for s in account.prefetched_splits)
    transactions = sorted(transactions, key=lambda tx: tx.id)

    # prepare rows for the ledger
    rows = []
    for transaction in transactions:
        row = {"description": transaction.desc, "accounts_data": [], "grand_total": 0}
        for account in operating_accounts:
            splits = [s for s in account.prefetched_splits if s.tx == transaction]
            debit = sum(s.am for s in splits if s.t_sp == "dr")
            credit = sum(s.am for s in splits if s.t_sp == "cr")
            net_balance = debit - credit
            running_balances[account.id] += net_balance
            row["accounts_data"].append(
                {
                    "net_balance": net_balance,
                    "running_balance": running_balances[account.id],
                }
            )
            row["grand_total"] += running_balances[account.id]
        rows.append(row)

    context = {"accounts_balances": accounts_balances, "rows": rows}

    return render(request, template, context)


def sales_ledger(request):
    template = "ledgers/sales_ledger.html"

    # get income accounts with balances (parent and child)
    accounts_balances = Ac.get_hierarchical_balances("IN")

    # get all income child accounts (it is specific to the predefined accounts hierarchy in scripts/insert-accounts.py)
    splits = Split.objects.select_related("tx")
    operating_accounts = Ac.objects.filter(p_ac__cat="IN").prefetch_related(
        Prefetch("split_set", queryset=splits, to_attr="prefetched_splits")
    )
    running_balances = {account.id: 0 for account in operating_accounts}

    # get all involved transactions
    transactions = set()
    for account in operating_accounts:
        transactions.update(s.tx for s in account.prefetched_splits)
    transactions = sorted(transactions, key=lambda tx: tx.id)

    # prepare rows for the ledger
    rows = []
    for transaction in transactions:
        row = {"description": transaction.desc, "accounts_data": [], "grand_total": 0}
        for account in operating_accounts:
            splits = [s for s in account.prefetched_splits if s.tx == transaction]
            debit = sum(s.am for s in splits if s.t_sp == "dr")
            credit = sum(s.am for s in splits if s.t_sp == "cr")
            net_balance = credit - debit
            running_balances[account.id] += net_balance
            row["accounts_data"].append(
                {
                    "net_balance": net_balance,
                    "running_balance": running_balances[account.id],
                }
            )
            row["grand_total"] += running_balances[account.id]
        rows.append(row)

    context = {"accounts_balances": accounts_balances, "rows": rows}

    return render(request, template, context)


def assets_ledger(request):
    template = "ledgers/assets_ledger.html"

    # last row of transaction and footer balances are the same if everything is correct
    # calling on get_flat_balances to get the balances is redundant and for tallying purposes
    assets_account_balances = Ac.get_flat_balances("AS")
    footer_grand_total = sum(
        assets_account["balance"]["net_balance"]
        for assets_account in assets_account_balances
    )
    running_balances = {
        account_bals["account"].id: 0 for account_bals in assets_account_balances
    }

    # fetch all assets accounts with prefetched splits for reduced database hits
    splits = Split.objects.select_related("tx")
    operating_accounts = Ac.objects.filter(
        Q(cat="AS") | Q(p_ac__cat="AS")
    ).prefetch_related(
        Prefetch("split_set", queryset=splits, to_attr="prefetched_splits")
    )
    # get top level accounts for top level view of the ledger (no child acs)
    top_level_accounts = [ac for ac in operating_accounts if not ac.is_child]

    # list all the involved transactions
    transactions = set()
    for account in operating_accounts:
        transactions.update(split.tx for split in account.prefetched_splits)

    # prepare the rows for the ledger
    rows = []
    for transaction in transactions:
        row = {"description": transaction.desc, "accounts_data": [], "grand_total": 0}
        for account in top_level_accounts:
            if account.is_parent:
                child_accounts = [ac for ac in operating_accounts if ac.p_ac == account]
                splits = []
                for ca in child_accounts:
                    child_splits = [
                        s for s in ca.prefetched_splits if s.tx == transaction
                    ]
                    splits.extend(child_splits)
            elif account.is_standalone:
                splits = [s for s in account.prefetched_splits if s.tx == transaction]

            debit = sum(split.am for split in splits if split.t_sp == "dr")
            credit = sum(split.am for split in splits if split.t_sp == "cr")
            net_balance = debit - credit
            running_balances[account.id] += net_balance
            row["accounts_data"].append(
                {
                    "debit": debit,
                    "credit": credit,
                    "running_balance": running_balances[account.id],
                }
            )
            row["grand_total"] += running_balances[account.id]
        rows.append(row)

    context = {
        "ledger_data": assets_account_balances,
        "rows": rows,
        "footer_grand_total": footer_grand_total,
    }

    return render(request, template, context)


def liabilities_ledger(request):
    template = "ledgers/liabilities_ledger.html"

    # last row of transaction and footer balances are the same if everything is correct
    # calling on get_flat_balances to get the balances is redundant and for tallying purposes
    accounts_balances = Ac.get_flat_balances("LI")
    footer_grand_total = sum(
        liabilities_account["balance"]["net_balance"]
        for liabilities_account in accounts_balances
    )
    running_balances = {
        account_bals["account"].id: 0 for account_bals in accounts_balances
    }

    # fetch all assets accounts with prefetched splits for reduced database hits
    splits = Split.objects.select_related("tx")
    operating_accounts = Ac.objects.filter(
        Q(cat="LI") | Q(p_ac__cat="LI")
    ).prefetch_related(
        Prefetch("split_set", queryset=splits, to_attr="prefetched_splits")
    )
    # get top level accounts for top level view of the ledger (no child acs)
    top_level_accounts = [ac for ac in operating_accounts if not ac.is_child]

    # list all the involved transactions
    transactions = set()
    for account in operating_accounts:
        transactions.update(split.tx for split in account.prefetched_splits)

    # prepare the rows for the ledger
    rows = []
    for transaction in transactions:
        row = {"description": transaction.desc, "accounts_data": [], "grand_total": 0}
        for account in top_level_accounts:
            if account.is_parent:
                child_accounts = [ac for ac in operating_accounts if ac.p_ac == account]
                splits = []
                for ca in child_accounts:
                    child_splits = [
                        s for s in ca.prefetched_splits if s.tx == transaction
                    ]
                    splits.extend(child_splits)
            elif account.is_standalone:
                splits = [s for s in account.prefetched_splits if s.tx == transaction]

            debit = sum(split.am for split in splits if split.t_sp == "dr")
            credit = sum(split.am for split in splits if split.t_sp == "cr")
            net_balance = credit - debit
            running_balances[account.id] += net_balance
            row["accounts_data"].append(
                {
                    "debit": debit,
                    "credit": credit,
                    "running_balance": running_balances[account.id],
                }
            )
            row["grand_total"] += running_balances[account.id]
        rows.append(row)

    context = {
        "accounts_balances": accounts_balances,
        "rows": rows,
        "footer_grand_total": footer_grand_total,
    }

    return render(request, template, context)
