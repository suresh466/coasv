from coasc.models import Transaction, Split


def generate_rows(splits):
    if not splits:
        return []

    rows = []
    difference = 0
    for split in splits:
        if split.type_split == 'dr':
            difference += split.amount
            row = {
                    'debit': split.amount, 'credit': 0,
                    'difference': difference,
                    'description': split.transaction.description}
        else:
            difference -= split.amount
            row = {'debit': 0, 'credit': split.amount,
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


def generate_simple_headers(acs):
    headers = []
    for ac in acs:
        header = f'{ac.name}-{ac.code}'
        headers.append(header)

    return headers


def generate_parent_headers(parent):
    headers = []
    for child in parent.impersonalaccount_set.all():
        header = f'{child.name}-{child.code}'
        headers.append(header)

    return headers


def generate_simple_footers(acs):
    footers = []
    for ac in acs:
        footer = ac.current_balance()
        footers.append(footer)

    return footers


def generate_parent_footers(parent):
    footers = []
    for child in parent.impersonalaccount_set.all():
        footer = child.current_balance()
        footers.append(footer)

    return footers


def get_simple_txs(acs):
    txs = set()
    for ac in acs:
        ac_is = ac.who_am_i()
        if ac_is['parent']:
            ac_txs = get_parent_txs(ac)
            txs.update(ac_txs)
            continue
        ac_txs = set(Transaction.objects.filter(split__account=ac))
        txs.update(ac_txs)

    txs = sorted(txs, key=lambda tx: tx.pk)
    return txs


def get_parent_txs(parent):
    txs = set(Transaction.objects.filter(split__account__parent_ac=parent))
    txs = sorted(txs, key=lambda tx: tx.pk)

    return txs


def generate_simple_rows(txs, acs):
    rows = []
    for tx in txs:
        row = []
        for ac in acs:
            row_data = {'dr_sum': 0, 'cr_sum': 0, 'diff': 0}

            ac_is = ac.who_am_i()
            if ac_is['parent']:
                sps = Split.objects.filter(account__parent_ac=ac)
            else:
                sps = Split.objects.filter(account=ac)
            for sp in sps:
                if sp.transaction == tx:
                    if sp.type_split == 'dr':
                        row_data['dr_sum'] += sp.amount
                        row_data['diff'] += sp.amount
                    else:
                        row_data['cr_sum'] += sp.amount
                        row_data['diff'] -= sp.amount
            row.append(row_data)
        rows.append(row)

    return rows


def generate_parent_rows(txs, parent):
    rows = []
    for tx in txs:
        row = []
        for child in parent.impersonalaccount_set.all():
            row_data = {'dr_sum': 0, 'cr_sum': 0, 'diff': 0}
            for sp in child.split_set.all():
                if sp.transaction == tx:
                    if sp.type_split == 'dr':
                        row_data['dr_sum'] += sp.amount
                        row_data['diff'] += sp.amount
                    else:
                        row_data['cr_sum'] += sp.amount
                        row_data['diff'] -= sp.amount
            row.append(row_data)
        rows.append(row)

    return rows


def load_rows_bal(rows):
    cols = list(zip(*rows))

    for col in cols:
        bal = 0
        for data in col:
            bal += data['diff']
            data['bal'] = bal

    rows = zip(*cols)
    return rows


def generate_grand_total(bal_loaded_rows):
    grand_total = []
    for row in bal_loaded_rows:
        bals = [data['bal'] for data in row]
        grand_total.append(sum(bals))

    return grand_total
