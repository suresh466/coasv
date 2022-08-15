from coasc.models import Transaction


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
            row_data = {'dr_sum': 0, 'cr_sum': 0, 'bal': 0}
            for sp in ac.split_set.all():
                if sp.transaction == tx:
                    if sp.type_split == 'dr':
                        row_data['dr_sum'] += sp.amount
                        row_data['bal'] += sp.amount
                    else:
                        row_data['cr_sum'] += sp.amount
                        row_data['bal'] -= sp.amount
            row.append(row_data)
        rows.append(row)

    return rows


def generate_parent_rows(txs, parent):
    rows = []
    for tx in txs:
        row = []
        for child in parent.impersonalaccount_set.all():
            row_data = {'dr_sum': 0, 'cr_sum': 0, 'bal': 0}
            for sp in child.split_set.all():
                if sp.transaction == tx:
                    if sp.type_split == 'dr':
                        row_data['dr_sum'] += sp.amount
                        row_data['bal'] += sp.amount
                    else:
                        row_data['cr_sum'] += sp.amount
                        row_data['bal'] -= sp.amount
            row.append(row_data)
        rows.append(row)

    return rows


def generate_grand_column(rows):
    column = []
    for row in rows:
        column_data = {'total_dr_sum': 0, 'total_cr_sum': 0, 'total_bal': 0}
        for row_data in row:
            column_data['total_dr_sum'] += row_data['dr_sum']
            column_data['total_cr_sum'] += row_data['cr_sum']
            column_data['total_bal'] += row_data['bal']
        column.append(column_data)

    return column


def generate_simple_table(acs):
    headers = generate_simple_headers(acs)
    footers = generate_simple_footers(acs)
    txs = get_simple_txs(acs)
    rows = generate_simple_rows(txs, acs)
    grand_col = generate_grand_column(rows)

    table = {
            'headers': headers,
            'footers': footers,
            'txs': txs,
            'rows': rows,
            'grand_col': grand_col,
    }
    return table


def generate_parent_table(parent):
    headers = generate_parent_headers(parent)
    footers = generate_parent_footers(parent)
    txs = get_parent_txs(parent)
    rows = generate_parent_rows(txs, parent)
    grand_col = generate_grand_column(rows)

    table = {
            'headers': headers,
            'footers': footers,
            'txs': txs,
            'rows': rows,
            'grand_col': grand_col,
    }
    return table
