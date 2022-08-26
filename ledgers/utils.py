from coasc.models import Transaction, Split


def generate_rows(sps):
    if not sps:
        return []

    rows = []
    diff = 0

    for sp in sps:
        if sp.t_sp == 'dr':
            diff += sp.am
            row = {
                    'debit': sp.am, 'credit': 0, 'diff': diff,
                    'desc': sp.tx.desc}
        else:
            diff -= sp.am
            row = {'debit': 0, 'credit': sp.am, 'diff': diff,
                   'desc': sp.tx.desc}

        rows.append(row)

    return rows


def generate_table(ac):
    table = {
            'name': ac.name, 'code': ac.code,
            'rows': generate_rows(ac.split_set.all()), 'bals': ac.bal(),
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

    for child in parent.impersonalac_set.all():
        header = f'{child.name}-{child.code}'
        headers.append(header)

    return headers


def generate_simple_footers(acs):
    footers = []

    for ac in acs:
        footer = ac.bal()
        footers.append(footer)

    return footers


def generate_parent_footers(parent):
    footers = []

    for child in parent.impersonalac_set.all():
        footer = child.bal()
        footers.append(footer)

    return footers


def get_simple_txs(acs):
    txs = set()

    for ac in acs:
        ac_is = ac.who_am_i()

        if ac_is['parent']:
            ac_txs = get_parent_txs(ac)
            txs.update(ac_txs)
        else:
            ac_txs = set(Transaction.objects.filter(split__ac=ac))
            txs.update(ac_txs)

    txs = sorted(txs, key=lambda tx: tx.pk)

    return txs


def get_parent_txs(parent):
    txs = set(Transaction.objects.filter(split__ac__p_ac=parent))
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
                sps = Split.objects.filter(ac__p_ac=ac)
            else:
                sps = Split.objects.filter(ac=ac)

            for sp in sps:
                if sp.tx == tx:

                    if sp.t_sp == 'dr':
                        row_data['dr_sum'] += sp.am
                        row_data['diff'] += sp.am
                    else:
                        row_data['cr_sum'] += sp.am
                        row_data['diff'] -= sp.am

            row.append(row_data)
        rows.append(row)

    return rows


def generate_parent_rows(txs, parent):
    rows = []

    for tx in txs:
        row = []

        for child in parent.impersonalac_set.all():
            row_data = {'dr_sum': 0, 'cr_sum': 0, 'diff': 0}

            for sp in child.split_set.all():
                if sp.tx == tx:

                    if sp.t_sp == 'dr':
                        row_data['dr_sum'] += sp.am
                        row_data['diff'] += sp.am
                    else:
                        row_data['cr_sum'] += sp.am
                        row_data['diff'] -= sp.am

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
